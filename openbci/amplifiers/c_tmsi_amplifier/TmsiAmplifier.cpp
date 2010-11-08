/* 
 * File:   TmsiAmplifier.cpp
 * Author: Macias
 * 
 * Created on 13 październik 2010, 13:14
 */
#include <stdio.h>
#include <stdlib.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <signal.h>
#include <string>
#include <iostream>
#include <sstream>
#include "TmsiAmplifier.h"
#include "nexus/tmsi.h"
TmsiAmplifier * tmsiAmplifierInstance=NULL;

void handler(int sig)
{
    signal(sig,SIG_DFL);
    fprintf(stderr,"Signal %d (%s) intercepted. Driver stopping\n",
            sig,strsignal(sig));
    tmsiAmplifierInstance->~TmsiAmplifier();
    exit(-1);
}


TmsiAmplifier::TmsiAmplifier(const char * address, int type, const char * r_address, const char* dump_file /* = NULL */) {
    printf("TmsiAmplifier writing to: %s\n", address);
    if (r_address!=NULL)
        printf(" reading from: %s",r_address);
    if (dump_file!=NULL)
        printf(" dumping amplifier output to: %s",dump_file);
    printf("\n");
    if (tmsiAmplifierInstance!=NULL)
        fprintf(stderr,"Warning: multiple tmsiAmplifier instances!!\n");
    tmsiAmplifierInstance = this;
    dev.Channel = NULL;
    vli.SampDiv = NULL;
    channel_data = NULL;
    channel_data_index=0;
    read_errors=0;
    mode=type;
    if (type == USB_AMPLIFIER)
        fd = connect_usb(address);
    else
        fd = connect_bluetooth(address);
    if (r_address != NULL)
        read_fd = open(r_address, O_RDONLY);
    else
        read_fd = fd;
    if (dump_file!=NULL)
        dump_fd = open(dump_file, O_WRONLY|O_CREAT|O_TRUNC);
    else
        dump_fd=-1;
    debug("Descriptors: %d %d", fd, read_fd);
    if (fd <= 0) {
        perror("DEVICE OPEN ERROR");
        exit(-1);
        return;
    }
    refreshInfo();

}

int TmsiAmplifier::connect_usb(const char * address) {
    return open(address, O_RDWR);
}

int TmsiAmplifier::connect_bluetooth(const char * address) {
       struct sockaddr_rc addr = {0};
      int s, status;
    
      /* allocate a socket */
      s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    
      /* set the connection parameters (who to connect to) */
      addr.rc_family = AF_BLUETOOTH;
      addr.rc_channel = (uint8_t) 1;
      addr.rc_bdaddr = *BDADDR_ANY;
      str2ba(address, &addr.rc_bdaddr );
    
      /* open connection to TMSi hardware */
      status = connect(s, (struct sockaddr *)&addr, sizeof(addr));
    
      /* return socket */
      return(s);
    return -1;
}

int TmsiAmplifier::refreshInfo() {
    if (sampling) {
        fprintf(stderr, "Cannot refresh info while sampling");
        return -1;
    }
    if (dev.Channel != NULL) {
        free(dev.Channel);
        dev.Channel = NULL;
    }
    if (vli.SampDiv != NULL) {
        free(vli.SampDiv);
        vli.SampDiv = NULL;
    }
    refreshFrontEndInfo();
    refreshIDData();
    refreshVLDeltaInfo();
    return 0;
}

int TmsiAmplifier::send_request(int type) {
    printf("Sending request for %s\n", get_type_name(type));
    switch (type) {
        case TMSFRONTENDINFO:
            tms_snd_FrontendInfoReq(fd);
            receive();
            break;
        case TMSIDDATA:
            br = fetch_iddata();
            debug("%d",print_message(stderr));
            break;
        case TMSVLDELTAINFO:
            tms_snd_vldelta_info_request(fd);
            receive();
            break;
        case TMSRTCDATA:
            tms_send_rtc_time_read_req(fd);
            receive();
            break;
        default:
            fprintf(stderr, "Wrong Request\n");
    }
    return 0;
}

