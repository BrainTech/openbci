/*
 * TmsiAmplifierDesc.cpp
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */
#include <iostream>
#include "TmsiAmplifierDesc.h"
#include "TmsiAmplifier.h"

TmsiAmplifierDesc::TmsiAmplifierDesc(tms_input_device_t &dev,TmsiAmplifier *amp):AmplifierDescription(dev.DeviceDescription,amp){
	for (int i = 0; i < dev.NrOfChannels; i++) {
		Channel * channel;
		if (dev.Channel[i].Type.Type==DIGI_CHANNEL){
			channel=new DigiChannel(dev.Channel[i],amp,i);
			digi_channels.push_back(channel);
		}
		else
			channel=new TmsiChannel(dev.Channel[i],amp,i);
		add_channel(channel);
	}
	physical_channels=dev.NrOfChannels;
	add_channel(new SawChannel(amp));
	add_channel(new TriggerChannel(this));
	add_channel(new OnOffChannel(this));
	add_channel(new BatteryChannel(this));
	uint base_sampling_rate=amp->get_base_sample_rate();
	while (base_sampling_rate>64){
		sampling_rates.insert(sampling_rates.begin(),base_sampling_rate);
		base_sampling_rate=base_sampling_rate>>1;
	}
}
