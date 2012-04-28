/* 
 * File:   AmplifierServer.cpp
 * Author: Macias
 * 
 * Created on 14 październik 2010, 15:31
 */
#include "AmplifierServer.h"
#include "multiplexer/Multiplexer.pb.h"
#include "multiplexer/multiplexer.constants.h"
#include "multiplexer/Client.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "variables.pb.h"
#include "Logger.h"
#include <boost/shared_ptr.hpp>
#include <boost/date_time/posix_time/ptime.hpp>
#include <vector>
using namespace multiplexer;
namespace po=boost::program_options;
AmplifierServer::AmplifierServer(Amplifier *driv) :
BaseMultiplexerServer(new Client(peers::AMPLIFIER), peers::AMPLIFIER)
{
    driver=driv;
	logger = NULL;
}
po::options_description AmplifierServer::get_options(){
	po::options_description	options("Server Options");
	options.add_options()
    		("host,h",po::value<string>()->default_value("127.0.0.1"),"IP Address of the multiplexer")
    		("port,p",po::value<uint>()->default_value(31889),"Port of the multiplexer")
    		("samples_per_vector,v",po::value<uint>(&samples_per_vector)->default_value(1),"Number of samples sent in one package")
    		("start","If specified - don't wait on stdin for additional parameters")
    		;
    return options;
}
void AmplifierServer::init(po::variables_map vm){
	connect(vm["host"].as<string>(),vm["port"].as<uint>());
	if (vm.count("start"))
		start_sampling();
}

void AmplifierServer::connect(string host,uint port){
	if (logger)
		logger->info() << "Connecting to:" << host <<":"<< port<< "\n";
	conn->connect(host,port);
}

void * _receive(void *amp) {
    ((AmplifierServer *) amp)->loop();
    return NULL;
}

int AmplifierServer::loop_in_thread() {
    debug("Starting receiving messages");
    return pthread_create(&receiving_thread, NULL, _receive, (void*) this);
}

AmplifierServer::~AmplifierServer() {
    stop_sampling();
    pthread_kill(receiving_thread, 0);
}
bool AmplifierServer::fetch_samples(){
	driver->next_samples();
	return driver->is_sampling();
}
void AmplifierServer::do_sampling(void * ptr = NULL) {
    MultiplexerMessage msg;
	msg.set_from(conn->instance_id());
	msg.set_type(types::AMPLIFIER_SIGNAL_MESSAGE);
	vector<Channel *> channels=driver->get_active_channels();
	variables::SampleVector s_vector;
    variables::Sample * sample[samples_per_vector];
    for (uint i = 0; i < samples_per_vector; i++){
        sample[i] = s_vector.add_samples();
        for (uint j=0;j<channels.size();j++)
        	sample[i]->add_channels(0);
    }
    while (driver->is_sampling()) {
    	for (uint i=0;i<samples_per_vector;i++){
    		if (!fetch_samples()) {
    			while (i++<samples_per_vector)
    				s_vector.mutable_samples()->RemoveLast();
    			break;
    		}
    		sample[i]->set_timestamp(driver->get_sample_timestamp());
    		for (uint j=0;j<channels.size();j++)
    			*sample[i]->mutable_channels()->Mutable(j)=channels[j]->get_sample();
    	  	if (logger != NULL) logger->next_sample();
    	}
  	  string msgstr;
  	  s_vector.SerializeToString(&msgstr);
  	  msg.set_id(conn->random64());
  	  msg.set_message(msgstr);
  	  Client::ScheduledMessageTracker tracker = conn->schedule_one(msg);
  	  if (!tracker) {
  	    fprintf(stderr,"Error: sending failed.\n");
  	    return;
  	  }
  	  conn->flush(tracker, -1);
  	}
    if (logger) logger->info() << "Sampling stopped\n";
}

void * _do_sampling(void * amp) {
    ((AmplifierServer *) amp)->do_sampling();
    return NULL;
}

void AmplifierServer::start_sampling() {
	driver->start_sampling();
    //  sampling_thread = new boost::thread(t);
    if (logger!=NULL) {
    	logger->restart();
    	logger->info() << "Sampling started\n";
    }
    //pthread_create(&sampling_thread, NULL, _do_sampling, (void *) this);
    do_sampling();
    
}

void AmplifierServer::stop_sampling() {
    debug("Stop_sampling\n");
    if (!driver->is_sampling()) return;
    driver->stop_sampling();
    //sampling_thread->join();
    if (!pthread_equal(pthread_self(),sampling_thread))
        pthread_join(sampling_thread, NULL);
    debug("Sampling stopped\n");
}

void AmplifierServer::handle_message(MultiplexerMessage & msg) {
    debug("Received message! Type:%s message: %s", types::get_name(msg.type()), msg.message().c_str());
}

bool AmplifierServer::do_command(string command, istream &cin){
	if (command=="start"){
				cout.flush();
				start_sampling();
			}
	else if (command=="stop")
				stop_sampling();
	else if (command=="sampling_rate"){
				uint s_r;
				cin>>s_r;
				driver->set_sampling_rate_(s_r);
			}
	else if (command=="active_channels"){
				string line;
				cin>>line;
				driver->set_active_channels_string(line);
			}
	else return false;
	return true;
}
string AmplifierServer::get_commands(){
    	return "sampling_rate <value>, active_channels <coma_separated_channel_names>, start, stop";
    }
