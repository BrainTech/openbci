//------------------------------------------------------------------------------
//Copyright (C) 2011 g.tec medical engineering GmbH.

#include <iostream>
#include <cstdio>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <signal.h>
#include <gAPI.h>
using namespace std;
//#define DEBUG

//------------------------------------------------------------------------------
#define SAMPLERATE 512

//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
unsigned char usr_buffer_master[32768];
const char* name;
bool sampling = false;
bool big_endian = false;

void CallBack(void* name_) {
	size_t cnt_master = GT_GetSamplesAvailable(name);
	size_t read = GT_GetData(name, usr_buffer_master, cnt_master);
	if (big_endian) {
		for (uint i = 0; i < read; i += 4) {
			float tmp = *((float *) usr_buffer_master + i);
			unsigned char *c = (unsigned char *) &tmp;
			usr_buffer_master[i + 0] = c[3];
			usr_buffer_master[i + 1] = c[2];
			usr_buffer_master[i + 2] = c[1];
			usr_buffer_master[i + 3] = c[0];
		}
	}
	if (read > 0)
		write(1, usr_buffer_master, read);
}
void get_device_list(bool print = false) {
	char** device_list = 0;
#ifdef DEBUG
	cout<<"Amp1\nAmp2";
	return;
#endif
	size_t list_size = 0;
	GT_UpdateDevices();
	list_size = GT_GetDeviceListSize();
	device_list = GT_GetDeviceList();
	if (print)
		for (uint i = 0; i < list_size; i++)
			cout << device_list[i] << "\n";
	GT_FreeDeviceList(device_list, list_size);
}
void stop_sampling(int sig) {
	signal(sig, SIG_DFL);
	cerr << "Simple Gtec driver Stopping....\n";
	sampling = false;
}
//------------------------------------------------------------------------------
bool show_debug(bool debug) {
#ifdef DEBUG
	return true;
#endif
	GT_ShowDebugInformation(debug);
	return true;

}

bool start_sampling(uint sample_rate) {
#ifdef DEBUG
	return true;
#endif
	gt_usbamp_analog_out_config ao_config_master;
	ao_config_master.shape = GT_ANALOGOUT_SINE;
	ao_config_master.frequency = 10;
	ao_config_master.amplitude = 200;
	ao_config_master.offset = 0;

	gt_usbamp_config config_master;
	config_master.ao_config = &ao_config_master;
	config_master.sample_rate = sample_rate;
	config_master.number_of_scans = GT_NOS_AUTOSET;
	config_master.enable_trigger_line = GT_FALSE;
	config_master.scan_dio = GT_FALSE;
	config_master.slave_mode = GT_FALSE;
	config_master.enable_sc = GT_FALSE;
	config_master.mode = GT_MODE_COUNTER;
	config_master.num_analog_in = 16;

	gt_usbamp_asynchron_config asynchron_config_master;
	for (unsigned int i = 0; i < GT_USBAMP_NUM_GROUND; i++) {
		asynchron_config_master.digital_out[i] = GT_FALSE;
		config_master.common_ground[i] = GT_TRUE;
		config_master.common_reference[i] = GT_TRUE;
	}

	for (unsigned char i = 0; i < config_master.num_analog_in; i++) {
		config_master.analog_in_channel[i] = i + 1;
		config_master.bandpass[i] = GT_FILTER_NONE;
		config_master.notch[i] = GT_FILTER_NONE;
		config_master.bipolar[i] = GT_BIPOLAR_DERIVATION_NONE;
	}
	if (!GT_OpenDevice(name)) {
		cerr << "Device open error\n";
		return false;
	}

	if (!GT_SetConfiguration(name, &config_master)) {
		cerr << "Set Configuration error\n";
		return false;
	}

	GT_SetDataReadyCallBack(name, &CallBack, (void*) (name));

	if (!GT_StartAcquisition(name)) {
		cerr << "Start failed\n";
		return false;
	}
	return true;
}
#define CHANNELS 16
#define CHUNK CHANNELS*256
int counter = 0;
void do_sampling() {
	sleep(1);
#ifndef DEBUG
	return;
#endif
	float data[CHUNK];
	for (int i = 0; i < CHUNK; i++) {
		if (i % CHANNELS == 0)
			counter++;
		data[i] = (i % CHANNELS * 10000) + counter;

	}
	write(1, (char*) data, CHUNK * sizeof(float));

}
int main(int argc, char** argv) {
	uint sample_rate = SAMPLERATE;
	show_debug(GT_FALSE);
	int a = 0x12345678;
	unsigned char *c = (unsigned char*) (&a);
	if (*c != 0x78)
		big_endian = true;

	if (argc == 1) {
		get_device_list(true);
		return 0;
	}
	name = argv[1];
	if (argc > 2) {
		sample_rate = atoi(argv[2]);
	}

	cerr << "Amplifier: " << name << "; Sampling rate:" << sample_rate << "\n";
	if (!start_sampling(sample_rate))
		return -1;
	sampling = true;
	signal(SIGINT, &stop_sampling);
	while (sampling)
		do_sampling();
	GT_StopAcquisition(name);
	GT_CloseDevice(name);
	cerr << "Simple Driver Stopped\n" << std::endl;
}
