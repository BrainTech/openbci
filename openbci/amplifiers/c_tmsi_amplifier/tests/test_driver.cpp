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
#include "TmsiAmplifier.h"
#include <fcntl.h>

int main(int argc, char ** argv) {
    tms_frontendinfo_t fei;
    close(open("dump.amp", O_WRONLY | O_CREAT | O_TRUNC));
    //int fd = open(argv[0],O_WRONLY|O_APPEND|O_CREAT);
    //tms_write_frontendinfo(fd,&fei);
    //close(fd);
    if (argc < 2) {
        printf("No device specified\n");
        return -1;
    }
    debug("Opening device: \"%s\"\n", argv[1]);
    debug("Time %d", time(NULL));
    char * read_f = NULL;
    if (argc > 2)
        read_f = argv[2];
    TmsiAmplifier amp(argv[1], USB_AMPLIFIER,read_f);
    amp.set_sampling_rate_div(0);
    vector<int> channels;
    for (int i = 0; i < 3; i++) channels.push_back(i);
    channels.push_back(32);
    amp.set_active_channels(channels);
    amp.start_sampling();

    debug("SAMPLING STARTED\n");
    for (int i = 0; i < 1000; i++) {
        vector<int> isamples(amp.number_of_channels(), 0);
        vector<float> fsamples(amp.number_of_channels(), 0.0);
        amp.fill_samples(isamples);
        printf("Integer samples form channels:\n");
        for (int j = 0; j < channels.size(); j++)
            printf("%3d: %d %x\n", channels[j], isamples[channels[j]], isamples[channels[j]]);
        //            amp.fill_samples(fsamples);
        //            printf("Float samples form channels:\n");
        //            for (int j = 0; j < fsamples.size(); j++)
        //                printf("%3d: %f\n", j, fsamples[j]);
    }
    amp.stop_sampling();
    printf("Sampling stopped\n");
}
