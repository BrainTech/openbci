/* 
 * File:   AmplifierDriver.h
 * Author: Macias
 *
 * Created on 14 październik 2010, 16:25
 */

#ifndef AMPLIFIERDRIVER_H
#define	AMPLIFIERDRIVER_H
#include <vector>
#include <string>
#include <sstream>
#include <stdlib.h>
#include <stdint.h>
#include <iostream>
#include <signal.h>
#include "AmplifierDescription.h"
#include "Logger.h"
using namespace std;
#include <boost/program_options.hpp>

class AmplifierDriver {
protected:
	bool sampling;

	int sampling_rate,sampling_rate_;
	string active_channels_str;
	std::vector<Channel *> active_channels;
	uint64_t last_sample;
	AmplifierDescription * description;
	static AmplifierDriver * signal_handler;
	Logger logger;
	template <class T>
	int _fill_samples(vector<T> &samples) {
		if (!sampling)
			return -1;
		for (uint i = 0; i < active_channels.size(); i++)
			active_channels[i]->fill_sample(&samples[i]);

		return active_channels.size();
	}
public:
	uint cur_sample;
	AmplifierDriver():logger(128,"AmplifierDriver"){
		description=NULL;
		sampling_rate=sampling_rate_=128;
	}

	void set_description(AmplifierDescription * description){
		this->description=description;
		set_sampling_rate(sampling_rate_);
		set_active_channels_string(active_channels_str);
	}
	virtual ~AmplifierDriver() {
		if (description)
			delete description;
	}
	void setup_handler();
	virtual void start_sampling();

	virtual void stop_sampling(bool disconnecting=false) {
		sampling = false;
		signal(SIGINT,SIG_DFL);
		signal(SIGTERM,SIG_DFL);
		logger.info()<<"Sampling stopped"<< (disconnecting?" and disconnecting":"")<<"\n";
	}
	static void stop_sampling_handler(int signal);
	virtual int fill_samples(vector<int> &samples){
		return _fill_samples(samples);
	}
	void set_active_channels(std::vector<std::string> &channels);
	void set_active_channels_string(const string &channels);
	inline bool is_sampling() {
		return sampling;
	}

	virtual int set_sampling_rate(const int samp_rate) {
		return sampling_rate = samp_rate;
	}
	inline void set_sampling_rate_(const int samp_rate){
		if (!description)
		{
			sampling_rate_=samp_rate;
			return;
		}
		set_sampling_rate(samp_rate);
		logger.info() << "Current Sampling rate:" << get_sampling_rate() << "\n";
	}

	inline int get_sampling_rate() {
		return sampling_rate;
	}

	inline AmplifierDescription* get_description() {
		return description;
	}
	inline const vector<Channel *> &get_active_channels(){
		return active_channels;
	}
	inline string get_active_channels_string(){
		ostringstream out;
		for (uint i=0;i<active_channels.size();i++)
			out <<(i?",":"")<<active_channels[i]->name;
		return out.str();
	}
	virtual boost::program_options::options_description get_options();
	virtual void init(boost::program_options::variables_map &vm);
	virtual uint64_t next_samples();
	inline double get_sample_timestamp(){
		return last_sample/1000000.0;
	}
};
class DummyAmplifier:public AmplifierDescription{
public:
	DummyAmplifier(AmplifierDriver *driver):AmplifierDescription("Dummy Amplifier",driver){
		add_channel(new Channel("temp1"));
		add_channel(new Channel("temp2"));
		add_channel(new SawChannel(this));
		add_channel(new BoolChannel("Trigger",this));
	}
};


#endif	/* AMPLIFIERDRIVER_H */

