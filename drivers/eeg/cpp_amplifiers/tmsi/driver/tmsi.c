/*
 * tmsi.c: USB driver for the TMS International Fiber to USB convertor
 *          used in the Refa8 series of products.
 *
 * Copyright (C) 2008 Clinical Science Systems (http://www.clinicalsciencesystems.com)
 *
 *      This program is free software; you can redistribute it and/or
 *      modify it under the terms of the GNU General Public License as
 *      published by the Free Software Foundation, version 3.
 *
 *          
 * ChangeLog
 * ---------
 * v1.6 - 21-10-2011 Maciej Pawlisz
 *      + Support kernel 3.0
 *      + Sending front_end_info with stop request on release
 *      * Allocating/deallocation urbs moved to open/release
 *       
 * v1.5 - 16-07-2011 Maciej Pawlisz
 *      * Name change to Tmsi driver
 *      * usb_kill_urb instead of usb_unlink_urb in release 
 *      + Support for SynFi device
 *
 *
 * v1.4 - 01-09-2010
 *      + Support for kernel 2.6.32 by Maciej Pawlisz (maciej.pawlisz@gmail.com)
 *
 * v1.3 - 10-03-2008
 *
 *      * Upgraded licence to GPL version 3
 *      * Fixed compiler warnings on usb_fill_bulk_urb calls
 *      + Support for kernel 2.6.24
 *
 *
 * v1.2 - 26-06-2007
 *
 *      + x86_64 architecture IOCTL command added
 *      * unlink_urb instead of kill_urb in callback handlers
 *
 *
 * v1.1 - 05-01-2007
 *
 *      - deprecated headers removed
 */

/* Kernel headers */
#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/module.h>
#include <linux/kref.h>
#include <linux/mutex.h>
#include <asm/uaccess.h>
#include <linux/usb.h>
#include <linux/usb/ch9.h>
#include <linux/kfifo.h>
#include <linux/version.h>
#include <linux/semaphore.h>

/* Driver information */
#define DRIVER_VERSION                  "1.6.1"
#define DRIVER_AUTHOR                  "Paul Koster (Clinical Science Systems), p.koster@mailcss.com; Maciej Pawlisz (maciej.pawlisz@gmail.com)"
#define DRIVER_DESC                  "TMS International USB <-> Fiber Interface Driver for Linux (c) 2005,2010,2011"

/* Define these values to match your devices */
#define USB_TMSI_VENDOR_ID            0x0C7C
#define USB_FUSBI_PRODUCT_ID            0x0004
#define USB_SYNFI_PRODUCT_ID            0x0005


/* IOCTL commands */
#define IOCTL_TMSI_BUFFERSIZE            0x40044601
#define IOCTL_TMSI_BUFFERSIZE_64      0x40084601

/* BLOCK TYPES */
#define TMSI_SYNCHRO                  0xAAAA
#define TMSI_FEI                      0x0210
#define TMSI_ACK                      0x0002
#define TMSI_STOP_REQ                 0x11
#define TMSI_MODE_FIELD               4
#define TMSI_CHECKSUM_FIELD           18

/* Buffer structure */
#define PACKET_BUFFER_SIZE            2097152
#define BULK_RECV_URBS                  50
#define ISOC_RECV_URBS                  50

/* Get a minor range for your devices from the usb maintainer */
#define USB_TMSI_MINOR_BASE            192
#define info(...) printk(KERN_INFO __VA_ARGS__)
#define debug(...) ;
//#define debug(...) printk(KERN_INFO __VA_ARGS__)
/* Structure to hold all of our device specific stuff */

struct tmsi_data {
    struct usb_device* udev;
    struct usb_interface* interface;
    struct kref kref;
    __u8 device_open;

    // Receive buffers
    unsigned char* bulk_recv_buffer[BULK_RECV_URBS];
    unsigned char* isoc_recv_buffer[ISOC_RECV_URBS];

