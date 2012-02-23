#include "AmplifierDriver.h"
#include <stdio.h>
using namespace std;
#include <boost/program_options.hpp>
#include <boost/bind.hpp>
#include <errno.h>
#include <time.h>
namespace po = boost::program_options;

po::options_description AmplifierDriver::get_options() {
	po::options_description options("Amplifier Options");
	options.add_options()
			("sampling_rate,s",	po::value<int>()
					->notifier(boost::bind(&AmplifierDriver::set_sampling_rate_, this,_1)),
					"Sampling rate to use")
			("active_channels,c",po::value<string>()->default_value("*")
					->notifier(boost::bind(&AmplifierDriver::set_active_channels_string,this, _1)),
					"String with channel names or indexes separated by semicolons");

	return options;
}
void AmplifierDriver::init(boost::program_options::variables_map &vm) {
//	set_sampling_rate(vm["sampling_rate"].as<int>());
//	set_active_channels_string(vm["channels"].as<string>());
}
AmplifierDriver * AmplifierDriver::signal_handler=NULL;
void AmplifierDriver::setup_handler(){
	AmplifierDriver::signal_handler = this;
	signal(SIGINT, &AmplifierDriver::stop_sampling_handler);
}
void AmplifierDriver::start_sampling() {
	sampling = true;
	cur_sample=-1;
	setup_handler();
	logger.sampling=sampling_rate;
	logger.info()<<" Sampling started with sampling rate "
			<<sampling_rate<<"\nActive Channels: " << get_active_channels_string() <<"\n";
	sleep_res=get_sleep_resolution();
	double start=get_time();
	get_time_res=(get_time()-start)*2;
	logger.info()<<"Sleep resolution: "<<sleep_res<<" get_time resolution:"<<get_time_res <<"\n";
	sampling_start_time=last_sample =get_time();
}
void AmplifierDriver::stop_sampling_handler(int sig) {
	signal(sig, SIG_DFL);
	fprintf(stderr, "Signal %d (%s) intercepted. Driver stopping\n", sig,
			strsignal(sig));
	AmplifierDriver::signal_handler->stop_sampling(true);
}
double AmplifierDriver::next_samples() {
	cur_sample++;
	double wait = last_sample + 1.0 / sampling_rate;
	double diff,seconds;
	last_sample =get_time();
	diff=wait-last_sample;
//	fprintf(stderr,"Sample %d, Computed timestamp: %f, relative to previous:%f,current timestamp %f; sleep_res:%f;",cur_sample,sampling_start_time+cur_sample/(float)sampling_rate,wait,last_sample,sleep_res); diff=wait-get_time();
	if (diff<0){
//fprintf(stderr,"is late by %f\n",-diff);
		return last_sample;
	}
	if (diff>sleep_res){
		struct timespec slptm;
//		fprintf(stderr," sleep for %f s",diff);diff=wait-get_time();
		diff-=sleep_res;
		slptm.tv_nsec = modf(diff,&seconds)*1000000000;
		slptm.tv_sec = seconds;
//		if (diff>0)
			nanosleep(&slptm,NULL);
		last_sample=get_time();
	}
	//if (last_sample+get_time_res<wait){
		//fprintf(stderr,"active wait for %f; ",wait-last_sample);last_sample=get_time();
		while (last_sample+get_time_res<wait)
			last_sample=get_time();
//	}
//	double tmp=get_time();
//	fprintf(stderr,"finished waiting at %f, should finish at %f, late by %f\n",tmp,wait,tmp-wait);
	last_sample = wait;
	return last_sample;
}
void AmplifierDriver::set_active_channels(std::vector<std::string> &channels) {
	active_channels.clear();
	if (!description)0.00
		return;
	for (uint i = 0; i < channels.size(); i++) {
		if (channels[i] == "*") {
			active_channels = description->get_channels();
			return;
		}
		Channel* chan = description->find_channel(channels[i]);
		if (!chan)
			throw NoSuchChannel(channels[i]);
		else
			active_channels.push_back(chan);
	}
}
void AmplifierDriver::set_active_channels_string(const string &channels) {
	if (!description)
	{
		active_channels_str=channels;
		return;
	}
	else
		if (get_active_channels_string()==channels)
			return;
	vector<string> names;
	uint i = 0;
	for (;;) {
		uint64_t j = channels.find(';', i);
		if (j == string::npos)
			break;
		names.push_back(channels.substr(i, j - i));
		i = j + 1;
	}
	names.push_back(channels.substr(i));
	set_active_channels(names);
	logger.info()<<"Active channels: "<<get_active_channels_string() << "\n";
}
