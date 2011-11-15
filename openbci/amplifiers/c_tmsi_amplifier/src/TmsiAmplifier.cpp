/* 
 * File:   TmsiAmplifier.cpp
 * Author: Macias
 * 
 * Created on 13 październik 2010, 13:14
 */
#include <stdio.h>
#include <stdlib.h>
#ifdef BLUETOOTH
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>
#endif
#include <sys/socket.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <signal.h>
#include <string>
#include <iostream>
#include <sstream>
#include <string.h>
#include "TmsiAmplifier.h"
#include "nexus/tmsi.h"
#include <boost/program_options.hpp>
#include <boost/bind.hpp>
namespace po=boost::program_options;

TmsiAmplifier::TmsiAmplifier():AmplifierDriver(){
    dev.Channel = NULL;
    vli.SampDiv = NULL;
    channel_data = NULL;
    channel_data_index=0;
    read_errors=0;
    fd=-1;
    read_fd=-1;
    dump_fd=-1;
    mode=0;
}
po::options_description TmsiAmplifier::get_options(){
	po::options_description options=AmplifierDriver::get_options();
	options.add_options()
			("device_path,d",po::value<string>()->default_value("/dev/tmsi0")
					->notifier(boost::bind(&TmsiAmplifier::connect_device,this,false,_1)),"Device path for usb connection")
			("bluetooth_addr,b",po::value<string>()
					->notifier(boost::bind(&TmsiAmplifier::connect_device,this,true,_1)),"Bluetooth address of amplifier")
			("amplifier_responses,r",po::value<string>()
					->notifier(boost::bind(&TmsiAmplifier::read_from,this,_1)),"File with saved amplifier responses. Useful for debug")
			("save_responses",po::value<string>()
					->notifier(boost::bind(&TmsiAmplifier::dump_to,this,_1)),"File for dumping amplifier responses");
	po::typed_value<string> * act_channels=(po::typed_value<string> *)options.find("active_channels",true).semantic().get();
	act_channels->default_value("1,2,onoff,Driver_Saw");
	return options;
}
void TmsiAmplifier::init(po::variables_map &vm){
	refreshInfo();
}
void TmsiAmplifier::connect_device(bool bluetooth,const string &address){
	if (fd>=0)
		close(fd);
	if (read_fd==fd)
		read_fd=-1;
	if (bluetooth)
		fd=connect_bluetooth(address);
	else
		fd=connect_usb(address);
	if (fd<0)
		cout << "DEVICE OPEN ERROR: "<<address << " errno: "<<fd<<" "<<strerror(fd);
	else
		logger.info()<< (bluetooth?"Bluetooth ":"Usb ") << "device connected "<<address<<"\n";
	if (read_fd<0)
	read_fd=fd;
}
int TmsiAmplifier::connect_usb(const string & address) {
	mode=USB_AMPLIFIER;
	return open(address.c_str(), O_RDWR);
}

int TmsiAmplifier::connect_bluetooth(const string & address) {
	int s, status;
	mode=BLUETOOTH_AMPLIFIER;
#ifdef BLUETOOTH
	struct sockaddr_rc addr = {0};


	/* allocate a socket */
	s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);

	/* set the connection parameters (who to connect to) */
	addr.rc_family = AF_BLUETOOTH;
	addr.rc_channel = (uint8_t) 1;
	addr.rc_bdaddr = *BDADDR_ANY;
	str2ba(address.c_str(), &addr.rc_bdaddr );

	/* open connection to TMSi hardware */
	status = connect(s, (struct sockaddr *)&addr, sizeof(addr));
      /* return socket */
#endif
	return s;
}
void TmsiAmplifier::read_from(const string &file){
if (read_fd && read_fd!=fd)
	close(read_fd);
	read_fd=open(file.c_str(),O_RDONLY);
	if (read_fd<0)
		read_fd=fd;
	else
		logger.info()<<"Reading amplifier responses from: " << file <<"\n";
}
void TmsiAmplifier::dump_to(const string &file){
	if (dump_fd>=0)
		close(dump_fd);
	dump_fd = open(file.c_str(), O_WRONLY|O_CREAT|O_TRUNC,S_IRWXU);
	if (dump_fd>=0)
		logger.info() << "Dumping Amplifier responses to: "<< file <<"\n";

}
int TmsiAmplifier::refreshInfo() {
    if (sampling) {
        cout << "Cannot refresh info while sampling!\n";
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
    logger.info()<<"Sending request for"<<get_type_name(type) <<"\n";
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
            break;
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
            break;

    }
    return false;
}

