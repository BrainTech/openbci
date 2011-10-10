/*
 * tmsi.c: USB driver for the TMS International Fiber to USB convertor
 *          used in the Refa8 series of products.
 *
 * Copyright (C) 2008 Clinical Science Systems (http://www.clinicalsciencesystems.com)
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License as
 *	published by the Free Software Foundation, version 3.
 *
 *
 * ChangeLog
 * ---------
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
 *	* Upgraded licence to GPL version 3
 *	* Fixed compiler warnings on usb_fill_bulk_urb calls
 *	+ Support for kernel 2.6.24
 *
 *
 * v1.2 - 26-06-2007
 *
 *	+ x86_64 architecture IOCTL command added
 *	* unlink_urb instead of kill_urb in callback handlers
 *
 *
 * v1.1 - 05-01-2007
 *
 *	- deprecated headers removed
 */

/* Kernel headers */
#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/module.h>
#include <linux/kref.h>
#include <asm/uaccess.h>
#include <linux/usb.h>
#include <linux/usb/ch9.h>
#include <linux/kfifo.h>
#include <linux/version.h>
#include <linux/smp_lock.h>
#include <linux/semaphore.h>

/* Driver information */
#define DRIVER_VERSION			"1.5"
#define DRIVER_AUTHOR			"Paul Koster (Clinical Science Systems), p.koster@mailcss.com; Maciej Pawlisz (maciej.pawlisz@gmail.com)"
#define DRIVER_DESC			"TMS International USB <-> Fiber Interface Driver for Linux (c) 2005"

/* Define these values to match your devices */
#define USB_TMSI_VENDOR_ID		0x0C7C
#define USB_FUSBI_PRODUCT_ID		0x0004
#define USB_SYNFI_PRODUCT_ID		0x0005


/* IOCTL commands */
#define IOCTL_TMSI_BUFFERSIZE		0x40044601
#define IOCTL_TMSI_BUFFERSIZE_64	0x40084601
#define IOCTL_TMSI_SENDSTOP     	0x40084603

/* Buffer structure */
#define PACKET_BUFFER_SIZE		131072
#define BULK_RECV_URBS			100
#define ISOC_RECV_URBS			100

/* Get a minor range for your devices from the usb maintainer */
#define USB_TMSI_MINOR_BASE		192
#define info(...) printk(KERN_INFO __VA_ARGS__)
#define debug(...) ;
//#define debug(...) printk(KERN_INFO __VA_ARGS__)
short front_end_info[19]={0xAAAA,0x0210,1,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0xFDEC};

/* Structure to hold all of our device specific stuff */

struct tmsi_data {
	struct usb_device* udev;
	struct usb_interface* interface;
	struct kref kref;
	__u8 device_open;

	// Receive buffers
	unsigned char** bulk_recv_buffer;
	unsigned char** isoc_recv_buffer;

	// Receive URB's
	struct urb** bulk_recv_urb;
	struct urb** isoc_recv_urb;

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
};

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

