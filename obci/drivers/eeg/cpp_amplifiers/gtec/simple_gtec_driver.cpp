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
#include <vector>
#include <math.h>
using namespace std;
#include <boost/program_options.hpp>
namespace po = boost::program_options;
#include "simple_gtec_driver.h"
//#define DEBUG

//------------------------------------------------------------------------------

#define CALIB_AMP 1.0
#define CALIB_OFFSET 0.0
#define CALIB_FREQ 10
#define CALIB_DURATION 5
#define CALIB_SAMPLING_RATE 512

#define SAMPLERATE 512

//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
gt_usbamp_analog_out_config calib_params;
gt_usbamp_device_mode mode=GT_MODE_COUNTER;
const char* name;
uint sample_rate;
uint calib_duration;
unsigned char usr_buffer_master[32768];

bool sampling = false;
bool big_endian = false;

size_t getSamples(){
	size_t cnt_master = GT_GetSamplesAvailable(name);
	size_t read = GT_GetData(name, usr_buffer_master, cnt_master);
	if (big_endian) {
		for (uint i = 0; i < read; i += 4) {
			float tmp = *((float *) (usr_buffer_master + i));
			unsigned char *c = (unsigned char *) &tmp;
			usr_buffer_master[i + 0] = c[3];
			usr_buffer_master[i + 1] = c[2];
			usr_buffer_master[i + 2] = c[1];
			usr_buffer_master[i + 3] = c[0];
		}
	}
	return read;
}
bool first_samples=true;
void sendCallBack(void *) {
	size_t read=getSamples();
	if (read > 0){
	if (first_samples){
		first_samples=false;
                write(1,"OK",2);	
	}
		write(1, usr_buffer_master, read);
	}
}

string getDeviceList(bool print = false,uint amp=0) {
	char** device_list = 0;
	string name;
#ifdef DEBUG
	cout<<"Amp1:1.0574;1.0506;1.0607;1.05776;1.0578;1.05702;1.05723;1.05892;1.05596;1.06086;1.05601;1.0543;1.05579;1.05741;1.05839;1.05715;:-508.797;-485.906;-670.641;-409.11;-1103.14;-598.157;-1236.43;-1011.43;-994.906;-646.509;-830.82;-1063.1;-701.673;-621.619;-292.877;-777.172;\nAmp2:1.0574;1.0506;1.0607;1.05776;1.0578;1.05702;1.05723;1.05892;1.05596;1.06086;1.05601;1.0543;1.05579;1.05741;1.05839;1.05715;:-508.797;-485.906;-670.641;-409.11;-1103.14;-598.157;-1236.43;-1011.43;-994.906;-646.509;-830.82;-1063.1;-701.673;-621.619;-292.877;-777.172;";
	return "Amp1";
#endif
	size_t list_size = 0;
	GT_UpdateDevices();
	list_size = GT_GetDeviceListSize();
	device_list = GT_GetDeviceList();
	vector<string> devices;
	for (uint i=0;i<list_size;i++)
		devices.push_back(device_list[i]);
	if (amp<list_size)
		name=device_list[amp];
	GT_FreeDeviceList(device_list, list_size);
	
	if (print)
		for (uint i = 0; i < list_size; i++){
			string name = devices[i];
			cout << name << ":";
			gt_usbamp_channel_calibration calibration;		
			if (GT_OpenDevice(name.c_str())){
				if (GT_GetChannelCalibration(name.c_str(),&calibration))
				{for (uint c=0;c<GT_USBAMP_NUM_ANALOG_IN;c++)
					cout<<calibration.scale[c]<<";";
				cout << ":";
				for (uint c=0;c<GT_USBAMP_NUM_ANALOG_IN;c++)
					cout<<calibration.offset[c]<<";";}
			    GT_CloseDevice(name.c_str());
			}				
			cout <<"\n";
		}
	
	return name;
}

void stopSampling(int sig) {
	signal(sig, SIG_DFL);
	cerr << "Simple Gtec driver Stopping....\n";
	sampling = false;
}




bool show_debug(bool debug) {
#ifdef DEBUG
	return true;
#endif
	GT_ShowDebugInformation(debug);
	return true;

}

