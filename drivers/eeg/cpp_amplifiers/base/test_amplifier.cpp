/* 
 * File:   test_driver.cpp
 * Author: Macias
 *
 * Created on 2010-10-19, 16:06:44
 */

#include <stdlib.h>
#define __STDC_LIMIT_MACROS
#include <stdint.h>
#include <iostream>

/*
 * Simple C++ Test Suite
 */
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/program_options.hpp>
#include "test_amplifier.h"
using namespace boost::posix_time;
using namespace std;
namespace po=boost::program_options;

int _test_driver(int argc, char ** argv, Amplifier *amp){
	int length;
	int saw;
	double time_diff;
	Channel * ampSaw,*driverSaw;
	po::options_description options("Program Options");

	options.add_options()
			("length,l",po::value<int>(&length)->default_value(5),"Length of the test in seconds")
			("help,h","Show help")
			("start","Start sampling")
			("saw",po::value<int>(&saw)->default_value(0),"Set expected Saw difference. If set driver will monitor samples lost")
			("time",po::value<double>(&time_diff)->default_value(0.0),"Monitor time difference. Display error, when difference between expected timestamps is bigger then give value");
	options.add(amp->get_options());
	cout << options <<"\n";

	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,options),vm);
	po::notify(vm);
	amp->init(vm);

	cout << amp->get_description()->get_json()<<"\n";
	int sample_rate = amp->get_sampling_rate();
	ampSaw=amp->get_description()->find_channel("Saw");
	driverSaw=amp->get_description()->find_channel("Driver_Saw");
	vector<Channel *> channels = amp->get_active_channels();
	int last_saw=-1;

	if (!vm.count("start"))
		return 0;
	if (saw){
		if (!ampSaw || !driverSaw){
			cerr<< "Driver has no 'Saw' or 'DriverSaw' channel which are required for 'saw' option";
			return -1;
		}
	}
	amp->start_sampling();
	ptime start=microsec_clock::local_time();
	double start_time=amp->get_sample_timestamp();

	printf("SAMPLING STARTED at %s  and will stop after %d (%d)samples\n",to_simple_string(start).c_str(),length*sample_rate,length);
	cout.precision(3);
	uint lost_samples=0;
	int i=0;
	double last_sample_time=amp->get_sample_timestamp();
	double stop_time;
	uint saw_jump=1<<31;
	while ((i < length * sample_rate) & amp->is_sampling()) {
		double cur_sample=amp->next_samples();
		if (!amp->is_sampling()) break;
		if (channels.size()>0){
			printf("[%15s] S %d, timestamp: %.20f\n",
					to_simple_string(microsec_clock::local_time()).substr(12).c_str(),i,cur_sample);
			for (uint j = 0; j < channels.size(); j++)
				printf("%12s: %f %x\n", channels[j]->name.c_str(),
						channels[j]->get_sample(),
						channels[j]->get_raw_sample());
		}
		if (saw) {
			int new_saw = ampSaw->get_raw_sample();
			if (last_saw!=-1 && new_saw < last_saw && saw_jump==1<<31)
				{
					while ((saw_jump>>1)>last_saw) saw_jump=saw_jump>>1;
					printf(
							"[%15s] S %d: Saw Jump set to: %d. Saw  %d ->%d\n",
							to_simple_string(microsec_clock::local_time()).substr(12).c_str(),
							 driverSaw->get_raw_sample(),saw_jump, last_saw,new_saw);
				}
			if (last_saw>=0 && (last_saw + saw)%saw_jump != new_saw) {
				int lost;
				if (new_saw<last_saw)
					lost = (saw_jump-last_saw+new_saw)/saw -1;
				else
					lost = (new_saw-last_saw)/saw -1;
				printf(
						"[%15s] S %d: ERROR!!! At least %d Samples lost. Saw %d->%d (jump %d)\n",
						to_simple_string(microsec_clock::local_time()).substr(12).c_str(),
						driverSaw->get_raw_sample(), lost, last_saw,new_saw, saw_jump);
				lost_samples += lost;
			}						
			last_saw=new_saw;
		}
		if (time_diff>0){
			double expected_sample=last_sample_time+1.0/amp->get_sampling_rate();
			if (abs(expected_sample-cur_sample)>time_diff)
				printf("[%15s] S %d: ERROR!!! Has different timestamp than expected: (exp: %.4f,got: %.4f,diff: %.4f)\n",
						to_simple_string(microsec_clock::local_time()).substr(12).c_str(),i,expected_sample-start_time,cur_sample-start_time,cur_sample-expected_sample);

		}
		last_sample_time=cur_sample;
		stop_time=get_time_as_double();
		i++;
	}
	ptime end=microsec_clock::local_time();
	printf("Sampling will be stopped at %s after %d samples\n",
			to_simple_string(end).c_str(), i);
	printf("Duration: %s\n",to_simple_string(end-start).c_str());
	printf("First TS: %f,last TS: %f, computed_frequency: %f\n",start_time,last_sample_time,i/(last_sample_time-start_time));
	printf("Actual frequency: %f\n",i/(stop_time-start_time));
	printf("Lost samples: %d\n",lost_samples);

	amp->stop_sampling();
	return 0;

}
int test_driver(int argc, char ** argv, Amplifier *amp){
	try{
		_test_driver(argc,argv,amp);
		return 0;
	}
	catch (char const* msg){
		cerr<< "Amplifier exception: "<<msg<<"\n";
	}
	catch (exception * ex){
		cerr << "Amplifier exception: "<<ex->what()<<"\n";
	}
	return -1;
}