    // Receive URB's
    struct urb* bulk_recv_urb[BULK_RECV_URBS];
    struct urb* isoc_recv_urb[ISOC_RECV_URBS];

    // FIFO buffer
    spinlock_t buffer_lock;
    struct kfifo inner_packet_buffer;
    struct kfifo * packet_buffer;
    struct semaphore * fifo_sem;
    // Endpoints
    struct usb_endpoint_descriptor* bulk_recv_endpoint;
    struct usb_endpoint_descriptor* bulk_send_endpoint;
    struct usb_endpoint_descriptor* isoc_recv_endpoint;

    //StopRequest
    char releasing;
    struct semaphore *release_sem;
    char * fei; // pointer to front_end_info with stop request
    unsigned int fei_size;
};

DEFINE_MUTEX(driver_lock);

static struct usb_driver tmsi_driver;

/*******************************************************************
                     Function prototypes
 *******************************************************************/

// File operations
static int tmsi_open(struct inode *inode, struct file *file);
static int tmsi_release(struct inode *inode, struct file *file);
static int tmsi_release_dev(struct tmsi_data *dev);
static ssize_t tmsi_read(struct file *file, char *buffer, size_t count, loff_t *ppos);
static ssize_t tmsi_write(struct file *file, const char *user_buffer, size_t count, loff_t *ppos);
static ssize_t tmsi_write_data(struct tmsi_data *dev, char *buf, size_t count);
static int tmsi_ioctl(struct inode* inode, struct file* file, unsigned int command, unsigned long argument);

// R/W callback functions
static void tmsi_write_bulk_callback(struct urb *urb, struct pt_regs *regs);
static void tmsi_read_bulk_callback(struct urb *urb, struct pt_regs *regs);
static void tmsi_read_isoc_callback(struct urb *urb, struct pt_regs *regs);

// Deletion function
static void tmsi_delete(struct kref *kref);

/*******************************************************************
            File operations function implementations
 *******************************************************************/

