/*
 * GTecDriver.cpp
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#include "GTecAmplifier.h"
#include "GTecDescription.h"
#include <string.h>
#include <errno.h>
#include <sys/wait.h>
#include "simple_gtec_driver.h"
#define MAX_DRIVERS 100000
#define SAMPLES_SIZE 16*4
namespace po=boost::program_options;
void GTecAmplifier::wait_simple_driver(){
	int status;
	if (simple_driver_id>0)
		waitpid(simple_driver_id,&status,0);
	if (simple_driver_output>-1)
		close(simple_driver_output);
	simple_driver_id=-1;
	simple_driver_output=-1;
}
void GTecAmplifier::spawn_simple_driver(const char* name){
	int fd[2];
	wait_simple_driver();
	pipe(fd);
	simple_driver_id=fork();
	stringstream s_rate;
	s_rate << sampling_rate;
	if (simple_driver_id<0)
		throw "Fork Error";
	else if (simple_driver_id==0){
		close(fd[0]);
		close(1);
		dup2(fd[1],1);
        if (name!=NULL)
            execl(simple_driver_path.c_str(),"simple_gtec_driver","-n",name,"-s",s_rate.str().c_str(),"-c","sampling",NULL);
        else
            execl(simple_driver_path.c_str(),"simple_gtec_driver",NULL);
		cerr << "Could not run "<<simple_driver_path<<":"<<strerror(errno)<<"\n";
		exit(-1);
	}
	else{
		close(fd[1]);
		simple_driver_output=fd[0];
	}
}
GTecAmplifier::GTecAmplifier():Amplifier(),simple_driver_id(-1),simple_driver_output(-1) {
}
po::options_description GTecAmplifier::get_options(){
	po::options_description options=Amplifier::get_options();
	options.add_options()
			("device_index,i",boost::program_options::value<uint>()->default_value(1),"Index of GTec device")
			("available_devices,a","Print available devices and exit")
			("simple_driver_path,d",boost::program_options::value<string>()->default_value("simple_gtec_driver"),"Path to the simple_gtec_driver")
			("run_simple,r","Run Simple Gtec Driver with remaining command line parameters. Can be used for signal generation or calibration. See 'Gtec Simple Driver Options' for available parameters");
	options.add(get_simple_options());
	return options;
}
void get_data_callback(void * driver){
	((GTecAmplifier *)driver)->get_data();
}
void GTecAmplifier::init(po::variables_map &vm){
	size_t list_size = 0;
	char drivers[MAX_DRIVERS];
	simple_driver_path=vm["simple_driver_path"].as<string>();	
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
	if (vm.count("available_devices")){
		for (uint i=0;i<device_names.size();i++)
			cout<<device_names[i]<<"\n";
		exit(0);
	}
	uint device_index=vm["device_index"].as<uint>()-1;
	if (device_index<0 || device_index>=device_names.size())
		throw "Wrong device index!";
	name=device_names[device_index];
	set_description(new GTecDescription(name,this,device_index));
}
void GTecAmplifier::start_sampling(){
	Amplifier::start_sampling();
	stringstream name;
	name << ((GTecDescription*)this->description)->device_index+1;	
	spawn_simple_driver(name.str().c_str());
	return;
	char msg[50];
	read(simple_driver_output,msg,2);
	msg[2]=0;
	string s(msg);
	if (s!="OK"){	
		read(simple_driver_output,msg+2,48);
		cerr<<msg<<"\n";
		throw "StartSampling Error!";
	
	}
}
void GTecAmplifier::stop_sampling(bool disconecting){
	kill(simple_driver_id,SIGINT);
	Amplifier::stop_sampling();
}
void GTecAmplifier::get_data(){

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
double GTecAmplifier::next_samples(bool synchronize){
	get_data();
	return Amplifier::next_samples(false);
}
GTecAmplifier::~GTecAmplifier() {
	wait_simple_driver();
}
bool GTecAmplifier::run_simple(int argc,char** argv){
	po::options_description options = get_options();
	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,options),vm);
	if (!vm.count("run_simple")){
		return false;
	}
	for (uint j=0;j<argc;j++){
		string str=argv[j];
		if (str=="-r" || str=="--run_simple"){
			argv[j]="simple_driver_path";
			string path =vm["simple_driver_path"].as<string>();
			execv(path.c_str(),argv+j);
			perror("Could not run Simple Gtec Driver:");
		}
	}
	return false;
}

