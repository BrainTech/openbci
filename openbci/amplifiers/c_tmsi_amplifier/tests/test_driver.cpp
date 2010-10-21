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
#include <fcntl.h>
#include <stdio.h>
#include <signal.h>
using namespace boost::posix_time;

int main(int argc, char ** argv) {
    tms_frontendinfo_t fei;
    
    char *dev="/dev/fusbi0", *read_dev=NULL,*dump_file=NULL;
    int sample_rate=128,length=5;
    int mode=USB_AMPLIFIER;
    for (int i=1;i<argc;i++)
        if (argv[i][0]=='-')
            switch (argv[i][1])
            {
                case 'd':
                    dev=argv[i+1]; break;
                case 'r':
                    read_dev=argv[i+1]; break;
                case 'f':
                    sample_rate=atoi(argv[i+1]);break;
                case 'b':
                    mode = BLUETOOTH_AMPLIFIER;break;
                case 'l':
                    length=atoi(argv[i+1]);break;
                case 'a':
                    dump_file=argv[i+1];

            }
    TmsiAmplifier amp(dev, mode,read_dev,dump_file);
    sample_rate=amp.set_sampling_rate(sample_rate);
    printf("Sampling rate: %d Hz\n",sample_rate);
    vector<int> channels;
    for (int i = 0; i < 3; i++) channels.push_back(i);
    channels.push_back(3);
    channels.push_back(32);
    amp.set_active_channels(channels);
    amp.start_sampling();
    ptime start=microsec_clock::local_time();
    printf("SAMPLING STARTED at %s\n",to_simple_string(start).c_str());
    for (int i = 0; i < length*sample_rate; i++) {
        vector<int> isamples(amp.number_of_channels(), 0);
        //vector<float> fsamples(amp.number_of_channels(), 0.0);
        amp.fill_samples(isamples);
        printf("Samples %d:\n",i);
        for (int j = 0; j < channels.size(); j++)
            printf("%3d: %d %x\n", channels[j], isamples[j], isamples[j]);
        //            amp.fill_samples(fsamples);
        //            printf("Float samples form channels:\n");
        //            for (int j = 0; j < fsamples.size(); j++)
        //                printf("%3d: %f\n", j, fsamples[j]);
    }
    ptime end=microsec_clock::local_time();
    amp.stop_sampling();
    printf("Sampling stopped at %s after %d samples\n",
            to_simple_string(end).c_str(), length*sample_rate);
    printf("Duration: %s\n",to_simple_string(end-start).c_str());
    printf("Actual frequency: %f\n",length*sample_rate/(double)(end-start).total_microseconds()*1000000);
    return 0;
}
