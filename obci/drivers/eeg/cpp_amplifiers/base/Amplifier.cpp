#include "Amplifier.h"
#include <stdio.h>
using namespace std;
#include <boost/program_options.hpp>
#include <boost/bind.hpp>
#include <errno.h>
#include <time.h>
namespace po = boost::program_options;
vector<string> split_string(string str,char separator){
	uint i=0;
	vector<string> res;
	for (;;) {
		size_t j = str.find(separator, i);
		if (j == string::npos)
			break;
		res.push_back(str.substr(i, j - i));
		i = j + 1;
	}
	if (str.size()-i>0)
		res.push_back(str.substr(i));
	return res;
}
po::options_description Amplifier::get_options() {
	po::options_description options("Amplifier Options");
	options.add_options()
			("sampling_rate,s",	po::value<int>()->default_value(128)
					->notifier(boost::bind(&Amplifier::set_sampling_rate_, this,_1)),
					"Sampling rate to use")
			("active_channels,c",po::value<string>()->default_value("*")
					->notifier(boost::bind(&Amplifier::set_active_channels_string,this, _1)),
					"String with channel names or indexes separated by semicolons");

	return options;
}
void Amplifier::init(boost::program_options::variables_map &vm) {
//	set_sampling_rate(vm["sampling_rate"].as<int>());
//	set_active_channels_string(vm["channels"].as<string>());
}
Amplifier * Amplifier::signal_handler=NULL;
void Amplifier::setup_handler(){
	Amplifier::signal_handler = this;
	signal(SIGINT, &Amplifier::stop_sampling_handler);
}
void Amplifier::start_sampling() {
	sampling = true;
	cur_sample=0;
	setup_handler();
	logger.sampling=sampling_rate;
	logger.info()<<" Sampling started with sampling rate "
			<<sampling_rate<<"\nActive Channels: " << get_active_channels_string() <<"\n";
	sleep_res=get_sleep_resolution();
	double start=get_time();
	get_time_res=(get_time()-start)*2;
	logger.info()<<"Sleep resolution: "<<sleep_res<<" get_time resolution:"<<get_time_res <<"\n";
	sampling_start_time=last_sample=sample_timestamp=get_time();
}
void Amplifier::stop_sampling_handler(int sig) {
	signal(sig, SIG_DFL);
	fprintf(stderr, "Signal %d (%s) intercepted. Driver stopping\n", sig,
			strsignal(sig));
	Amplifier::signal_handler->stop_sampling(true);
}
double Amplifier::get_expected_sample_time(){
	return sampling_start_time+cur_sample/(double)sampling_rate;
}
double Amplifier::next_samples(bool synchronize) {
	cur_sample++;
	double expected = get_expected_sample_time();
	sample_timestamp=last_sample =get_time();
	if (!synchronize)
		return sample_timestamp;
	double diff,seconds;
	diff=expected-last_sample;
//	fprintf(stderr,"[%d] Cur:%f, Expected:%f, Diff:%f, Comp:%f",cur_sample, sample_timestamp, expected, diff,sampling_start_time+cur_sample/(float)sampling_rate); diff=expected-get_time();
//	if (diff<0){
//		fprintf(stderr,"is late by %f\n",-diff);
//	}
	if (diff>sleep_res){
		struct timespec slptm;
//		fprintf(stderr," sleep for %f s",diff);diff=expected-get_time();
		diff-=sleep_res;
		slptm.tv_nsec = modf(diff,&seconds)*1000000000;
		slptm.tv_sec = seconds;
//		if (diff>0)
		nanosleep(&slptm,NULL);
		last_sample=get_time();
	}
//	if (last_sample+get_time_res<expected){
//		fprintf(stderr,"active wait for %f; ",expected-last_sample);last_sample=get_time();
	while (last_sample+get_time_res<expected)
		last_sample=get_time();
//	}
//	double tmp=get_time();fprintf(stderr,"finished waiting at %f, should finish at %f, late by %f\n",tmp,expected,tmp-expected);
	sample_timestamp = expected;
	return sample_timestamp;
}
void Amplifier::set_active_channels(std::vector<std::string> &channels) {
	active_channels.clear();
	if (!description)
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
void Amplifier::set_active_channels_string(const string &channels) {
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

double Amplifier::get_sleep_resolution() {
	double start = get_time();
	struct timespec slptm;
	slptm.tv_nsec = 1;
	slptm.tv_sec = 0;
	nanosleep(&slptm, NULL);
	return get_time() - start;
}

Amplifier::Amplifier():logger(128, "AmplifierDriver") {
	description = NULL;
	sampling_rate = sampling_rate_ = 128;
	sleep_res = get_sleep_resolution();
}

void Amplifier::set_description(AmplifierDescription * description) {
	this->description = description;
	set_sampling_rate(sampling_rate_);
	set_active_channels_string(active_channels_str);
}
Amplifier::~Amplifier() {
	logger.info() << "Destructor\n";
	if (description)
		delete description;
	description = NULL;
}

void Amplifier::stop_sampling(bool disconnecting) {
	sampling = false;
	signal(SIGINT, SIG_DFL);
	signal(SIGTERM, SIG_DFL);
	logger.info() << "Sampling stopped" << (disconnecting ? " and disconnecting" : "") << "\n";
}

uint Amplifier::set_sampling_rate(const uint samp_rate) {
	return sampling_rate = samp_rate;
}
