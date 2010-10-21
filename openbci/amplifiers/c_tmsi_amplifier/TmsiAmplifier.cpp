/* 
 * File:   TmsiAmplifier.cpp
 * Author: Macias
 * 
 * Created on 13 październik 2010, 13:14
 */
#include <stdio.h>
#include <stdlib.h>
//#include <net/bluetooth/bluetooth.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <signal.h>
#include <string.h>
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

int fd_dump=-1;

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
    signal(SIGINT,handler);
    signal(SIGTERM,handler);
    sampling = false;
    dev.Channel = NULL;
    vli.SampDiv = NULL;
    channel_data = NULL;
    channel_data_index=0; 
    if (type == USB_AMPLIFIER)
        fd = connect_usb(address);
    else
        fd = connect_bluetooth(address);
    if (r_address != NULL)
        read_fd = open(r_address, O_RDONLY);
    else
        read_fd = fd;
    if (dump_file!=NULL)
        fd_dump = open(dump_file, O_WRONLY|O_CREAT|O_TRUNC);
    debug("Descriptors: %d %d", fd, read_fd);
    if (fd <= 0) {
        perror("DEVICE OPEN ERROR");
        return;
    }
    refreshInfo();

}

int TmsiAmplifier::connect_usb(const char * address) {
    return open(address, O_RDWR);
}

int TmsiAmplifier::connect_bluetooth(const char * address) {
    //    struct sockaddr_rc addr = { 0 };
    //  int s, status;
    //
    //  /* allocate a socket */
    //  s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    //
    //  /* set the connection parameters (who to connect to) */
    //  addr.rc_family = AF_BLUETOOTH;
    //  addr.rc_channel = (uint8_t) 1;
    //  str2ba(fname, &addr.rc_bdaddr );
    //
    //  /* open connection to TMSi hardware */
    //  status = connect(s, (struct sockaddr *)&addr, sizeof(addr));
    //
    //  /* return socket */
    //  return(s);
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
            br = tms_fetch_iddata(read_fd, msg, MESSAGE_SIZE);
            print_message(stderr);
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
    }
}

void TmsiAmplifier::start_sampling() {
    if (fd < 0) return;
    fei.mode &= 0x10;
    fei.currentsampleratesetting = sample_rate_div&0xFFFF;
    sampling = true;
    br = 0;
    keep_alive=sampling_rate*KEEP_ALIVE_RATE;
    int counter = 20;
    int type;
    while (counter-- > 0 && (!update_info(TMSACKNOWLEDGE) || ack.errorcode != 0)) {
        debug("Sending frontendinfo\n");
        tms_write_frontendinfo(fd, &fei);
        receive();

        if (br < 0 || tms_chk_msg(msg, br) != 0) {
            fprintf(stderr, "Error while receiving message (%d)", br);
            br = 0;
        }
        type = tms_get_type(msg, br);
        if (type == TMSCHANNELDATA || type == TMSVLDELTADATA) break;
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

}

void TmsiAmplifier::stop_sampling() {
    if (fd < 0) return;
    fei.mode &= 0x01;
    printf("Sending stop message...\n");
    tms_write_frontendinfo(fd, &fei);
    sampling=false;
}

tms_channel_data_t * TmsiAmplifier::alloc_channel_data(bool vldelta = false) {
    int32_t i; /**< general index */
    int32_t ns_max = 1; /**< maximum number of samples of all channels */

    /* allocate storage space for all channels */
    tms_channel_data_t *channel_data = (tms_channel_data_t *) calloc(dev.NrOfChannels, sizeof (tms_channel_data_t));
    for (i = 0; i < dev.NrOfChannels; i++) {
        if (!vldelta) {
            channel_data[i].ns = 1;
        } else {
            channel_data[i].ns = (vli.TransFreqDiv + 1) / (vli.SampDiv[i] + 1);
        }
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

bool TmsiAmplifier::get_samples() {
    if (!sampling || fd < 0)
        return false;
    if (channel_data_index < channel_data[0].ns)
        return true;
    while (sampling) {
        receive();
        int type = tms_get_type(msg, br);
        if (tms_chk_msg(msg, br) != 0) {
            fprintf(stderr, "# checksum error !!!\n");
            if (type == TMSCHANNELDATA || type == TMSVLDELTADATA)
                return false;
            else
                continue;
        }
        if (type == TMSCHANNELDATA || type == TMSVLDELTADATA) {
            tms_get_data(msg, br, &dev, channel_data);
            channel_data_index = 0;
            debug("Channel data received...\n");
            if (--keep_alive==0)
            {
                keep_alive=sampling_rate*KEEP_ALIVE_RATE;
                debug("Sending keep_alive\n");
                tms_snd_keepalive(fd);
            }
            return true;
        }
    }
    return false;
}

int TmsiAmplifier::fill_samples(vector<int>& samples) {
    debug("Filling samples\n");
    if (!get_samples()) return -1;
    //printf("fill_samplse %d\n",sampling);
    if (sampling)
    {
        for (unsigned int i = 0; i < active_channels.size(); i++)
            samples[i] = channel_data[active_channels[i]].data[channel_data_index].isample;
    channel_data_index++;
    return active_channels.size();
    }
    return -1;
}

int TmsiAmplifier::fill_samples(vector<float>& samples) {
    if (!get_samples()) return -1;
    if (sampling){
        for (unsigned int i = 0; i < active_channels.size(); i++)
            samples[i] = channel_data[active_channels[i]].data[channel_data_index].sample;
    channel_data_index++;
    return active_channels.size();}
    return -1;
}

int TmsiAmplifier::get_digi() {
    if (channel_data == NULL) return 0;
    int tmp = channel_data[fei.nrofswchannels - 2].data[0].isample;
    for (int i = 1; i < channel_data[fei.nrofswchannels - 1].ns; i++)
        tmp |= channel_data[fei.nrofswchannels - 2].data[i].isample;
    return tmp;
}
void TmsiAmplifier::receive() {
    debug(">>>>>>>>>>>>>>>Receiving Message>>>>>>>>>>>>>>>\n");
    debug("flush %d",fflush(stderr));
    br = tms_rcv_msg(read_fd, msg, MESSAGE_SIZE);
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

int TmsiAmplifier::print_message(FILE * f) {
    int type = tms_get_type(msg, br);
    bool valid = tms_chk_msg(msg, br) == 0;
    fprintf(f, "Message length: %d, type: %x(%20s), valid: %s\n",
            br, type, get_type_name(type), valid ? "YES" : "NO");
    if (br < 2) return -1;
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
    int retry=0;
    while (br>0)
    {
        int type=tms_get_type(msg, br);
        if (type == TMSACKNOWLEDGE) {
            tms_get_ack(msg, br, &ack);
            tms_prt_ack(stderr, &ack);
            printf("Ack Received. Continuing emptying message buffer...\n");
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
    if (fd_dump!=-1)
        close(fd_dump);
}