static int tmsi_open(struct inode *inode, struct file *file) {
    struct tmsi_data* dev;
    struct usb_interface* interface;
    int i, subminor,pipe,retval = 0;
    subminor = iminor(inode);
    mutex_lock(&driver_lock);
    interface = usb_find_interface(&tmsi_driver, subminor);
    if (!interface) {
        err("%s - error, can't find device for minor %d", __FUNCTION__, subminor);
        retval = -ENODEV;
        goto exit;
    }

    dev = usb_get_intfdata(interface);
    mutex_unlock(&driver_lock);
    if (!dev) {
        retval = -ENODEV;
        goto exit;
    }

    if (dev->device_open > 0)
        {
        retval=-1;
          goto exit;
      }
    else
        dev->device_open = 1;

    /* increment our usage count for the device */
    kref_get(&dev->kref);

    /* save our object in the file's private structure */
    file->private_data = dev;

    // Setup incoming databuffer
#if LINUX_VERSION_CODE > KERNEL_VERSION(3,0,0)
    spin_lock_init(&dev->buffer_lock);
#else
    dev->buffer_lock = SPIN_LOCK_UNLOCKED;
#endif

#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,32)
    dev->packet_buffer = &dev->inner_packet_buffer;
    kfifo_alloc(dev->packet_buffer, PACKET_BUFFER_SIZE, GFP_KERNEL);
#else
    dev->packet_buffer = kfifo_alloc(PACKET_BUFFER_SIZE, GFP_KERNEL, &dev->buffer_lock);
#endif
    
    // Setup initial bulk receive URB and submit
    pipe=usb_rcvbulkpipe(dev->udev, dev->bulk_recv_endpoint->bEndpointAddress);
    for (i = 0; i < BULK_RECV_URBS; ++i) {
        dev->bulk_recv_urb[i] = usb_alloc_urb(0, GFP_KERNEL);
        dev->bulk_recv_buffer[i] = kmalloc(dev->bulk_recv_endpoint->wMaxPacketSize, GFP_KERNEL);
        usb_fill_bulk_urb(dev->bulk_recv_urb[i], dev->udev, pipe, dev->bulk_recv_buffer[i], dev->bulk_recv_endpoint->wMaxPacketSize, (usb_complete_t) tmsi_read_bulk_callback, dev);
        retval = usb_submit_urb(dev->bulk_recv_urb[i], GFP_KERNEL);
        if (retval)
            err("%s - failed submitting bulk read urb[%d], error %d", __FUNCTION__, i, retval);
    }

    // Setup initial isochronous receive URB's and submit
    pipe=usb_rcvisocpipe(dev->udev, dev->isoc_recv_endpoint->bEndpointAddress);
    for (i = 0; i < ISOC_RECV_URBS; ++i) {
        dev->isoc_recv_urb[i] = usb_alloc_urb(1, GFP_KERNEL);
        dev->isoc_recv_buffer[i] = kmalloc(dev->isoc_recv_endpoint->wMaxPacketSize, GFP_KERNEL);
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,24)
        spin_lock_init(&dev->isoc_recv_urb[i]->lock);
#endif
        dev->isoc_recv_urb[i]->dev = dev->udev;
        dev->isoc_recv_urb[i]->pipe = pipe;
        dev->isoc_recv_urb[i]->transfer_buffer = dev->isoc_recv_buffer[i];
        dev->isoc_recv_urb[i]->transfer_buffer_length = dev->isoc_recv_endpoint->wMaxPacketSize;
        dev->isoc_recv_urb[i]->complete = (usb_complete_t) tmsi_read_isoc_callback;
        dev->isoc_recv_urb[i]->context = dev;
        dev->isoc_recv_urb[i]->interval = 1 << (dev->isoc_recv_endpoint->bInterval - 1);
        dev->isoc_recv_urb[i]->number_of_packets = 1;
        dev->isoc_recv_urb[i]->start_frame = -1;
        dev->isoc_recv_urb[i]->iso_frame_desc[0].offset = 0;
        dev->isoc_recv_urb[i]->iso_frame_desc[0].length = dev->isoc_recv_endpoint->wMaxPacketSize;
        dev->isoc_recv_urb[i]->transfer_flags = URB_ISO_ASAP;

        retval = usb_submit_urb(dev->isoc_recv_urb[i], GFP_KERNEL);
        if (retval)
            err("%s - failed submitting isochronous read urb[%d], error %d", __FUNCTION__, i, retval);
    }
    dev->fifo_sem = kmalloc(sizeof (struct semaphore), GFP_KERNEL);
    sema_init(dev->fifo_sem, 0);
    dev->release_sem = kmalloc(sizeof (struct semaphore), GFP_KERNEL);
    sema_init(dev->release_sem, 0);
    info("Tmsi device open() success");
exit:
    return retval;
}

static int tmsi_release(struct inode *inode, struct file *file) {
    struct tmsi_data* dev;
    int retval = 0;
    info("Tmsi Release\n");
    dev = (struct tmsi_data*) file->private_data;
    if (!dev)
        return -ENODEV;
    dev->releasing = 1;
    if (dev->fei)
    {
      //We have front end info, so just to be sure, we send a stop message      
        info("Sending stop request\n");
        retval = tmsi_write_data(dev, dev->fei, dev->fei_size);
      //We are waiting for stop confirmation, for a while....
        down_timeout(dev->release_sem, HZ);
      //It will be deallocated in write callback
        dev->fei=NULL;
    }
    tmsi_release_dev(dev);
    return retval;
}
void free_urb(struct urb *urb)
{
   usb_kill_urb(urb);
   kfree(urb->transfer_buffer);
   usb_free_urb(urb);
}
static int tmsi_release_dev(struct tmsi_data* dev) {

    int i;
    if (!dev)
        return -ENODEV;
    // Unlink current receiving bulk URB
    for (i = 0; i < BULK_RECV_URBS; ++i)
      free_urb(dev->bulk_recv_urb[i]);
    // Unlink current receiving isochronous URB's
    for (i = ISOC_RECV_URBS-1; i>=0; --i)
      free_urb(dev->isoc_recv_urb[i]);

    if (dev->device_open > 0)
        dev->device_open = 0;


    // Remove buffer

    kfifo_reset(dev->packet_buffer);
    kfifo_free(dev->packet_buffer);
    up(dev->fifo_sem);
    kfree(dev->fifo_sem);
    kfree(dev->release_sem);

    /* decrement the count on our device */
    kref_put(&dev->kref, tmsi_delete);

    info("Tmsi device realese() success\n");
    dev->releasing = 0;
    return 0;
}

