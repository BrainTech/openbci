/* 
 * File:   TmsiAmplifier.h
 * Author: Macias
 *
 * Created on 13 październik 2010, 13:14
 */

#ifndef TMSIAMPLIFIER_H
#define	TMSIAMPLIFIER_H
#include <string>
#include <vector>
#include <stdio.h>
#include <iostream>

#include "nexus/tmsi.h"
#include "AmplifierDriver.h"
#include "TmsiDriverDesc.h"
#include "AmplifierDescription.h"
#define BLUETOOTH_AMPLIFIER 1
#define USB_AMPLIFIER 2
#define IP_AMPLIFIER 3
#define MESSAGE_SIZE 1024*1024
#define CHAN_TYPE_DIG 4
#define KEEP_ALIVE_RATE 1 //seconds between every keep_alive message
#define MAX_ERRORS 10
#define MAX_ERRORS 10
using namespace std;
#undef debug
#ifdef AMP_DEBUG
#define debug(...) fprintf(stderr,__VA_ARGS__)
#define in_debug(...) __VA_ARGS__;
#else
#define debug(...) ;
#define in_debug(...) ;
#endif



class TmsiAmplifier : public AmplifierDriver {
private:
    int fd, read_fd, dump_fd; //device descriptor
    tms_frontendinfo_t fei;
    tms_vldelta_info_t vli;
    tms_input_device_t dev;
    tms_acknowledge_t ack;
    tms_rtc_t rtc;
    tms_channel_data_t *channel_data;
    uint8_t msg[MESSAGE_SIZE];
    int br; //actual msg length;
    int channel_data_index;
    int sample_rate_div;
    int keep_alive;
    int read_errors;
    uint mode;
public:
    TmsiAmplifier();
    uint get_digi(uint index);
    inline int get_sample_int(uint index){
    	return channel_data[index].data[channel_data_index].isample;
    }
    inline double get_sample_double(uint index){
    	return channel_data[index].data[channel_data_index].sample;
    }
    template <class T>
    inline void fill_sample(T* s,uint index){
    	_put_sample(s,index);
    }
    uint get_base_sample_rate(){
    	return fei.basesamplerate;
    }
    uint64_t next_samples();
    int number_of_channels() {
        return fei.nrofswchannels;
    }

    int set_sampling_rate(int sample_rate) {
    	vector<uint> s_r=description->get_sampling_rates();
    	bool ok=false;
    	for (uint i=0;i<s_r.size();i++)
    		if (s_r[i]==sample_rate) ok=true;
    	if (!ok)
    		{
    			cout <<"Sampling rate "<<sample_rate << " not available!";
    			return 0;
    		}
        int tmp = 0, bsr = fei.basesamplerate;
        while (tmp < 4 && abs(sample_rate - (bsr >> tmp)) > abs(sample_rate - (bsr >> (tmp + 1)))) tmp++;
        sample_rate_div = tmp;
        sampling_rate = bsr >> tmp;
        if (sample_rate > 128 && mode == BLUETOOTH_AMPLIFIER)
            sample_rate_div -= 1;
        return sampling_rate;
    }

    void set_sampling_rate_div(int sampling_rate_div) {
        sample_rate_div = sampling_rate_div;
        sampling_rate = fei.basesamplerate >> sample_rate_div;
    }

    int get_sampling_rate_div() {
        return sample_rate_div;
    }
    void start_sampling();
    void stop_sampling(bool disconnecting=false);
    int refreshInfo();
	boost::program_options::options_description get_options();
	void init(boost::program_options::variables_map &vm);
	void connect_device(uint type,const string &address);
    ~TmsiAmplifier();
private:
    inline void _put_sample(int *s, uint index) {
			(*s) = get_sample_int(index);
	}
	inline void _put_sample(double *s, uint index) {
			(*s) = get_sample_double(index);
	}
    int connect_usb(const string & address);
    int connect_bluetooth(const string &address);
    int connect_ip(const string &address);
    void read_from(const string &file);
    void dump_to(const string &file);
    int send_request(int type);
    bool update_info(int type);
    bool _refreshInfo(int type);
    tms_channel_data_t* alloc_channel_data(bool vldelta);

    void free_channel_data(tms_channel_data_t * &channel_data) {
        if (channel_data != NULL) {
            for (int i = 0; i < fei.nrofswchannels; i++)
                free(channel_data[i].data);
            free(channel_data);
            channel_data = NULL;
        }
    }

    void refreshFrontEndInfo() {
        while (!_refreshInfo(TMSFRONTENDINFO));
        set_sampling_rate_div(fei.currentsampleratesetting);
        sampling = true;
        stop_sampling();
    }

    void refreshIDData() {
        int counter = 20;
        while (counter--) {
            send_request(TMSIDDATA);
            if (update_info(TMSIDDATA)) break;
        }
//        tms_prt_iddata(stderr,&dev);
        set_description(new TmsiDriverDesc(dev,this));
        if (sampling_rate==0)
        	set_sampling_rate(description->get_sampling_rates()[0]);
    }

    void refreshVLDeltaInfo() {
        _refreshInfo(TMSVLDELTAINFO);
    }
    int _print_message(FILE *, uint8_t * msg, int br);

    int print_message(FILE * f) {
        return _print_message(f, msg, br);
    }

    int rcv_message(uint8_t *, int n);
    int fetch_iddata();
    void receive();
    const char * get_type_name(int type);
    void disconnect_mobita();
};
class DummyTmsiAmplifier: public AmplifierDriver{
public:
	DummyTmsiAmplifier():AmplifierDriver(){
		set_description(new DummyAmplifier(this));
	}
};
#endif	/* TMSIAMPLIFIER_H */