bool openDevice(){
	gt_usbamp_config config_master;
	config_master.ao_config =&calib_params;
	config_master.sample_rate = sample_rate;
	config_master.number_of_scans = GT_NOS_AUTOSET;
	config_master.enable_trigger_line = GT_FALSE;
	config_master.scan_dio = GT_FALSE;
	config_master.slave_mode = GT_FALSE;
	config_master.enable_sc = GT_FALSE;
	config_master.mode = mode;
	config_master.num_analog_in = 16;

	//gt_usbamp_asynchron_config asynchron_config_master;
	for (unsigned int i = 0; i < GT_USBAMP_NUM_GROUND; i++) {
		//asynchron_config_master.digital_out[i] = GT_FALSE;
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
		cerr<< "Device open error:'"<<name<<"'\n";
		return false;
	}
	
	if (!GT_SetConfiguration(name, &config_master)) {
		cerr<<"Set Configuration error\n";
		return false;
	}
	return true;

}

struct channel_calib_data{
  vector<float> max,min;
  vector<float> samples;
  float last,last_p;
  uint max_count,min_count,count;
  double max_sum,min_sum,max_avg,min_avg, sum;

};
class calib_data{
 public:
  vector<channel_calib_data> channel;
  uint cur_channel;
  const char * name;
  bool gather;
  uint sample;
  calib_data(const char* name_):channel(16),cur_channel(0),name(name_),gather(false),sample(0){}
};
void gatherDataCallback(void * ptr){
	calib_data * c_data=(calib_data *)ptr;
	size_t data = getSamples();
	uint i=0;
	
	while (i<data){
	  float val = *((float*)(usr_buffer_master+i));	  
	  channel_calib_data& c = c_data->channel[c_data->cur_channel];	  
	  if (c_data->gather){
		  if (c.last_p <= c.last && c.last > val && val>0)
			{c.max.push_back(c.last);c.max_count++;c.max_sum+=c.last;}
		  if (c.last_p >= c.last && c.last < val && val<0)
			{c.min.push_back(c.last);c.min_count++;c.min_sum+=c.last;}
		  c.sum+=val;
		  c.count++;
		  c.samples.push_back(val);
	  }
	  c.last_p=c.last;
	  c.last = val;
	  c_data->cur_channel=(c_data->cur_channel+1)%16;
		if (c_data->cur_channel==0) c_data->sample++;
	  i+=4;	
	}
}


int computeCalibration(gt_usbamp_channel_calibration &calibration){
	calib_data c_data(name);
	
	GT_SetDataReadyCallBack(name,&gatherDataCallback,(void*) &c_data);
	if (!GT_StartAcquisition(name)) {
		cerr<< "Start failed\n";
		return -1;
	} 
	cerr <<"Waiting...(2 seconds)\n";
	sleep(2);
	c_data.gather=true;
	cerr <<"Gathering data ("<<calib_duration<<" seconds)\n";
	sleep(calib_duration);
	cerr <<"\nStop Aquisition....\n";
	GT_StopAcquisition(name);
	
	cout <<"Calibration Results"<<"\n";
	for (uint i=0;i<16;i++){
	  channel_calib_data c= c_data.channel[i];
	  double avg = c.sum/c.count;
	  double sq_sum = 0;
	  for (uint j=0;j<c.samples.size();j++)
		  sq_sum+=(c.samples[j]-avg)*(c.samples[j]-avg);
	  double rms = sqrt(sq_sum/c.count);
      double max_avg=c.max_avg = c.max_sum/c.max_count;
	  double min_avg=c.min_avg = c.min_sum/c.min_count;
	  printf("Channel %d: max_avg:%f (%d), min_avg:%f (%d), avg:%f, rms:%f\n",i,max_avg,c.max_count,min_avg,c.min_count,avg,rms);
	  //double amp_max = CALIB_AMP*1000;
      	  //double amp_min = -CALIB_AMP*1000;
	  double o=avg;
	  double s=calib_params.amplitude*1000/(rms*sqrt(2));
	  calibration.offset[i]=o;
	  calibration.scale[i]=s;
	  cout <<"  Scale: "<<s<<" offset:"<<o<<"\n";	  
	}
	return 0;
	
}
int resetCalibration(bool open=false){
	if (open)
		GT_OpenDevice(name);
	gt_usbamp_channel_calibration calibration;
	GT_GetChannelCalibration(name,&calibration);
	cout << "Current Calibration Values\n";
	for (uint i=0;i<16;i++){
		cout <<"Channel "<<i<<" scale:"<<calibration.scale[i]<<" offset:"<<calibration.offset[i]<<"\n";
		calibration.scale[i]=1.0;
		calibration.offset[i]=0.0;
	}
	cout << "Setting all scales to 1.0 and offsets to 0.0...";
	cout.flush();
	GT_SetChannelCalibration(name,&calibration);	
	cout <<"done.\n";
	if (open)
	   GT_CloseDevice(name);
        return 0;
}
int checkCalibration(){
    mode = GT_MODE_CALIBRATE;
    openDevice();
    gt_usbamp_channel_calibration calibration;
    computeCalibration(calibration);
    GT_CloseDevice(name);
    return 0;
}
int calibrate(){
	gt_usbamp_channel_calibration calibration;
	calib_params.shape=GT_ANALOGOUT_SINE;
	mode = GT_MODE_CALIBRATE;
	if (!openDevice())
	  return -1;
	calib_data c_data(name);
	resetCalibration();	
	computeCalibration(calibration);	
	GT_SetChannelCalibration(name,&calibration);
	cout << "Calibration param set. Checking signal after calibration....("<<CALIB_DURATION<<" seconds)\n";
	cout << "Calibration Errors (scale should be close to 1.0 and offset should be 0.0):\n";	
	computeCalibration(calibration);
		
	GT_CloseDevice(name);
	return 0;
}