static ssize_t tmsi_read(struct file *file, char *buffer, size_t count, loff_t *ppos) {
    struct tmsi_data* dev;
    char* temp_buffer = NULL;
    int retval = 0;
    size_t true_count;
    dev = (struct tmsi_data*) file->private_data;
    if (down_timeout(dev->fifo_sem, HZ / 2) != 0)
        return -ETIME;
    while (down_trylock(dev->fifo_sem) == 0);

    temp_buffer = kmalloc(count, GFP_KERNEL);

    if (!temp_buffer) {
        retval = -ENOMEM;
        goto exit;
    }


#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,35)
    true_count = kfifo_out_spinlocked(dev->packet_buffer, temp_buffer, count, &dev->buffer_lock);
#elif LINUX_VERSION_CODE > KERNEL_VERSION(2,6,32)
    true_count = kfifo_out_locked(dev->packet_buffer, temp_buffer, count, &dev->buffer_lock);
#else
    true_count = kfifo_get(dev->packet_buffer, temp_buffer, count);
#endif


    /* if the read was successful, copy the data to userspace */
    if (copy_to_user(buffer, temp_buffer, true_count))
        retval = -EFAULT;
    else
        retval = true_count;

    kfree(temp_buffer);
exit:
    if (kfifo_len(dev->packet_buffer) > 0)
        up(dev->fifo_sem);
    return retval;
}

static ssize_t tmsi_write_data(struct tmsi_data* dev, char * buf, size_t count) {
    struct urb *urb = NULL;
    int retval = 0;
    /* Create an URB */
    urb = usb_alloc_urb(0, GFP_KERNEL);
    if (!urb) {
        retval = -ENOMEM;
        goto error;
    }
    /* Initialize the urb properly */
    usb_fill_bulk_urb(urb, dev->udev, usb_sndbulkpipe(dev->udev, dev->bulk_send_endpoint->bEndpointAddress), 
                      buf, count, (usb_complete_t) tmsi_write_bulk_callback, dev);
    /* Send the data out the bulk port */
    retval = usb_submit_urb(urb, GFP_KERNEL);
    if (retval) {
        err("%s - failed submitting write urb, error %d", __FUNCTION__, retval);
        goto error;
    }  
    /* release our reference to this urb, the USB core will eventually free it entirely */
error:
    usb_free_urb(urb);
    return retval;
}

static ssize_t tmsi_write(struct file *file, const char *user_buffer, size_t count, loff_t *ppos) {
    struct tmsi_data* dev;
    int retval = 0;
    char *buf = NULL;
    unsigned short *packet;
    dev = (struct tmsi_data*) file->private_data;

    /* Verify that we actually have some data to write */
    if (count == 0)
        goto exit;

    /* Create a send buffer */
    buf = kmalloc(count, GFP_KERNEL);
    if (!buf) {
        retval = -ENOMEM;
        goto error;
    }

    /* Copy the data to the urb */
    if (copy_from_user(buf, user_buffer, count)) {
        retval = -EFAULT;
        goto error;
    }
    retval = tmsi_write_data(dev, buf, count);
    packet = (unsigned short *)buf;
    //Storing front end info (FEI) for later use
    if (dev->fei==NULL && count>=38 &&  packet[0]==TMSI_SYNCHRO && packet[1]==TMSI_FEI)
    {
        dev->fei = kmalloc(count, GFP_KERNEL);
        if (dev->fei)
        {
            unsigned short *vals=(unsigned short *)dev->fei;
            dev->fei_size=count;
            memcpy(dev->fei,buf,count);
          //Modifying FEI: stopp request, and checksum
            vals[TMSI_CHECKSUM_FIELD]-=TMSI_STOP_REQ-vals[TMSI_MODE_FIELD];
            vals[TMSI_MODE_FIELD]=TMSI_STOP_REQ;
        }
    }
    if (retval < 0)
        goto error;
exit:
    return count;

error:
    debug("Write: error:%d\n",retval);
    if (buf) kfree(buf);
    return retval;
}