static int tmsi_open(struct inode *inode, struct file *file)
{
	struct tmsi_data* dev;
	struct usb_interface* interface;
	int i, subminor;
	int retval = 0;
	debug("tmsi open\n");
	subminor = iminor(inode);

	interface = usb_find_interface(&tmsi_driver, subminor);
	if (!interface) {
		err ("%s - error, can't find device for minor %d", __FUNCTION__, subminor);
		retval = -ENODEV;
		goto exit;
	}

	dev = usb_get_intfdata(interface);
	if (!dev) {
		retval = -ENODEV;
		goto exit;
	}

	if(dev->device_open > 0)
		return -1;
	else
		dev->device_open = 1;

	/* increment our usage count for the device */
	debug("Kref Inc\n");
	kref_get(&dev->kref);

	/* save our object in the file's private structure */
	file->private_data = dev;

	// Setup incoming databuffer
	dev->buffer_lock = SPIN_LOCK_UNLOCKED;
	#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,32)
	dev->packet_buffer = &dev->inner_packet_buffer;
	kfifo_alloc(dev->packet_buffer, PACKET_BUFFER_SIZE, GFP_KERNEL);
	#else
	dev->packet_buffer = kfifo_alloc(PACKET_BUFFER_SIZE, GFP_KERNEL, &dev->buffer_lock);
	#endif

	debug("Allocatng bulk urbs\n");
	// Setup initial bulk receive URB and submit
	for(i = 0; i < BULK_RECV_URBS; ++i) {
		usb_fill_bulk_urb(dev->bulk_recv_urb[i], dev->udev, usb_rcvbulkpipe(dev->udev, dev->bulk_recv_endpoint->bEndpointAddress), dev->bulk_recv_buffer[i], dev->bulk_recv_endpoint->wMaxPacketSize, (usb_complete_t)tmsi_read_bulk_callback, dev);

		retval = usb_submit_urb(dev->bulk_recv_urb[i], GFP_KERNEL);
		if(retval)
			err("%s - failed submitting bulk read urb[%d], error %d", __FUNCTION__, i, retval);
	}
	debug("Allocatng isoc urbs\n");
	// Setup initial isochronous receive URB's and submit
	for(i = 0; i < ISOC_RECV_URBS; ++i) {
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,24)
		spin_lock_init(&dev->isoc_recv_urb[i]->lock);
#endif
		dev->isoc_recv_urb[i]->dev = dev->udev;
		dev->isoc_recv_urb[i]->pipe = usb_rcvisocpipe(dev->udev, dev->isoc_recv_endpoint->bEndpointAddress);
		dev->isoc_recv_urb[i]->transfer_buffer = dev->isoc_recv_buffer[i];
		dev->isoc_recv_urb[i]->transfer_buffer_length = dev->isoc_recv_endpoint->wMaxPacketSize;
		dev->isoc_recv_urb[i]->complete = (usb_complete_t)tmsi_read_isoc_callback;
		dev->isoc_recv_urb[i]->context = dev;
		dev->isoc_recv_urb[i]->interval = 1 << (dev->isoc_recv_endpoint->bInterval - 1);
		dev->isoc_recv_urb[i]->number_of_packets = 1;
		dev->isoc_recv_urb[i]->start_frame = -1;
		dev->isoc_recv_urb[i]->iso_frame_desc[0].offset = 0;
		dev->isoc_recv_urb[i]->iso_frame_desc[0].length = dev->isoc_recv_endpoint->wMaxPacketSize;
		dev->isoc_recv_urb[i]->transfer_flags = URB_ISO_ASAP;

		retval = usb_submit_urb(dev->isoc_recv_urb[i], GFP_KERNEL);
		if(retval)
			err("%s - failed submitting isochronous read urb[%d], error %d", __FUNCTION__, i, retval);
	}
	debug("Allocatng fifo_sem\n");
        dev->fifo_sem = kmalloc(sizeof(struct semaphore),GFP_KERNEL);
        sema_init(dev->fifo_sem,0);
        info("Tmsi device open() success");
exit:
	return retval;
}
static int tmsi_release(struct inode *inode, struct file *file)
{
	struct tmsi_data* dev;
	int retval = 0;	
	char *buf = NULL;
    info("Tmsi Release");
	dev = (struct tmsi_data*)file->private_data;
    buf = kmalloc(sizeof(front_end_info), GFP_KERNEL);
	if (!buf) {
		retval = -ENOMEM;
		goto error;
	}
    memcpy(front_end_info,buf,sizeof(front_end_info));
    info("Sending front end info");
    retval= tmsi_write_data(dev,buf,sizeof(front_end_info));
    dev->releasing=1;
    return retval;
error:
    tmsi_release_dev(dev);
    return retval;
}
static int tmsi_release_dev(struct tmsi_data* dev)
{
	
	int i;	
	if(!dev)
		return -ENODEV;
	debug("DeAllocatng bulk urbs\n");
	// Unlink current receiving bulk URB
	for(i = 0; i < BULK_RECV_URBS; ++i)
		usb_kill_urb(dev->bulk_recv_urb[i]);
	debug("DeAllocatng isoc urbs\n");
	// Unlink current receiving isochronous URB's
	for(i = 0; i < ISOC_RECV_URBS; ++i)
		usb_kill_urb(dev->isoc_recv_urb[i]);

	if(dev->device_open > 0)
		dev->device_open = 0;

	// Remove buffer

	kfifo_reset(dev->packet_buffer);
	kfifo_free(dev->packet_buffer);
	debug("DeAllocatng fifo_sem\n");
	up(dev->fifo_sem);
        kfree(dev->fifo_sem);

	/* decrement the count on our device */
	debug("Kref dec");
	kref_put(&dev->kref, tmsi_delete);

    info("Tmsi device realese() success");
    dev->releasing=0;
	return 0;
}