bool startSampling(uint sample_rate) {
#ifdef DEBUG
	return true;
#endif
	if (!openDevice())
		return false;
	GT_SetDataReadyCallBack(name, &sendCallBack, (void*) (name));

	if (!GT_StartAcquisition(name)) {
		cerr<< "Start failed\n";
		return false;
	}
	return true;
}
#define CHANNELS 16
#define CHUNK CHANNELS*256
int counter = 0;
void doSampling() {
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
	po::options_description desc=get_simple_options();
	po::variables_map vm;
	po::store(po::parse_command_line(argc, argv, desc), vm);
	if (vm.count("help"))
		cerr << desc;
	else
		cerr << "Use --help for available options" <<"\n";
	calib_duration = vm["calib_duration"].as<int>();
	sample_rate = vm["sampling_rate"].as<uint>();
	string shape=vm["function"].as<string>();
	if (shape=="sinus")
		calib_params.shape = GT_ANALOGOUT_SINE;
	else if (shape=="saw")
		calib_params.shape = GT_ANALOGOUT_SAWTOOTH;
	else if (shape=="square")
		calib_params.shape = GT_ANALOGOUT_SQUARE;
	else if (shape=="noise")
		calib_params.shape = GT_ANALOGOUT_NOISE;
	calib_params.frequency = vm["frequency"].as<int>();
	calib_params.amplitude = vm["amplitude"].as<int>();
	calib_params.offset = vm["offset"].as<int>();
	string m=vm["mode"].as<string>();
	if (m=="normal")
		mode = GT_MODE_NORMAL;
	else if (m=="counter")
		mode = GT_MODE_COUNTER;
	else if (m=="function")
		mode = GT_MODE_CALIBRATE; 
	string s_name;
	show_debug(GT_FALSE);
	int a = 0x12345678;
	unsigned char *c = (unsigned char*) (&a);
	if (*c != 0x78)
		big_endian = true;
	if (vm.count("device_name")){
		s_name=vm["device_name"].as<string>();
		name = s_name.c_str();
	}
	else{
		s_name = getDeviceList(false,vm["device_index"].as<int>()-1);
		name=s_name.c_str();
	}
	string command = vm["command"].as<string>();
	cerr << "Amplifier: " << name << "; Sampling rate:" << sample_rate << "\n";	
	if (command=="show") {
		getDeviceList(true);
		return 0;
	}else if (command=="calibrate")
		return calibrate();
	else if (command=="reset")
		return resetCalibration(true);
	else if (command=="measure")
		return checkCalibration();

	if (!startSampling(sample_rate))
	{			
		return -1;
	}
	
	sampling = true;
	signal(SIGINT, &stopSampling);
	while (sampling)
		doSampling();
	cerr <<"\nStop Aquisition....\n";
	GT_StopAcquisition(name);
	cerr <<"\nCloseDevice...\n";
	GT_CloseDevice(name);
	cerr << "Simple Driver Stopped\n" << std::endl;
}