static int tmsi_ioctl(struct inode* inode, struct file* file, unsigned int command, unsigned long argument) {
    struct tmsi_data* dev;
    unsigned long* arg_address = (unsigned long*) argument;

    dev = (struct tmsi_data*) file->private_data;

    switch (command) {
        case IOCTL_TMSI_BUFFERSIZE:
        case IOCTL_TMSI_BUFFERSIZE_64:
        {
            put_user(kfifo_len(dev->packet_buffer), arg_address);
            return 0;
        }
        default:
            info("%s: IOCTL command 0x%X not implemented!", __FUNCTION__, command);
            break;
    }

    return -1;
}

/*******************************************************************
                      R/W callback functions
 *******************************************************************/

static void tmsi_write_bulk_callback(struct urb *urb, struct pt_regs *regs) {
    struct tmsi_data* dev;
    dev = (struct tmsi_data*) urb->context;
    /* sync/async unlink faults aren't errors */
    if (urb->status && !(urb->status == -ENOENT || urb->status == -ECONNRESET || urb->status == -ESHUTDOWN))
        err("%s - nonzero write bulk status received: %d", __FUNCTION__, urb->status);

    /* free up our allocated buffer */
    kfree(urb->transfer_buffer);
}


static void tmsi_enqueue_data(struct tmsi_data *dev, const char * buffer, size_t length)
{
        if (length == 0)
            return;
#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,35)
        kfifo_in_spinlocked(dev->packet_buffer, buffer, length, &dev->buffer_lock);
#elif LINUX_VERSION_CODE > KERNEL_VERSION(2,6,32)
        kfifo_in_locked(dev->packet_buffer, buffer, length, &dev->buffer_lock);
#else 
        kfifo_put(dev->packet_buffer, buffer, length);
#endif
        up(dev->fifo_sem);
}

static void tmsi_read_bulk_callback(struct urb *urb, struct pt_regs *regs) {
    int retval = 0;
    struct tmsi_data* dev;
    if (!(urb->status == -ENOENT || urb->status == -ECONNRESET || urb->status == -ESHUTDOWN)) {
        dev = (struct tmsi_data*) urb->context;
        debug("Read_callback: begin%d\n",urb->status);
        switch (urb->status) {
            case 0:
            {
                // Packet received is OK and cleared the buffer completely
                // Enqueue packet in user buffer
            tmsi_enqueue_data(dev,urb->transfer_buffer,urb->actual_length);

                if (dev->releasing) {
            //We are waiting for ack from amplifier to confirm that sampling is stopped
                    unsigned short *buf = (unsigned short *) urb->transfer_buffer;
                debug("message received while releasing\n");
                    if (urb->actual_length >= 4) {
                        if (buf[0] == TMSI_SYNCHRO && buf[1] == TMSI_ACK)
                            up(dev->release_sem);
                        else
                            debug("buf[0]==%d, buf[1]=%d\n", buf[0], buf[1]);
                    }
                }
                break;
            }

            case -EPIPE:
            {
                // This error occurs when an endpoint has stalled.
                info("%s: The bulk endpoint has stalled. (size = %d)", __FUNCTION__, urb->actual_length);

                break;
            }

            default:
            {
                // Unknown error. Log to syslog
                info("%s: Unknown bulk error occurred (status %d)", __FUNCTION__, urb->status);
                break;
            }
        }

        urb->dev = dev->udev;
        urb->status = 0;

        // Submit the URB
        retval = usb_submit_urb(urb, GFP_ATOMIC);
        if (retval)
            err("%s - failed submitting bulk_recv_urb, error %d", __FUNCTION__, retval);
    }
}