bool TmsiAmplifier::_refreshInfo(int type) {
    int counter = 0;
    while (counter++ < 20) {
	send_request(type);
        if (br < 0 || tms_chk_msg(msg, br) != 0)
            fprintf(stderr, "Error while receiving message (%d)", br);
        else
            if (update_info(type)) return true;
    }
    fprintf(stderr, "Could not receive proper %s!!\n",get_type_name(type));
    return false;
}

void TmsiAmplifier::start_sampling() {
    if (fd < 0 || read_fd < 0) return;
    fei.mode &= 0x10;
    fei.currentsampleratesetting = sample_rate_div&0xFFFF;
    br = 0;
    keep_alive=1;
    int counter = 0;
    int type=0;
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
    free_channel_data(channel_data);
    channel_data = alloc_channel_data(type == TMSVLDELTADATA);
    channel_data_index=1<<30;
    AmplifierDriver::start_sampling();
}

void TmsiAmplifier::stop_sampling() {
    if (fd < 0) return;
    fei.mode = 0x11;
    if (!sampling) return;
    signal(SIGINT,SIG_DFL);
    signal(SIGTERM,SIG_DFL);
    logger.info() <<"Sending stop message...\n";
    tms_write_frontendinfo(fd, &fei);
    AmplifierDriver::stop_sampling();
    int retry=0;
    read_errors=0;
    receive();
    while (br>0)
    {   int type=tms_get_type(msg, br);
        if (type == TMSACKNOWLEDGE) {
            tms_get_ack(msg, br, &ack);
            tms_prt_ack(stderr, &ack);
            in_debug(return);
            if (mode==BLUETOOTH_AMPLIFIER|| read_fd!=fd) return;
        }
        if (++retry % (2 * sampling_rate) == 0)
            tms_write_frontendinfo(fd,&fei);
        receive();
    }
    logger.info()<<"Stop sampling succeeded after "<<retry<<" messages!\n";
}
uint64_t TmsiAmplifier::next_samples() {
    channel_data_index++;
    if (channel_data_index >= channel_data[0].ns)
		while (sampling) {
			receive();
//			if (fd==read_fd)
//				last_sample =boost::posix_time::microsec_clock::local_time().time_of_day().total_microseconds();
//			else
//				last_sample = AmplifierDriver::next_samples();
			int type = tms_get_type(msg, br);
			if (tms_chk_msg(msg, br) != 0) {
				fprintf(stderr, "Sample dropped!!!\n");
				continue;
			}
			if (type == TMSCHANNELDATA || type == TMSVLDELTADATA) {
				uint64_t result=AmplifierDriver::next_samples();
				tms_get_data(msg, br, &dev, channel_data);
				channel_data_index = 0;
				debug("Channel data received...\n");
				if (--keep_alive==0)
				{
					keep_alive=sampling_rate*KEEP_ALIVE_RATE/channel_data[0].ns;
					logger.info()<<"Sending keep_alive\n";
					tms_snd_keepalive(fd);
				}
				return result;
			}
		}
	return AmplifierDriver::next_samples();
}

 uint TmsiAmplifier::get_digi(uint index) {
    if (channel_data == NULL) return 0;
    tms_channel_data_t channel=channel_data[index];
    int digi = channel.data[0].isample;
    for (int i = 1; i < channel.ns; i++)
        digi |= channel.data[i].isample;
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
  int32_t all_br=0;        /**< all bytes read */
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
      if (br==0 && ++rtc>TIMEOUT) 
		{
			fprintf(stderr,"Warning: Read 0 bytes\n");	
			no_error=0;
		}
      if (br<0)
      {
          perror("# Receive message: file read error");
        --no_error;
        continue;
      }
      else if (br){ 
          all_br+=br;
	  if (dump_fd!=-1) write(dump_fd,&msg[i],br);
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
  if (no_error==0) {
    fprintf(stderr,"# Error: timeout on rest of message. Bytes read: %d\n",all_br);
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
    int channel_count=fei.nrofswchannels;
    /* allocate storage space for all channels */
   
    tms_channel_data_t *channel_data = (tms_channel_data_t *) calloc(channel_count, sizeof (tms_channel_data_t));
    for (i = 0; i < channel_count; i++) {
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
    for (i = 0; i < channel_count; i++) {
        channel_data[i].td = ns_max / (channel_data[i].ns * tms_get_sample_freq());
    }
    return channel_data;
}
