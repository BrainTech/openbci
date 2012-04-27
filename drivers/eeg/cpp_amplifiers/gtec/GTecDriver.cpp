/*
 * GTecDriver.cpp
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#include "GTecDriver.h"
#include "GTecDescription.h"
#include <string.h>
#include <errno.h>
#include <sys/wait.h>
#define MAX_DRIVERS 100000
#define SAMPLES_SIZE 16*4
void GTecDriver::wait_simple_driver(){
	int status;
	if (simple_driver_id>0)
		waitpid(simple_driver_id,&status,0);
	if (simple_driver_output>-1)
		close(simple_driver_output);
	simple_driver_id=-1;
	simple_driver_output=-1;
}
void GTecDriver::spawn_simple_driver(const char* name){
	int fd[2];
	wait_simple_driver();
	pipe(fd);
	simple_driver_id=fork();
	if (simple_driver_id<0)
		throw "Fork Error";
	else if (simple_driver_id==0){
		close(fd[0]);
		close(1);
		dup2(fd[1],1);
		execl("simple_gtec_driver","simple_gtec_driver",name,NULL);

	}
	else{
		close(fd[1]);
		simple_driver_output=fd[0];
	}
}

GTecDriver::GTecDriver():AmplifierDriver(),simple_driver_id(-1),simple_driver_output(-1) {
	size_t list_size = 0;
	char drivers[MAX_DRIVERS];
	spawn_simple_driver(NULL);
	read(simple_driver_output,drivers,MAX_DRIVERS);
	close(simple_driver_output);
	simple_driver_output=-1;
	simple_driver_id=-1;
	device_names=split_string(drivers,'\n');
	list_size=device_names.size();
	if (list_size==1)
		logger.info()<<"Found 1 GTec device:"<<device_names[0]<<"\n";
	else if (list_size==0){
		logger.info()<<"No GTec devices!!";
		throw "No GTec devices";
	}
	else
	{	ostream& s=logger.info() << "Found "<<list_size<<" GTec devices:\n";
		for (uint i=0;i<list_size;i++)
			s <<"\t"<<i+1<<".\t"<<device_names[i]<<"\n";
	}
}
boost::program_options::options_description GTecDriver::get_options(){
	boost::program_options::options_description options=AmplifierDriver::get_options();
	options.add_options()
			("device_index,d",boost::program_options::value<uint>()->default_value(1),"Index of GTec device")
			("available_devices,a","Print available devices and exit");
	return options;
}
void get_data_callback(void * driver){
	((GTecDriver *)driver)->get_data();
}
void GTecDriver::init(boost::program_options::variables_map &vm){
	if (vm.count("available_devices")){
		for (uint i=0;i<device_names.size();i++)
			cout<<device_names[i]<<"\n";
		exit(0);
	}
	uint device_index=vm["device_index"].as<uint>()-1;
	if (device_index<0 || device_index>=device_names.size())
		throw "Wrong device index!";
	name=device_names[device_index];
	set_description(new GTecDescription(name,this));
}
void GTecDriver::start_sampling(){
	AmplifierDriver::start_sampling();
	spawn_simple_driver(name.c_str());
}
void GTecDriver::stop_sampling(bool disconecting){
	kill(simple_driver_id,SIGINT);
	AmplifierDriver::stop_sampling();
}
void GTecDriver::get_data(){

	float buffer[SAMPLES_SIZE];
	ssize_t left=SAMPLES_SIZE,count=1;
	while (left>0 && count>0){
		count = read(simple_driver_output,((char*)buffer)+(SAMPLES_SIZE-left),left);
		if (count<0){
			logger.info() <<"Read error:" <<strerror(errno);
			return;
		}

		left-=count;
	}
	for (uint i=0;i<description->get_physical_channels();i++){
		((GTecChannel*)description->get_channels()[i])->set_sample(buffer[i]);
	}
}
double GTecDriver::next_samples(){
	get_data();
	return AmplifierDriver::next_samples();
}
GTecDriver::~GTecDriver() {
	wait_simple_driver();
}

