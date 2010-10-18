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

#include "TmsiAmplifier.h"
#include "nexus/tmsi.h"
#define debug(...) fprintf(stderr,__VA_ARGS__)

TmsiAmplifier::TmsiAmplifier(const char * address, const char * r_address,int type) {
    sampling = false;
    dev.Channel = NULL;
    vli.SampDiv = NULL;
    channel_data = NULL;
    if (type == USB_AMPLIFIER)
        fd = connect_usb(address);
    else
        fd = connect_bluetooth(address);
    if (r_address!=NULL)
        read_fd=open(r_address,O_RDONLY);
    else
        read_fd=fd;
    debug("Descriptors: %d %d",fd,read_fd);
    if (fd > 0)
        refreshInfo();
    else
        perror("DEVICE OPEN ERROR");
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
    debug("Sending request for %s\n",get_type_name(type));
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
}

bool TmsiAmplifier::update_info(int type) {
    debug("Got type: %s",get_type_name(tms_get_type(msg,br)));
    if (tms_get_type(msg, br) != type)
    {
        debug(" expected type: %s\n",get_type_name(type));
        return false;
    }
    else
        debug("\n");
        
    switch (type) {
        case TMSFRONTENDINFO:
            return tms_get_frontendinfo(msg, br, &fei) != -1;
        case TMSIDDATA:
            return tms_get_iddata(msg, br, &dev) != 1;
        case TMSVLDELTAINFO:
            return tms_get_vldelta_info(msg, br, dev.NrOfChannels, &vli) != -1;
        case TMSRTCDATA:
            return tms_get_rtc(msg, br, &rtc) != -1;
        default:
            fprintf(stderr, "Wrong Info type\n");

    }
    return false;
}

void TmsiAmplifier::_refreshInfo(int type) {
    while (true) {
        send_request(type);
        if (br < 0 || tms_chk_msg(msg, br) != 0)
            fprintf(stderr, "Error while receiving message (%d)", br);
        else
            if (update_info(type)) break;
    }
}

void TmsiAmplifier::load_channel_desc() {
    channels_desc.clear();
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
    if (fd<0) return;
    fei.mode &= 0x10;
    fei.currentsampleratesetting = sample_rate_div;
    sampling = true;
    br = 0;
    while (!update_info(TMSACKNOWLEDGE)) {
        tms_write_frontendinfo(fd, &fei);
        receive();
        if (br < 0 || tms_chk_msg(msg, br) != 0) {
            fprintf(stderr, "Error while receiving message (%d)", br);
            br = 0;
        }
    }
    if (ack.errorcode != 0)
        tms_prt_ack(stderr, &ack);
}

void TmsiAmplifier::stop_sampling() {
    if (fd<0) return;
    if (!sampling) return;
    fei.mode &= 0x11;
    sampling = false;
    tms_write_frontendinfo(fd, &fei);
}

tms_channel_data_t * TmsiAmplifier::alloc_channel_data() {
    int32_t i; /**< general index */
    int32_t ns_max = 1; /**< maximum number of samples of all channels */

    /* allocate storage space for all channels */
    tms_channel_data_t *channel_data = (tms_channel_data_t *) calloc(dev.NrOfChannels, sizeof (tms_channel_data_t));
    for (i = 0; i < dev.NrOfChannels; i++) {
        //if (vli.==NULL) {
        //   chd[i].ns=1;
        // } else {
        channel_data[i].ns = (vli.TransFreqDiv + 1) / (vli.SampDiv[i] + 1);
        //}
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
    if (!sampling||fd<0)
        return false;
    if (channel_data_index < channel_data[0].ns)
        return true;
    receive();
    while (sampling) {
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
            return true;
        }
    }
    return false;
}

int TmsiAmplifier::fill_samples(vector<int>& samples) {
    if (!get_samples()) return -1;
    if (sampling)
        for (int i = 0; i < active_channels.size(); i++)
            samples[i] = channel_data[active_channels[i]].data[channel_data_index].isample;
    channel_data_index++;

}

