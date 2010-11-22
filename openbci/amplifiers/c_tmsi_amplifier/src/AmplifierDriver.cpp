#include "AmplifierDriver.h"
#include <boost/date_time/posix_time/ptime.hpp>
#include <stdio.h>
#include <boost/date_time/posix_time/posix_time_types.hpp>
using namespace std;
using namespace boost::posix_time;
void AmplifierDriver::start_sampling()
    {
        sampling=true;
        last_sample=boost::posix_time::microsec_clock::local_time().time_of_day().total_microseconds();
    }
void AmplifierDriver::synchronize()
    {
        uint64_t wait=(last_sample+1000000/sampling_rate);
        uint64_t this_sample=0;
        int counter=0;
        while (this_sample<wait)
        {
            this_sample=boost::posix_time::microsec_clock::local_time().time_of_day().total_microseconds();
            if (++counter%(1000000/sampling_rate)==0)
                printf("Waiting %lld-%lld\n",wait,this_sample);
        }


    last_sample=this_sample;
    }
