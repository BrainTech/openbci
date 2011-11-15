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
#include "../TmsiAmplifier.h"
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/program_options.hpp>
using namespace boost::posix_time;
namespace po=boost::program_options;
#include <fcntl.h>
#include <stdio.h>
#include <signal.h>


int main(int argc, char ** argv) {
    int sample_rate=128,length=5;
    po::options_description options("Program Options");
    options.add_options()
    		("length,l",po::value<int>(&length)->default_value(5),"Length of the test in seconds")
    		("help,h","Show help")
    		("start","Start sampling");
    TmsiAmplifier amp;
    options.add(amp.get_options());
    po::variables_map vm;
    po::store(po::parse_command_line(argc,argv,options),vm);
    po::notify(vm);
    amp.init(vm);
    if (vm.count("help"))
        	cout<<options<<"\n";

    cout << amp.get_description()->get_json()<<"\n";
    sample_rate = amp.get_sampling_rate();

    vector<Channel *> channels = amp.get_active_channels();
    if (!vm.count("start"))
    	return 0;
    amp.start_sampling();
    ptime start=microsec_clock::local_time();
    printf("SAMPLING STARTED at %s  and will stop after %d (%d)samples\n",to_simple_string(start).c_str(),length*sample_rate,length);
    for (int i = 0; i < length*sample_rate; i++) {
    	amp.next_samples();
        printf("Samples %d:\n",i);
        for (uint j = 0; j < channels.size(); j++)
        	{
        		channels[j]->get_sample_int();
        		printf("%7s: %d %x\n", channels[j]->name.c_str(), channels[j]->get_sample_int(),channels[j]->get_sample_int());
        	}
    }
    ptime end=microsec_clock::local_time();
    printf("Sampling will be stopped at %s after %d samples\n",
            to_simple_string(end).c_str(), length*sample_rate);
    printf("Duration: %s\n",to_simple_string(end-start).c_str());
    printf("Actual frequency: %f\n",length*sample_rate/(double)(end-start).total_microseconds()*1000000);
    amp.stop_sampling();
    return 0;
}