int TmsiAmplifier::fill_samples(vector<float>& samples) {
    if (!get_samples()) return -1;
    if (sampling)
        for (int i = 0; i < active_channels.size(); i++)
            samples[i] = channel_data[active_channels[i]].data[channel_data_index].sample;
    channel_data_index++;
}

int TmsiAmplifier::get_digi() {
    if (channel_data == NULL) return 0;
    int tmp = channel_data[fei.nrofswchannels - 1].data[0].isample;
    for (int i = 1; i < channel_data[fei.nrofswchannels - 1].ns; i++)
        tmp |= channel_data[fei.nrofswchannels - 1].data[i].isample;
    return tmp;
}

void TmsiAmplifier::receive() {
    br = tms_rcv_msg(read_fd, msg, MESSAGE_SIZE);
    print_message(stderr);
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
    void TmsiAmplifier::print_message(FILE * f) {
        int type = tms_get_type(msg, br);
        fprintf(f, "Message length: %d, type: %x(%20s), valid: %s\n",
                br, type, get_type_name(type), tms_chk_msg(msg, br) == 0 ? "YES" : "NO");
        if (br < 2) return;
        fprintf(f, "%5s | %6s %6s | %5s | %6s %6s\n", "nr", "[nr]", "[nr+1]", "chars", "[nr+1]", "[nr]");

        for (int i = 0; i + 1 < br; i += 2) {
            fprintf(f, "%5d | %6d %6d | %2c %2c | %6x  %6x\n",
                    i, msg[i], msg[i + 1], isprint(msg[i]) ? msg[i] : '.',
                    isprint(msg[i + 1]) ? msg[i + 1] : '.', msg[i + 1], msg[i]);
        }
        if (tms_chk_msg(msg, br)) {
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
                    tms_get_iddata(msg, br, &idev);
                    tms_prt_iddata(f, &idev);
                    break;
                case TMSCHANNELDATA:
                case TMSVLDELTADATA:
                    tms_channel_data_t *chan = alloc_channel_data();
                    tms_get_data(msg, br, &dev, chan);
                    tms_prt_channel_data(f, &dev, chan, 0);
                    free_channel_data(chan);
                    break;
            }
        }
    }

    TmsiAmplifier::~TmsiAmplifier() {
        stop_sampling();
        while (tms_get_type(msg, br) != TMSACKNOWLEDGE) receive();
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
        if (read_fd!=fd)
            close(read_fd);
    }

    int main(int argc,char ** argv) {
        tms_frontendinfo_t fei;
        close(open("dump.amp",O_WRONLY|O_CREAT|O_TRUNC));
        //int fd = open(argv[0],O_WRONLY|O_APPEND|O_CREAT);
        //tms_write_frontendinfo(fd,&fei);
        //close(fd);
        if (argc<2)
        {printf("No device specified\n");
            return -1;
        }
        debug("Opening device: \"%s\"\n",argv[1]);
        char * read_f=NULL;
        if (argc>2)
            read_f=argv[2];
        TmsiAmplifier amp(argv[1],read_f);
        amp.set_sampling_rate_div(1);
        amp.start_sampling();
        for (int i = 0; i < 10; i++) {
            vector<int> isamples(amp.number_of_channels(), 0);
            vector<float> fsamples(amp.number_of_channels(), 0.0);
            amp.fill_samples(isamples);
            printf("Integer samples form channels:\n");
            for (int j = 0; j < isamples.size(); j++)
                printf("%3d: %d\n", j, isamples[j]);
            amp.fill_samples(fsamples);
            printf("Float samples form channels:\n");
            for (int j = 0; j < fsamples.size(); j++)
                printf("%3d: %f\n", j, fsamples[j]);
        }
        amp.stop_sampling();
    }