bool TmsiAmplifier::update_info(int type) {
    debug("Got type: %s", get_type_name(tms_get_type(msg, br)));
    if (tms_get_type(msg, br) != type) {
        debug(" expected type: %s\n", get_type_name(type));
        return false;
    } else
    {
        debug("\n");
    }
    if (tms_chk_msg(msg,br)!=0) return false;
    switch (type) {
        case TMSFRONTENDINFO:
            return tms_get_frontendinfo(msg, br, &fei) != -1;
        case TMSIDDATA:
            return tms_get_iddata(msg, br, &dev) != -1;
        case TMSVLDELTAINFO:
            return tms_get_vldelta_info(msg, br, dev.NrOfChannels, &vli) != -1;
        case TMSRTCDATA:
            return tms_get_rtc(msg, br, &rtc) != -1;
        case TMSACKNOWLEDGE:
            return tms_get_ack(msg, br, &ack) != -1;
        default:
            fprintf(stderr, "Wrong Info type\n");

    }
    return false;
}

bool TmsiAmplifier::_refreshInfo(int type) {
    int counter = 0;
    send_request(type);
    while (counter++ < 20) {
        if (br < 0 || tms_chk_msg(msg, br) != 0)
            fprintf(stderr, "Error while receiving message (%d)", br);
        else
            if (update_info(type)) return true;
        receive();
    }
    fprintf(stderr, "Could not receive proper %s!!\n",get_type_name(type));
    return false;
}

void TmsiAmplifier::load_channel_desc() {
    channels_desc.clear();
    tms_prt_iddata(stderr,&dev);
    for (int i = 0; i < dev.NrOfChannels; i++) {
        channel_desc chan;
        tms_channel_desc_t &t_chan = dev.Channel[i];
        chan.name = t_chan.ChannelDescription;
        chan.gain = t_chan.GainCorrection;
        chan.offset = t_chan.OffsetCorrection;
        chan.a = t_chan.Type.a;
        chan.b = t_chan.Type.b;
        chan.exp = t_chan.Type.Exp;
        chan.type = t_chan.Type.Type;
        chan.subtype = t_chan.Type.SubType;
        chan.is_signed = t_chan.Type.Format & 0x100;
        chan.bit_length = t_chan.Type.Format & 0x11;
        channels_desc.push_back(chan);
        if (chan.name=="Digi")
            digi_channel=i;
    }
    channel_desc ch;
    ch.name="Empty";
    channels_desc.push_back(ch);
    ch.name="trig";
    channels_desc.push_back(ch);
    ch.name="onoff";
    channels_desc.push_back(ch);
    ch.name="bat";
    channels_desc.push_back(ch);
}

void TmsiAmplifier::start_sampling() {
    if (fd < 0) return;
    fei.mode &= 0x10;
    fei.currentsampleratesetting = sample_rate_div&0xFFFF;
    br = 0;
    keep_alive=1;
    int counter = 0;
    int type;
    signal(SIGINT,handler);
    signal(SIGTERM,handler);
    tms_write_frontendinfo(fd, &fei);
    receive();
    while (counter < sampling_rate && (!update_info(TMSACKNOWLEDGE))) {
        counter++;
        if (counter%(sampling_rate/4)==0 || read_errors==MAX_ERRORS/2)
        {
            fprintf(stderr,"Sending start request again....\n");
            tms_write_frontendinfo(fd,&fei);
        }
        receive();
        type = tms_get_type(msg, br);
        //if (type == TMSCHANNELDATA || type == TMSVLDELTADATA) break;
    }
    if (ack.errorcode != 0) {
        tms_prt_ack(stderr, &ack);
        tms_prt_frontendinfo(stderr, &fei, 0, 1);
    }
    while (type != TMSCHANNELDATA && type != TMSVLDELTADATA) {
        receive();
        type = tms_get_type(msg, br);
    }
    sampling=true;
    free_channel_data(channel_data);
    channel_data = alloc_channel_data(type == TMSVLDELTADATA);

}

void TmsiAmplifier::stop_sampling() {
    if (fd < 0) return;
    fei.mode = 0x11;
    if (!sampling) return;
    signal(SIGINT,SIG_DFL);
    signal(SIGTERM,SIG_DFL);
    printf("Sending stop message...\n");
    tms_write_frontendinfo(fd, &fei);
    int retry=0;
    read_errors=0;
    receive();
    while (br>0)
    {   int type=tms_get_type(msg, br);
        if (type == TMSACKNOWLEDGE) {
            tms_get_ack(msg, br, &ack);
            tms_prt_ack(stderr, &ack);
            printf("Ack Received. Clearing buffer from pending messages...\n");
            in_debug(return);
            if (mode==BLUETOOTH_AMPLIFIER|| read_fd!=fd) return;
        }
        if (++retry % (2 * sampling_rate) == 0)
        {
            printf("After %d I am still getting messages\n"
                    "Trying to stop again...\n",retry);
            tms_write_frontendinfo(fd,&fei);
        }
        receive();
    }
    printf("Stop sampling succeeded after %d messages!\n",retry);
    sampling=false;
}