static void tmsi_read_isoc_callback(struct urb *urb, struct pt_regs *regs) {
    int retval = 0,status;
    struct tmsi_data* dev;
    status=urb->status;
    debug("Read isoc callback %x:%d,%d\n",(void *)urb,urb->status,urb->iso_frame_desc[0].status);
    if (!(status == -ENOENT || status == -ECONNRESET || status == -ESHUTDOWN)) {
        dev = (struct tmsi_data*) urb->context;
        switch (status) {
            case 0:
            {
                // Packet received is OK and cleared the buffer completely
                // Enqueue packet in user buffer
            tmsi_enqueue_data(dev,urb->transfer_buffer,urb->iso_frame_desc[0].actual_length);
                break;
            }

            default:
            {
                // Unknown error. Log to syslog
                err("%s: Unknown USB error occurred (status %d)", __FUNCTION__, status);
                break;
            }
        }

        urb->dev = dev->udev;
        urb->status = 0;
        urb->iso_frame_desc[0].status = 0;
        urb->iso_frame_desc[0].actual_length = 0;
        // Submit the URB
      retval = usb_submit_urb(urb, GFP_ATOMIC);
        if (retval)
            err("%s - failed submitting isoc_recv_urb, error %d", __FUNCTION__, retval);
    }
}

/*******************************************************************
          Delete function for freeing our dev structure
 *******************************************************************/

static void tmsi_delete(struct kref *kref) {
    struct tmsi_data* dev = container_of(kref, struct tmsi_data, kref);
    usb_put_dev(dev->udev);
    kfree(dev);
    info("Tmsi device deleted");
}

/*******************************************************************
                  file_operations struct
 *******************************************************************/

static struct file_operations tmsi_fops = {
    .owner = THIS_MODULE,
    .open = tmsi_open,
    .release = tmsi_release,
    .read = tmsi_read,
    .write = tmsi_write,
#if LINUX_VERSION_CODE <= KERNEL_VERSION(2,6,35)
    .ioctl = tmsi_ioctl,
#endif
};

/*******************************************************************
   USB class driver info in order to get a minor number from the
  usb core and to have the device registered with the driver core
 *******************************************************************/

static struct usb_class_driver tmsi_class = {
    .name = "usb/tmsi%d",
    .fops = &tmsi_fops,
    .minor_base = USB_TMSI_MINOR_BASE,
};

