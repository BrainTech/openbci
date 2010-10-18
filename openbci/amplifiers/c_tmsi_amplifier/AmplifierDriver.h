/* 
 * File:   AmplifierDriver.h
 * Author: Macias
 *
 * Created on 14 październik 2010, 16:25
 */

#ifndef AMPLIFIERDRIVER_H
#define	AMPLIFIERDRIVER_H
#include <vector>
#include <stdlib.h>
using namespace std;
class AmplifierDriver
{
protected:
    bool sampling;
    int sampling_rate;
    vector<int> active_channels;
public:
    AmplifierDriver(){};
    void start_sampling()
    {
        sampling=true;
    }
    void stop_sampling()
    {
        sampling=false;
    }
    int fill_samples(vector<int> &samples)
    {   if (!sampling) return -1;
        for (int i=0;i<active_channels.size();i++)
            samples[i]=rand();
    }
    int fill_samples(vector<float> &samples)
    {   if (!sampling) return -1;
        for (int i=0;i<active_channels.size();i++)
            samples[i]=((float)rand())/RAND_MAX;
    }
    void set_active_channels(vector<int> &channels)
    {
        active_channels = channels;
    }
    inline bool is_sampling(){return sampling;}
    int set_sampling_rate(int samp_rate)
    {
        return sampling_rate=samp_rate;
    }
    int get_sampling_rate()
    {return sampling_rate;}
};



#endif	/* AMPLIFIERDRIVER_H */