static ssize_t tmsi_read(struct file *file, char *buffer, size_t count, loff_t *ppos)
{
	struct tmsi_data* dev;
	char* temp_buffer = NULL;
	int retval = 0;
	size_t true_count;
	debug("Read:Waiting for sem\n");
	// Get device context from private_data file* member.
	dev = (struct tmsi_data*)file->private_data;
        if (down_timeout(dev->fifo_sem,HZ/2)!=0)
            return -ETIME;
        while (down_trylock(dev->fifo_sem)==0);
	debug("Read:Waiting for sem. Done\n");
	// Allocate temporary buffer
	temp_buffer = kmalloc(count, GFP_KERNEL);

	if(!temp_buffer) {
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
	if(copy_to_user(buffer, temp_buffer, true_count))
		retval = -EFAULT;
	else
		retval = true_count;

	kfree(temp_buffer);
	debug("Read:kfifo_len: %d. Read:%d\n",kfifo_len(dev->packet_buffer),true_count);
exit:

        if (kfifo_len(dev->packet_buffer)>0) 
	{
		up(dev->fifo_sem);
		debug("Read:Releasing sem\n");
	}
	return retval;
}
static ssize_t tmsi_write_data(struct tmsi_data* dev, char * buf, size_t count)
{
	struct urb *urb = NULL;
    int retval = 0;
    debug("Write:Allocating urb\n");
	/* Create an URB */
	urb = usb_alloc_urb(0, GFP_KERNEL);
	if (!urb) {
		retval = -ENOMEM;
		goto error;
	}
    debug("Write: fill urb\n");
	/* Initialize the urb properly */
	usb_fill_bulk_urb(urb, dev->udev, usb_sndbulkpipe(dev->udev, dev->bulk_send_endpoint->bEndpointAddress), buf, count, (usb_complete_t)tmsi_write_bulk_callback, dev);
	debug("Write: send urb\n");
	/* Send the data out the bulk port */
	retval = usb_submit_urb(urb, GFP_KERNEL);
	if (retval) {
		err("%s - failed submitting write urb, error %d", __FUNCTION__, retval);
		goto error;
	}

	/* release our reference to this urb, the USB core will eventually free it entirely */
error:
	usb_free_urb(urb);
	debug("Write: done\n");
    return retval;
}

static ssize_t tmsi_write(struct file *file, const char *user_buffer, size_t count, loff_t *ppos)
{
	struct tmsi_data* dev;
	int retval = 0;	
	char *buf = NULL;

	dev = (struct tmsi_data*)file->private_data;

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
	retval = tmsi_write_data(dev,buf,count);
    if (retval<0)
        goto error;

exit:
	return count;

error:
	if (buf) kfree(buf);
	debug("Write: error\n");
	return retval;
}


static int tmsi_ioctl(struct inode* inode, struct file* file, unsigned int command, unsigned long argument)
{
	struct tmsi_data* dev;
	unsigned long* arg_address = (unsigned long*)argument;

	dev = (struct tmsi_data*)file->private_data;

	switch(command) {
		case IOCTL_TMSI_BUFFERSIZE:
		case IOCTL_TMSI_BUFFERSIZE_64: {
			put_user(kfifo_len(dev->packet_buffer), arg_address);
			return 0;

			break;        
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

static void tmsi_write_bulk_callback(struct urb *urb, struct pt_regs *regs)
{
	struct tmsi_data* dev;
	debug("Write_callback: begin\n");
	dev = (struct tmsi_data*)urb->context;

	/* sync/async unlink faults aren't errors */
	if (urb->status && !(urb->status == -ENOENT || urb->status == -ECONNRESET || urb->status == -ESHUTDOWN))
		err("%s - nonzero write bulk status received: %d", __FUNCTION__, urb->status);

	/* free up our allocated buffer */
	kfree(urb->transfer_buffer);
	debug("Write_callback: done\n");
}


static void tmsi_read_bulk_callback(struct urb *urb, struct pt_regs *regs)
{
	int retval = 0;
	struct tmsi_data* dev;
    int release_dev=0;
	
	if(!(urb->status == -ENOENT || urb->status == -ECONNRESET || urb->status == -ESHUTDOWN)) {
		// Retrieve private data from URB's context
		dev = (struct tmsi_data*)urb->context;
		debug("Read_callback: begin\n");
		switch(urb->status) {
			case 0: {
				// Packet received is OK and cleared the buffer completely
				// Enqueue packet in user buffer
				if (urb->actual_length==0)
					break;
				#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,35)
				kfifo_in_spinlocked(dev->packet_buffer, urb->transfer_buffer, urb->actual_length, &dev->buffer_lock);
                #elif LINUX_VERSION_CODE > KERNEL_VERSION(2,6,32)
				kfifo_in_locked(dev->packet_buffer, urb->transfer_buffer, urb->actual_length, &dev->buffer_lock);				
                #else 
				kfifo_put(dev->packet_buffer, urb->transfer_buffer, urb->actual_length);
                #endif

                                up(dev->fifo_sem);
				debug("Read_callback: sem_up: %d\n",urb->actual_length);
                if (dev->releasing)
                {
                    short *buf=(short *)urb->transfer_buffer;
                    debug("message received while releasing");
                    if (buf[0]==0xAAAA && buf[1]==0x0002)
                        release_dev=1;
                    else
                        debug("buf[0]==%d, buf[1]=%d",buf[0],buf[1]);
                }
				break;
			}

			case -EPIPE: {
				// This error occurs when an endpoint has stalled.
				info("%s: The bulk endpoint has stalled. (size = %d)", __FUNCTION__, urb->actual_length);

				break;
			}

			default: {
				// Unknown error. Log to syslog
				info("%s: Unknown bulk error occurred (status %d)", __FUNCTION__, urb->status);

				break;
			}
		}

		urb->dev = dev->udev;
		urb->status = 0;

		// Submit the URB
		retval = usb_submit_urb(urb, GFP_ATOMIC);
		debug("Read_callback: urb_submit\n");
		if (retval)
			err("%s - failed submitting bulk_recv_urb, error %d", __FUNCTION__, retval);
        if (release_dev)
            tmsi_release_dev(dev);
	}
}


static void tmsi_read_isoc_callback(struct urb *urb, struct pt_regs *regs)
{
	int retval = 0;
	struct tmsi_data* dev;
	if(!(urb->status == -ENOENT || urb->status == -ECONNRESET || urb->status == -ESHUTDOWN)) {
		// Retrieve private data from URB's context
		dev = (struct tmsi_data*)urb->context;

		switch(urb->status) {
			case 0: {
				// Packet received is OK and cleared the buffer completely
				// Enqueue packet in user buffer
				if (urb->iso_frame_desc[0].actual_length==0)
					break;				
				debug("Isoc Read_callback: sem_up:%d\n",urb->iso_frame_desc[0].actual_length);
                #if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,35)
				kfifo_in_spinlocked(dev->packet_buffer, urb->transfer_buffer,  urb->iso_frame_desc[0].actual_length, &dev->buffer_lock);
                #elif LINUX_VERSION_CODE > KERNEL_VERSION(2,6,32)
				kfifo_in_locked(dev->packet_buffer, urb->transfer_buffer, urb->iso_frame_desc[0].actual_length , &dev->buffer_lock);				
                #else 
				kfifo_put(dev->packet_buffer, urb->transfer_buffer, urb->iso_frame_desc[0].actual_length);
                #endif

                                up(dev->fifo_sem);
				break;
			}

			default: {
				// Unknown error. Log to syslog
				err("%s: Unknown USB error occurred (status %d)", __FUNCTION__, urb->status);
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

static void tmsi_delete(struct kref *kref)
{
	struct tmsi_data* dev = container_of(kref, struct tmsi_data, kref);
	int i;
	info("Deleting Tmsi device ...");
	usb_put_dev(dev->udev);

	// Free device instance
	for(i = 0; i < BULK_RECV_URBS; ++i) {
		usb_free_urb(dev->bulk_recv_urb[i]);
		kfree(dev->bulk_recv_buffer[i]);
	}

	for(i = 0; i < ISOC_RECV_URBS; ++i) {
		usb_free_urb(dev->isoc_recv_urb[i]);
		kfree(dev->isoc_recv_buffer[i]);
	}

	kfree(dev);
	info("Tmsi device deleted");
}

/*******************************************************************
                  file_operations struct
 *******************************************************************/

static struct file_operations tmsi_fops = {
	.owner =	THIS_MODULE,
	.open =		tmsi_open,
	.release =	tmsi_release,
	.read =		tmsi_read,
	.write =	tmsi_write,
    #if LINUX_VERSION_CODE <= KERNEL_VERSION(2,6,35)
	.ioctl = 	tmsi_ioctl,
	#endif
};

/*******************************************************************
   USB class driver info in order to get a minor number from the
  usb core and to have the device registered with the driver core
 *******************************************************************/

static struct usb_class_driver tmsi_class = {
	.name =		"usb/tmsi%d",
	.fops =		&tmsi_fops,
	.minor_base =	USB_TMSI_MINOR_BASE,
};


static int tmsi_probe(struct usb_interface *interface, const struct usb_device_id *id)
{
	struct tmsi_data* dev = NULL;
	struct usb_host_interface* iface_desc;
	struct usb_endpoint_descriptor* endpoint;
	int i, j;
	int retval = -ENOMEM;
	debug("Tmsi probe");

	// Allocate memory for our device state and initialize it
	dev = kmalloc(sizeof(struct tmsi_data), GFP_KERNEL);
	if (dev == NULL) {
		err("Out of memory");
		goto error;
	}
	memset(dev, 0x00, sizeof(*dev));

	// Initialize dev structure
	dev->udev = usb_get_dev(interface_to_usbdev(interface));
	dev->interface = interface;
	debug("Kref init");
	kref_init(&dev->kref);

	dev->bulk_recv_buffer = kmalloc(BULK_RECV_URBS * sizeof(unsigned char*), GFP_KERNEL);
	dev->bulk_recv_urb = kmalloc(BULK_RECV_URBS * sizeof(struct urb*), GFP_KERNEL);
	dev->isoc_recv_buffer = kmalloc(ISOC_RECV_URBS * sizeof(unsigned char*), GFP_KERNEL);
	dev->isoc_recv_urb = kmalloc(ISOC_RECV_URBS * sizeof(struct urb*), GFP_KERNEL);

	/* Use the alternate interface specified in the tmsi device */
	usb_set_interface(dev->udev, 0, 1);

	/* set up the endpoint information */
	iface_desc = interface->cur_altsetting;

	for (i = 0; i < iface_desc->desc.bNumEndpoints; ++i) {
		endpoint = &iface_desc->endpoint[i].desc;

		/* we found a Bulk IN endpoint */
		if (!dev->bulk_recv_endpoint && (endpoint->bEndpointAddress & USB_DIR_IN) && ((endpoint->bmAttributes & USB_ENDPOINT_XFERTYPE_MASK) == USB_ENDPOINT_XFER_BULK)) {
			dev->bulk_recv_endpoint = endpoint;

			for(j = 0; j < BULK_RECV_URBS; ++j) {
				dev->bulk_recv_urb[j] = usb_alloc_urb(0, GFP_KERNEL);
				dev->bulk_recv_buffer[j] = kmalloc(endpoint->wMaxPacketSize, GFP_KERNEL);
			}
		}

		/* we found a Bulk OUT endpoint */
		if (!dev->bulk_send_endpoint && !(endpoint->bEndpointAddress & USB_DIR_IN) && ((endpoint->bmAttributes & USB_ENDPOINT_XFERTYPE_MASK) == USB_ENDPOINT_XFER_BULK)) {
			dev->bulk_send_endpoint = endpoint;
		}

		/* We found an Isochronous IN endpoint */
		if (!dev->isoc_recv_endpoint && (endpoint->bEndpointAddress & USB_DIR_IN) && ((endpoint->bmAttributes & USB_ENDPOINT_XFERTYPE_MASK) == USB_ENDPOINT_XFER_ISOC)) {
			dev->isoc_recv_endpoint = endpoint;

			for(j = 0; j < ISOC_RECV_URBS; ++j) {
				dev->isoc_recv_urb[j] = usb_alloc_urb(1, GFP_KERNEL);
				dev->isoc_recv_buffer[j] = kmalloc(endpoint->wMaxPacketSize, GFP_KERNEL);
			}
		}
	}

	/* Check if all required endpoints are present */
	if (!(dev->bulk_recv_endpoint->bEndpointAddress && dev->bulk_send_endpoint->bEndpointAddress && dev->isoc_recv_endpoint->bEndpointAddress)) {
		err("Could not find the required USB endpoints (bulk in/out, isochronous in)");
		goto error;
	}

	/* Check if device is attached to an USB2 interface */
	if(dev->udev->speed != USB_SPEED_HIGH) {
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
	info("Tmsi device now attached (minor %d)", interface->minor);

	return 0;

error:
	if(dev)
{
		debug("Kref dec");
		kref_put(&dev->kref, tmsi_delete);
}
	return retval;
}


static void tmsi_disconnect(struct usb_interface *interface)
{
	struct tmsi_data *dev;
	int minor = interface->minor;
	info("Disconnecting Tmsi device ...(minor %d)", minor);	

	/* prevent tmsi_open() from racing tmsi_disconnect() */
	lock_kernel();

	dev = usb_get_intfdata(interface);
	usb_set_intfdata(interface, NULL);

	usb_deregister_dev(interface, &tmsi_class);

	unlock_kernel();

	/* decrement our usage count */
	debug("Kref dec");
	kref_put(&dev->kref, tmsi_delete);

	info("Tmsi device now disconnected (minor %d)", minor);
}


static struct usb_device_id tmsi_idtable [] = {
	{ USB_DEVICE(USB_TMSI_VENDOR_ID, USB_FUSBI_PRODUCT_ID) },
	{ USB_DEVICE(USB_TMSI_VENDOR_ID, USB_SYNFI_PRODUCT_ID) },
	{ }					/* Terminating entry */
};
MODULE_DEVICE_TABLE (usb, tmsi_idtable);

static struct usb_driver tmsi_driver = {
	.name =		"tmsi driver",
	.probe =	tmsi_probe,
	.disconnect =	tmsi_disconnect,
	.id_table =	tmsi_idtable,
};


/*******************************************************************
                         Module entry points
 *******************************************************************/

static int __init usb_tmsi_init(void)
{
	int result;

	/* register this driver with the USB subsystem */
	result = usb_register(&tmsi_driver);
	if (result)
		err("%s: Registration of tmsi driver failed. (error %d)", __FUNCTION__, result);
	
	return result;
}


static void __exit usb_tmsi_exit(void)
{
	/* deregister this driver with the USB subsystem */
	usb_deregister(&tmsi_driver);

}


module_init (usb_tmsi_init);
module_exit (usb_tmsi_exit);

MODULE_LICENSE("GPL");
