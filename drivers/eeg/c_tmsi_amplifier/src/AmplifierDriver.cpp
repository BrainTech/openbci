#include "AmplifierDriver.h"
#include <stdio.h>
using namespace std;
#include <boost/date_time/posix_time/ptime.hpp>
#include <boost/date_time/posix_time/posix_time_types.hpp>
#include <boost/program_options.hpp>
#include <boost/bind.hpp>
#include <errno.h>
#include <time.h>
namespace po = boost::program_options;
using namespace boost::posix_time;

po::options_description AmplifierDriver::get_options() {
	po::options_description options("Amplifier Options");
	options.add_options()
			("sampling_rate,s",	po::value<int>()
					->notifier(boost::bind(&AmplifierDriver::set_sampling_rate_, this,_1)),
					"Sampling rate to use")
			("active_channels,c",po::value<string>()->default_value("*")->
						notifier(boost::bind(&AmplifierDriver::set_active_channels_string,this, _1)),
						"String with channel names or indexes separated by commas");

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
	last_sample =boost::posix_time::microsec_clock::local_time().time_of_day().total_microseconds();
}
void AmplifierDriver::stop_sampling_handler(int sig) {
	signal(sig, SIG_DFL);
	fprintf(stderr, "Signal %d (%s) intercepted. Driver stopping\n", sig,
			strsignal(sig));
	AmplifierDriver::signal_handler->stop_sampling(true);
}
uint64_t AmplifierDriver::next_samples() {
	uint64_t wait = last_sample + 1000000 / sampling_rate;
//	uint64_t this_sample = 0;
	last_sample =get_time();
	cur_sample++;
	if (last_sample>wait)
		return last_sample;
	struct timespec slptm;
	slptm.tv_sec = 0;
	slptm.tv_nsec = (wait-last_sample-500)*1000;      //1000 ns = 1 us
	if (slptm.tv_nsec>0)
		nanosleep(&slptm,NULL);
//	this_sample =boost::posix_time::microsec_clock::local_time().time_of_day().total_microseconds();
//	printf(" realwait %lld-%lld, should wait %lld\n",this_sample,this_sample-last_sample,wait-last_sample);
	last_sample = wait;
	return last_sample;
}
void AmplifierDriver::set_active_channels(std::vector<std::string> &channels) {
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