bool TmsiAmplifier::get_samples() {
    if (!sampling || fd < 0)
        return false;
    if (channel_data_index < channel_data[0].ns)
        return true;
    while (sampling) {
        receive();
        int type = tms_get_type(msg, br);
        if (tms_chk_msg(msg, br) != 0) {
            fprintf(stderr, "Sample dropped!!!\n");
            continue;
        }
        if (type == TMSCHANNELDATA || type == TMSVLDELTADATA) {
            tms_get_data(msg, br, &dev, channel_data);
            channel_data_index = 0;
            digi=-1;
            debug("Channel data received...\n");
            if (--keep_alive==0)
            {
                keep_alive=sampling_rate*KEEP_ALIVE_RATE/channel_data[0].ns;
                printf("Sending keep_alive\n");
                tms_snd_keepalive(fd);
            }

            return true;
        }
    }
    return false;
}
//template<typename T>
//int TmsiAmplifier::fill_samples(vector<T>& samples) {
//    debug("Filling samples\n");
//    if (!get_samples()) return -1;
//    //printf("fill_samplse %d\n",sampling);
//    if (sampling)
//    {
//        for (unsigned int i = 0; i < act_channels.size(); i++)
//            _put_sample(&samples[i],channel_data[act_channels[i]].data[channel_data_index]);
//        channel_data_index++;
//    debug("Filling special channels\n");
//    if (spec_channels[TRIGGER_CHANNEL]!=-1)
//        samples[spec_channels[TRIGGER_CHANNEL]]=is_trigger();
//    if (spec_channels[ONOFF_CHANNEL]!=-1)
//        samples[spec_channels[ONOFF_CHANNEL]]=is_onoff_pressed();
//    if (spec_channels[BATTERY_CHANNEL]!=-1)
//        samples[spec_channels[BATTERY_CHANNEL]]=is_battery_low()?1:0;
//    return active_channels.size();
//    }
//    return -1;
//}

//int TmsiAmplifier::fill_samples(vector<float>& samples) {
//    if (!get_samples()) return -1;
//    if (sampling){
//        for (unsigned int i = 0; i < act_channels.size(); i++)
//            samples[i] = channel_data[act_channels[i]].data[channel_data_index].sample;
//    channel_data_index++;
//    if (spec_channels[TRIGGER_CHANNEL]!=-1)
//        samples[spec_channels[TRIGGER_CHANNEL]]=get_digi()&TRIGGER_ACTIVE;
//    if (spec_channels[ONOFF_CHANNEL]!=-1)
//        samples[spec_channels[ONOFF_CHANNEL]]=get_digi()&ON_OFF_BUTTON;
//    if (spec_channels[BATTERY_CHANNEL]!=-1)
//        samples[spec_channels[BATTERY_CHANNEL]]=get_digi()&BATTERY_LOW;
//    return active_channels.size();}
//    return -1;
//}

 int TmsiAmplifier::get_digi() {
    if (channel_data == NULL) return 0;
    if (digi!=-1) return digi;
    digi = channel_data[fei.nrofswchannels - 2].data[0].isample;
    for (int i = 1; i < channel_data[fei.nrofswchannels - 1].ns; i++)
        digi |= channel_data[fei.nrofswchannels - 2].data[i].isample;
    return digi;
}
void TmsiAmplifier::receive() {
    debug(">>>>>>>>>>>>>>>Receiving Message>>>>>>>>>>>>>>>\n");
    debug("flush %d",fflush(stderr));
    br = rcv_message(msg, MESSAGE_SIZE);
    debug("%d",print_message(stderr));
    debug("<<<<<<<<<<<<<<<End Message<<<<<<<<<<<<<<<<<<<<<\n");
    
}

