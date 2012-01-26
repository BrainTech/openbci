/* 
 * File:   test_driver.cpp
 * Author: Macias
 *
 * Created on 2010-10-19, 16:06:44
 */

#include <stdlib.h>
#include <iostream>

/*
 * Simple C++ Test Suite
 */
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/program_options.hpp>
#include "../AmplifierDriver.h"
using namespace boost::posix_time;
using namespace std;
namespace po=boost::program_options;

int test_driver(int argc, char ** argv, AmplifierDriver *amp){
	int length;
	po::options_description options("Program Options");
	options.add_options()
			("length,l",po::value<int>(&length)->default_value(5),"Length of the test in seconds")
			("help,h","Show help")
			("start","Start sampling");
	options.add(amp->get_options());
	cout << options <<"\n";

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,options),vm);
	po::notify(vm);
	amp->init(vm);

	cout << amp->get_description()->get_json()<<"\n";
	int sample_rate = amp->get_sampling_rate();

	vector<Channel *> channels = amp->get_active_channels();
	if (!vm.count("start"))
		return 0;
	amp->start_sampling();
	ptime start=microsec_clock::local_time();
	printf("SAMPLING STARTED at %s  and will stop after %d (%d)samples\n",to_simple_string(start).c_str(),length*sample_rate,length);
	for (int i = 0; (i < length*sample_rate) & amp->is_sampling(); i++) {
		amp->next_samples();
		cout.precision(20);
		cout << "Samples "<<i<<" timestamp:"<<amp->get_sample_timestamp()<<"\n";
		for (uint j = 0; j < channels.size(); j++)
			{
				printf("%7s: %f %x\n", channels[j]->name.c_str(), channels[j]->get_sample(),channels[j]->get_raw_sample());
			}
	}
	ptime end=microsec_clock::local_time();
	printf("Sampling will be stopped at %s after %d samples\n",
			to_simple_string(end).c_str(), length*sample_rate);
	printf("Duration: %s\n",to_simple_string(end-start).c_str());
	printf("Actual frequency: %f\n",length*sample_rate/(double)(end-start).total_microseconds()*1000000);
	amp->stop_sampling();
	return 0;

}
