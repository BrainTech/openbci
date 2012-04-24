/*
 * GTecDriver.cpp
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#include "GTecDriver.h"
#include "GTecDescription.h"
#include "gAPI.h"

GTecDriver::GTecDriver():AmplifierDriver() {
	char** device_list = 0;
	size_t list_size = 0;
	GT_UpdateDevices();
	list_size = GT_GetDeviceListSize();
	device_list = GT_GetDeviceList();
	for (uint i=0;i<list_size;i++)
		device_names.push_back(device_list[i]);
	if (list_size==1)
		logger.info()<<"Found 1 GTec device:"<<device_names[0];
	else if (list_size==0){
		logger.info()<<"No GTec devices!!";
		throw "No GTec devices";
	}
	else
	{	ostream& s=logger.info() << "Found "<<list_size<<" GTec devices:\n";
		for (uint i=0;i<list_size;i++)
			s <<"\t"<<i+1<<".\t"<<device_names[i]<<"\n";
	}
	GT_FreeDeviceList(device_list,list_size);

}
boost::program_options::options_description GTecDriver::get_options(){
	boost::program_options::options_description options=AmplifierDriver::get_options();
	options.add_options()
			("device_index,d",boost::program_options::value<uint>()->default_value(1),"Index of GTec device");
	return options;
}
void get_data_callback(void * driver){
	((GTecDriver *)driver)->get_data();
}
void GTecDriver::init(boost::program_options::variables_map &vm){

	uint device_index=vm["device_index"].as<uint>()-1;
	if (device_index<0 || device_index>=device_names.size())
		throw "Wrong device index!";
	name=device_names[device_index];
	if (!GT_OpenDevice(name.c_str()))
		throw "Device open error!";
	set_description(new GTecDescription(name,this));
	GT_SetDataReadyCallBack(name.c_str(),&get_data_callback,this);
}
void GTecDriver::start_sampling(){
	AmplifierDriver::start_sampling();
	GT_StartAcquisition(name.c_str());
}
void GTecDriver::stop_sampling(){
	GT_StopAcquisition(name.c_str());
}
void GTecDriver::get_data(){
	uint size=GT_GetSamplesAvailable(name.c_str());
	logger.info()<<"Available Samples: "<<size;
	unsigned char buffer[1000000000];
	logger.info()<<"Read Samples:"<<GT_GetData(name.c_str(),buffer,size)<<"; "<<GT_GetSamplesAvailable(name.c_str());
	for (uint i=0;i<description->get_physical_channels();i++)
		((GTecChannel*)description->get_channels()[i])->set_sample((float)*(buffer+i*4));

}
GTecDriver::~GTecDriver() {
	// TODO Auto-generated destructor stub
}