static int tmsi_probe(struct usb_interface *interface, const struct usb_device_id *id) {
    struct tmsi_data* dev = NULL;
    struct usb_host_interface* iface_desc;
    struct usb_endpoint_descriptor* endpoint;
    int i;
    int retval = -ENOMEM;

    // Allocate memory for our device state and initialize it
    dev = kmalloc(sizeof (struct tmsi_data), GFP_KERNEL);
    if (dev == NULL) {
        err("Out of memory");
        goto error;
    }
    memset(dev, 0x00, sizeof (*dev));

    // Initialize dev structure
    dev->udev = usb_get_dev(interface_to_usbdev(interface));
    dev->interface = interface;
    kref_init(&dev->kref);

    

    /* Use the alternate interface specified in the tmsi device */
    usb_set_interface(dev->udev, 0, 1);

    /* set up the endpoint information */
    iface_desc = interface->cur_altsetting;

    for (i = 0; i < iface_desc->desc.bNumEndpoints; ++i) {
        endpoint = &iface_desc->endpoint[i].desc;

        /* we found a Bulk IN endpoint */
        if (!dev->bulk_recv_endpoint && (endpoint->bEndpointAddress & USB_DIR_IN) && ((endpoint->bmAttributes & USB_ENDPOINT_XFERTYPE_MASK) == USB_ENDPOINT_XFER_BULK))
            dev->bulk_recv_endpoint = endpoint;


        /* we found a Bulk OUT endpoint */
        if (!dev->bulk_send_endpoint && !(endpoint->bEndpointAddress & USB_DIR_IN) && ((endpoint->bmAttributes & USB_ENDPOINT_XFERTYPE_MASK) == USB_ENDPOINT_XFER_BULK)) {
            dev->bulk_send_endpoint = endpoint;
        }

        /* We found an Isochronous IN endpoint */
        if (!dev->isoc_recv_endpoint && (endpoint->bEndpointAddress & USB_DIR_IN) && ((endpoint->bmAttributes & USB_ENDPOINT_XFERTYPE_MASK) == USB_ENDPOINT_XFER_ISOC))
            dev->isoc_recv_endpoint = endpoint;
    }

    /* Check if all required endpoints are present */
    if (!(dev->bulk_recv_endpoint->bEndpointAddress && dev->bulk_send_endpoint->bEndpointAddress && dev->isoc_recv_endpoint->bEndpointAddress)) {
        err("Could not find the required USB endpoints (bulk in/out, isochronous in)");
        goto error;
    }

    /* Check if device is attached to an USB2 interface */
    if (dev->udev->speed != USB_SPEED_HIGH) {
        err("Device is not attached to an USB2 bus");
        goto error;
    }

    /* save our data pointer in this interface device */
    usb_set_intfdata(interface, dev);

    /* we can register the device now, as it is ready */
    retval = usb_register_dev(interface, &tmsi_class);
    if (retval) {
        /* something prevented us from registering this driver */
        err("Not able to get a minor for this device.");
        usb_set_intfdata(interface, NULL);
        goto error;
    }

    /* let the user know what node this device is now attached to */
      info("%s device (driver version %s) now attached (minor %d)\n", id->idProduct==USB_SYNFI_PRODUCT_ID?"SYNFI":"FUSBI",DRIVER_VERSION, interface->minor);

    return 0;

error:
    if (dev) {
        debug("Kref dec\n");
        kref_put(&dev->kref, tmsi_delete);
    }
    return retval;
}

static void tmsi_disconnect(struct usb_interface *interface) {
    struct tmsi_data *dev;
    int minor = interface->minor;
    info("Disconnecting Tmsi device ...(minor %d)\n", minor);

    /* prevent tmsi_open() from racing tmsi_disconnect() */
    mutex_lock(&driver_lock);

    dev = usb_get_intfdata(interface);
    usb_set_intfdata(interface, NULL);

    usb_deregister_dev(interface, &tmsi_class);

    mutex_unlock(&driver_lock);

    /* decrement our usage count */
    debug("Kref dec\n");
    kref_put(&dev->kref, tmsi_delete);

    info("Tmsi device disconnected\n");
}


static struct usb_device_id tmsi_idtable [] = {
    { USB_DEVICE(USB_TMSI_VENDOR_ID, USB_FUSBI_PRODUCT_ID)},
    { USB_DEVICE(USB_TMSI_VENDOR_ID, USB_SYNFI_PRODUCT_ID)},
    {} /* Terminating entry */
};
MODULE_DEVICE_TABLE(usb, tmsi_idtable);

static struct usb_driver tmsi_driver = {
    .name = "tmsi driver",
    .probe = tmsi_probe,
    .disconnect = tmsi_disconnect,
    .id_table = tmsi_idtable,
};

/*******************************************************************
                         Module entry points
 *******************************************************************/

static int __init usb_tmsi_init(void) {
    int result;
    result = usb_register(&tmsi_driver);
    if (result)
        err("%s: Registration of tmsi driver failed. (error %d)", __FUNCTION__, result);
    return result;
}

static void __exit usb_tmsi_exit(void) {
    usb_deregister(&tmsi_driver);
}


module_init(usb_tmsi_init);
module_exit(usb_tmsi_exit);

MODULE_LICENSE("GPL");
