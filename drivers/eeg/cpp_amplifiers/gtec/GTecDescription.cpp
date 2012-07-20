/*
 * GTecDescription.cpp
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#include "GTecDescription.h"
#include "gAPI.h"
#include "Amplifier.h"

GTecDescription::GTecDescription(string name,Amplifier *driver,uint device_index):AmplifierDescription(name,driver) {
	uint s_r[]={32, 64, 128, 256, 512, 600,	1200, 2400, 4800, 9600, 19200, 38400};
	for (uint i=0;i<12;i++)
		sampling_rates.push_back(s_r[i]);
	vector<string> device = split_string(name,':');
	this->name = device[0];
	vector<string> gains = split_string(device[1],';');
	vector<string> offsets = split_string(device[2],';');
	for (uint i=0;i<GT_USBAMP_NUM_ANALOG_IN;i++)
	add_channel(new GTecChannel(i,atof(gains[i].c_str()),atof(offsets[i].c_str()),driver));
	this->get_channels()[GT_USBAMP_NUM_ANALOG_IN-1]->name = "Saw";
	add_channel(new SawChannel(driver));
	this->device_index = device_index;
}

GTecDescription::~GTecDescription() {
}

