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
	int saw;
	po::options_description options("Program Options");

	options.add_options()
			("length,l",po::value<int>(&length)->default_value(5),"Length of the test in seconds")
			("help,h","Show help")
			("start","Start sampling")
			("saw",po::value<int>(&saw)->default_value(0),"Set expected Saw difference. If set driver will monitor samples lost");
	options.add(amp->get_options());
	cout << options <<"\n";

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,options),vm);
	po::notify(vm);
	amp->init(vm);

	cout << amp->get_description()->get_json()<<"\n";
	int sample_rate = amp->get_sampling_rate();
	if (saw)
		amp->set_active_channels_string("Saw;Driver_Saw");
	vector<Channel *> channels = amp->get_active_channels();
	if (!vm.count("start"))
		return 0;
	amp->start_sampling();
	ptime start=microsec_clock::local_time();
	uint last_saw=0;
	printf("SAMPLING STARTED at %s  and will stop after %d (%d)samples\n",to_simple_string(start).c_str(),length*sample_rate,length);
	cout.precision(20);
	uint lost_samples=0;
	int i=0;
	while ((i++ < length * sample_rate) & amp->is_sampling()) {
		amp->next_samples();
		if (!saw) {
			printf("[%15s] S %d, timestamp: %.20f\n",
					to_simple_string(microsec_clock::local_time()).substr(12).c_str(),i,amp->get_sample_timestamp());
			for (uint j = 0; j < channels.size(); j++)
				printf("%12s: %f %x\n", channels[j]->name.c_str(),
						channels[j]->get_sample(),
						channels[j]->get_raw_sample());
		} else {
			uint new_saw = channels[0]->get_raw_sample();
			if (new_saw < last_saw) {
				printf(
						"[%15s] S %d: Saw Jump. Saw  %d ->%d",
						to_simple_string(microsec_clock::local_time()).substr(12).c_str(),
						channels[1]->get_raw_sample(), last_saw,new_saw);
				if (new_saw != 0)
					printf(" ERROR samples lost: %d\n", new_saw);
				else
					printf("\n");
				lost_samples += new_saw;
			} else if (last_saw + saw != new_saw) {
				printf(
						"[%15s] S %d: ERROR!!! %d Samples lost. Saw %d->%d\n",
						to_simple_string(microsec_clock::local_time()).substr(12).c_str(),
						channels[1]->get_raw_sample(), new_saw - saw - last_saw,
						last_saw,new_saw);
				lost_samples += new_saw - saw - last_saw;
			}						
			last_saw=new_saw;
		}
	}
	ptime end=microsec_clock::local_time();
	printf("Sampling will be stopped at %s after %d samples\n",
			to_simple_string(end).c_str(), i);
	printf("Duration: %s\n",to_simple_string(end-start).c_str());
	printf("Actual frequency: %f\n",i/(double)(end-start).total_microseconds()*1000000);
	printf("Lost samples: %d\n",lost_samples);

	amp->stop_sampling();
	return 0;

}
