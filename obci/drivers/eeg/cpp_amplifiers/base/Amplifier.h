/* 
 * File:   Amplifier.h
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
#include <sys/timeb.h>
#include <time.h>
vector<string> split_string(string str,char separator);
inline double get_time_as_double(){
	struct timeval tv;
	struct timezone tz;
	gettimeofday(&tv,&tz);
	return tv.tv_sec+tv.tv_usec/1000000.0;
}
class Amplifier {
private:
	double sleep_res;
	double get_time_res;
	double get_sleep_resolution();
protected:
	bool sampling;
	uint sampling_rate,sampling_rate_;
	string active_channels_str;
	std::vector<Channel *> active_channels;
	double last_sample;
	double sample_timestamp;
	double sampling_start_time;
	AmplifierDescription * description;
	static Amplifier * signal_handler;

	inline double get_time(){
		return get_time_as_double();
	}
	virtual double get_expected_sample_time();
public:
	Logger logger;
	uint cur_sample;
	Amplifier();

	void set_description(AmplifierDescription * description);
	virtual ~Amplifier();
	void setup_handler();
	virtual void start_sampling();

	virtual void stop_sampling(bool disconnecting=false);
	static void stop_sampling_handler(int signal);
	template <class T>
	int fill_samples(vector<T> &samples,bool adjusted=false){
		if (!sampling) return -1;
		if (!adjusted)
			for (uint i = 0; i < active_channels.size(); i++)
				samples[i]=active_channels[i]->get_sample();
		else
			for (uint i = 0; i < active_channels.size(); i++)
				samples[i]=active_channels[i]->get_adjusted_sample();
		return active_channels.size();
	}
	void set_active_channels(std::vector<std::string> &channels);
	void set_active_channels_string(const string &channels);
	inline bool is_sampling() {
		return sampling;
	}

	virtual uint set_sampling_rate(const uint samp_rate);
	inline void set_sampling_rate_(const uint samp_rate){
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
	virtual double next_samples(bool synchronize=true);
	inline double get_sample_timestamp(){
		return sample_timestamp;
	}
};


#endif	/* AMPLIFIERDRIVER_H */

