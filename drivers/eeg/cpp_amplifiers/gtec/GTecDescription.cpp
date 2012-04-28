/*
 * GTecDescription.cpp
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#include "GTecDescription.h"
#include "gAPI.h"

GTecDescription::GTecDescription(string name,Amplifier *driver):AmplifierDescription(name,driver) {
	uint s_r[]={32, 64, 128, 256, 512, 600,	1200, 2400, 4800, 9600, 19200, 38400};
	for (uint i=0;i<12;i++)
		sampling_rates.push_back(s_r[i]);
	gt_usbamp_channel_calibration calib;
//	GT_Calibrate(name.c_str(),&calib);
	for (uint i=0;i<GT_USBAMP_NUM_ANALOG_IN;i++)
		add_channel(new GTecChannel(i,1.0,0,driver));
}

GTecDescription::~GTecDescription() {
}