const char * TmsiAmplifier::get_type_name(int type) {
    switch (type) {
        case TMSACKNOWLEDGE:
            return "TMSACKNOWLEDGE";
            break;
        case TMSCHANNELDATA:
            return "TMSCHANNELDATA";
            break;
        case TMSFRONTENDINFOREQ:
            return "TMSFRONTENDINFOREQ";
            break;
        case TMSRTCREADREQ:
            return "TMSRTCREADREQ";
            break;
        case TMSRTCDATA:
            return "TMSRTCDATA";
            break;
        case TMSRTCTIMEREADREQ:
            return "TMSRTCTIMEREADREQ";
            break;
        case TMSRTCTIMEDATA:
            return "TMSRTCTIMEDATA";
            break;
        case TMSFRONTENDINFO:
            return "TMSFRONTENDINFO";
            break;
        case TMSKEEPALIVEREQ:
            return "TMSKEEPALIVEREQ";
            break;
        case TMSVLDELTADATA:
            return "TMSVLDELTADATA";
            break;
        case TMSVLDELTAINFOREQ:
            return "TMSVLDELTAINFOREQ";
            break;
        case TMSVLDELTAINFO:
            return "TMSVLDELTAINFO";
            break;
        case TMSIDREADREQ:
            return "TMSIDREADREQ";
            break;
        case TMSIDDATA:
            return "TMSIDDATA";
            break;
        default:
            return "UNKNOWN";
    }
}

int TmsiAmplifier::_print_message(FILE * f,uint8_t *msg, int br) {
    int type = tms_get_type(msg, br);
    bool valid = tms_chk_msg(msg, br) == 0;
    fprintf(f, "Message length: %d, type: %x(%20s), valid: %s\n",
            br, type, get_type_name(type), valid ? "YES" : "NO");
    if (br < 2) return -1;
    //if (type==TMSCHANNELDATA) return 0;
    fprintf(f, "%5s | %6s %6s | %5s | %6s %6s\n", "nr", "[nr]", "[nr+1]", "chars", "[nr+1]", "[nr]");

    for (int i = 0; i + 1 < br; i += 2) {
        fprintf(f, "%5d | %6d %6d | %2c %2c | %6x  %6x\n",
                i/2, msg[i], msg[i + 1], isprint(msg[i]) ? msg[i] : '.',
                isprint(msg[i + 1]) ? msg[i + 1] : '.', msg[i + 1], msg[i]);
    }
    if (valid) {
        switch (type) {
            case TMSACKNOWLEDGE:
                tms_acknowledge_t ack;
                tms_get_ack(msg, br, &ack);
                tms_prt_ack(f, &ack);
                break;
            case TMSRTCTIMEDATA:
                tms_rtc_t rtc;
                tms_get_rtc(msg, br, &rtc);
                tms_prt_rtc(f, &rtc, 0, 1);
                break;
            case TMSFRONTENDINFO:
                tms_frontendinfo_t fei;
                tms_get_frontendinfo(msg, br, &fei);
                tms_prt_frontendinfo(f, &fei, 0, 1);
                break;
            case TMSVLDELTAINFO:
                tms_vldelta_info_t vli;
                tms_get_vldelta_info(msg, br, dev.NrOfChannels, &vli);
                tms_prt_vldelta_info(f, &vli, 0, 1);
                break;
            case TMSIDDATA:
                tms_input_device_t idev;
                if (br < 500) return -1;
                tms_get_iddata(msg, br, &idev);
                tms_prt_iddata(f, &idev);
                break;
            case TMSCHANNELDATA:
            case TMSVLDELTADATA:
                tms_channel_data_t *chan = alloc_channel_data(type == TMSVLDELTADATA);
                tms_get_data(msg, br, &dev, chan);
                tms_prt_channel_data(f, &dev, chan, 0);
                free_channel_data(chan);
                break;
        }
    }
    return 0;
}

TmsiAmplifier::~TmsiAmplifier() {
    stop_sampling();
    if (dev.Channel != NULL) {
        free(dev.Channel);
        dev.Channel = NULL;
    }
    if (vli.SampDiv != NULL) {
        free(vli.SampDiv);
        vli.SampDiv = NULL;
    }
    free_channel_data(channel_data);
    close(fd);
    if (read_fd != fd)
        close(read_fd);
    if (dump_fd!=-1)
        close(dump_fd);
}
//------------------------MODIFIED NEXUS FUNCTIONS---------------------
int32_t tms_put_int(int32_t a, uint8_t *msg, int32_t *s, int32_t n);
int32_t tms_send_iddata_request(int32_t fd, int32_t adr, int32_t len);
int32_t tms_msg_size(uint8_t *msg, int32_t n, int32_t *i);
int16_t tms_put_chksum(uint8_t *msg, int32_t n);
#define TMSBLOCKSYNC (0xAAAA)    /**< TMS block sync word */

