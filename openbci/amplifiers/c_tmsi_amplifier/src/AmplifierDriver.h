/* 
 * File:   AmplifierDriver.h
 * Author: Macias
 *
 * Created on 14 październik 2010, 16:25
 */

#ifndef AMPLIFIERDRIVER_H
#define	AMPLIFIERDRIVER_H
#include <vector>
#include <string>
#include <stdlib.h>
#include <stdint.h>

class AmplifierDriver
{
protected:
    bool sampling;
    int sampling_rate;
    std::vector<std::string> active_channels;
    uint64_t last_sample;
public:
    AmplifierDriver(){};
    virtual void start_sampling();
    
    virtual void stop_sampling()
    {
        sampling=false;
    }
    virtual int fill_samples(std::vector<int> &samples)
    {   if (!sampling) return -1;
        for (unsigned int i=0;i<active_channels.size();i++)
	  samples[i]=rand() % 100;
    synchronize();
    return active_channels.size();
    }
    virtual int fill_samples(std::vector<float> &samples)
    {   if (!sampling) return -1;
        for (unsigned int i=0;i<active_channels.size();i++)
	  samples[i]=(float) (rand() % 100);///RAND_MAX;
    synchronize();
    return active_channels.size();
    }
    virtual void set_active_channels(std::vector<std::string> &channels)
    {
        active_channels = channels;
    }
    inline bool is_sampling(){return sampling;}
    virtual int set_sampling_rate(int samp_rate)
    {
        return sampling_rate=samp_rate;
    }
    virtual int get_sampling_rate()
    {return sampling_rate;}
private:
    void synchronize();
};



#endif	/* AMPLIFIERDRIVER_H */