int TmsiAmplifier::fetch_iddata()
{
  int32_t i;        /**< general index */
  int16_t adr=0x0000; /**< start address of buffer ID data */
  int16_t len=0x80;   /**< amount of words requested */
  int32_t tbw=0;      /**< total bytes written in 'msg' */
  uint8_t rcv[512];   /**< recieve buffer */
  int32_t type;       /**< received IDData type */
  int32_t size;       /**< received IDData size */
  int32_t tsize=0;    /**< total received IDData size */
  int32_t start=0;    /**< start address in receive ID Data packet */
  int32_t length=0;   /**< length in receive ID Data packet */
  int32_t rtc=0;      /**< retry counter */

  /* prepare response header */
  tbw=0;
  /* block sync */
  tms_put_int(TMSBLOCKSYNC,msg,&tbw,2);
  /* length 0xFF */
  tms_put_int(0xFF,msg,&tbw,1);
  /* IDData type */
  tms_put_int(TMSIDDATA,msg,&tbw,1);
  /* temp zero length, final will be put at the end */
  tms_put_int(0,msg,&tbw,4);
  int header_size=tbw;
  /* start address and maximum length */
  adr=0x0000;
  len=0x80;

  rtc=0;
  /* keep on requesting id data until all data is read */
  while ((rtc<20) && (len>0) && (tbw<MESSAGE_SIZE)) {
    rtc++;
    if (tms_send_iddata_request(fd,adr,len) < 0) {
        fprintf(stderr,"# Sending request for IDDATA for addr %d failed \n",adr);
      //continue;
    }
    /* get response */
    br=rcv_message(rcv,sizeof(rcv));
    //_print_message(stderr,rcv,br);
    /* check checksum and get type of response */
    type=tms_get_type(rcv,br);
    if (type!=TMSIDDATA) {
      fprintf(stderr,"# Warning: tms_get_iddata: unexpected type 0x%02X\n",type);
      continue;
    } else {
      /* get payload of 'rcv' */
      size=tms_msg_size(rcv,sizeof(rcv),&i);
      /* get start address */
      i=4;
      start=tms_get_int(rcv,&i,2);
      /* get length */
      length=tms_get_int(rcv,&i,2);
      /* copy response to final result */
      int buf_start=start*2+header_size;
      debug("IDDATA Received!! Address: %d length: %d write to %d\n",start,length,buf_start/2);
      if (buf_start+2*length>MESSAGE_SIZE) {
        fprintf(stderr,"# Error: tms_get_iddata: msg too small %d\n",buf_start+2*length);
      } else {
        memcpy(msg+buf_start,rcv+i,2*length);
        if (start>tsize) continue;
        adr=start+length;
        if (adr>tsize)
            tsize=adr;
      }
      /* if block ends with 0xFFFF, then this one was the last one */
      if ((rcv[2*size-2]==0xFF) && (rcv[2*size-1]==0xFF)) { break; }
    }
  }
  /* put final total size */
  i=4; tms_put_int(tsize,msg,&i,4);
  /* add checksum */
  tbw=tms_put_chksum(msg,tsize*2+header_size);
  /* return number of byte actualy written */
  br=tbw;
  return(tbw);
}
#define TIMEOUT 1000
#define NUMBER_OF_ERRORS 2
#define MINIMUM_MESSAGE_LENGTH 6
int TmsiAmplifier::rcv_message(uint8_t *msg,int n){

  int32_t i=0;         /**< byte index */
  int32_t br=0;        /**< bytes read */
  int32_t size=0;      /**< payload size [uint16_t] */
  int32_t no_error=NUMBER_OF_ERRORS;
  int32_t meta_data=MINIMUM_MESSAGE_LENGTH;
  int32_t end;
  int fd=read_fd,rtc=0;;
  br=0;
  msg[0]=0;
  i=0;
  while (no_error &&i<meta_data)
  {
      br=read(fd,&msg[i],meta_data-i);
      if (br==0 && ++rtc>TIMEOUT) no_error=0;
      if (br<0)
      {
          perror("# Receive message: file read error");
        --no_error;
        continue;
      }
      else if (br){ if (dump_fd!=-1) write(dump_fd,&msg[i],br);
          if (msg[0] == msg[1] && msg[0] == 0xAA)
                i += br;
            else { int j=i;
                for (j = i; j < i + br; j++)
                    if (j>0 && msg[j] == msg[j - 1] && msg[j] == 0xAA) {
                        memcpy(msg, msg + j-1, i + br - j+1);
                        i = i + br - j+1;
                        break;
                    }
            if (j>=i+br)
            {
                msg[0] = msg[i + br - 1];
                i = 1;
            }
            }
      }


  }
    size=msg[2]&0xFF;
  if (size==255)
  {
      i=4;
      size=tms_get_int(msg,&i,4);
      meta_data+=4;
  }

  /* read rest of message */
  end = 2*size+meta_data;
  if (end>n) {
    fprintf(stderr,"# Warning: message buffer size %d too small (required %d) !\n",n,end);
    return (-1);
  }
  while (no_error && (i<end) ) {
    br=read(fd,&msg[i],end-i);
    if (br==0 && ++rtc>TIMEOUT) no_error=0;
    if (br<0){
        perror("# Receive message file read error");
        --no_error;
        continue;
    }
    if (dump_fd!=-1&&br) write(dump_fd,&msg[i],br);
    i+=br;
  }
  if (!no_error) {
    fprintf(stderr,"# Error: timeout on rest of message\n");
    read_errors++;
    if (read_errors>MAX_ERRORS)
    {
        fprintf(stderr,"Couldnt get message after %d tries. Connection lost.",
                read_errors);
        stop_sampling();
        exit(-1);
    }
    return(-3);
  }
  read_errors=0;
  return (i);
}
tms_channel_data_t * TmsiAmplifier::alloc_channel_data(bool vldelta = false) {
    int32_t i; /**< general index */
    int32_t ns_max = 1; /**< maximum number of samples of all channels */

    /* allocate storage space for all channels */
    tms_channel_data_t *channel_data = (tms_channel_data_t *) calloc(dev.NrOfChannels, sizeof (tms_channel_data_t));
    for (i = 0; i < dev.NrOfChannels; i++) {
        if (i<dev.NrOfChannels)
        if (!vldelta) {
            channel_data[i].ns = 1;
        } else {
            channel_data[i].ns = (vli.TransFreqDiv + 1) / (vli.SampDiv[i] + 1);
        }
        else
            channel_data[i].ns=ns_max;
        /* reset sample counter */
        channel_data[i].sc = 0;
        if (channel_data[i].ns > ns_max) {
            ns_max = channel_data[i].ns;
        }
        channel_data[i].data = (tms_data_t *) calloc(channel_data[i].ns, sizeof (tms_data_t));
    }
    for (i = 0; i < dev.NrOfChannels; i++) {
        channel_data[i].td = ns_max / (channel_data[i].ns * tms_get_sample_freq());
    }
    return channel_data;
}
using namespace std;
void TmsiAmplifier::set_active_channels(vector<string>& channels)
{
    int tmp;
    act_channels.clear();
    spec_channels.clear();
    for (int i=0;i<=ADDITIONAL_CHANNELS;i++)
        spec_channels.push_back(-1);
    printf("Sending channels: ");
    for (unsigned int i=0;i<channels.size();i++)
    {
        stringstream stream(channels[i]);
        if ((stream>>tmp)==0)
        {
            bool ok=false;
            for(unsigned int j=0;j<channels_desc.size();j++)
                if (channels_desc[j].name==channels[i]){
                    if (j<fei.nrofswchannels){
                        act_channels.push_back(j);
                        printf("%s(%d), ",channels_desc[j].name.c_str(),j);
                        ok=true;
                    }
                    else
                    {
                        act_channels.push_back(0);
                        spec_channels[j-fei.nrofswchannels]=i;
                        printf("%s(%d), ",channels_desc[j].name.c_str(),fei.nrofswchannels-j);
                        ok=true;
                    }
                }
            if (!ok)
            {
                fprintf(stderr,"Unknown channel name: %s",channels[i].c_str());
                exit(-1);
            }
        }
        else {
            if (tmp>=0)
                if (tmp>=fei.nrofswchannels)
                {
                    fprintf(stderr,"Channel index to big:%d (max:%d)!\n",tmp,fei.nrofswchannels);
                    exit(-1);
                }
                else
                {
                    act_channels.push_back(tmp);
                    printf("%s(%d), ",channels_desc[tmp].name.c_str(),tmp);
                }
            else
                if (-tmp>ADDITIONAL_CHANNELS)
                {
                    fprintf(stderr,"Unknown special channel: %d!\n",tmp);
                    exit(-1);
                }
                else{
                    spec_channels[-tmp]=i;
                    printf("%s(%d), ",channels_desc[fei.nrofuserchannels-tmp].name.c_str(),tmp);
                }
        }
    }
    printf("\n");
}
