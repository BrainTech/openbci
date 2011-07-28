/* 
 * File:   AmplifierServer.cpp
 * Author: Macias
 * 
 * Created on 14 październik 2010, 15:31
 */
#include "multiplexer/Multiplexer.pb.h"
#include "multiplexer/multiplexer.constants.h"
#include "multiplexer/Client.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "variables.pb.h"
#include "AmplifierServer.h"
#include "Logger.h"
#include <boost/shared_ptr.hpp>
#include <boost/date_time/posix_time/ptime.hpp>
#include <vector>
using namespace multiplexer;

AmplifierServer::AmplifierServer(const std::string& host, boost::uint16_t port,
        AmplifierDriver *driv) :
BaseMultiplexerServer(new Client(peers::AMPLIFIER), peers::AMPLIFIER) {

    debug("Connecting....");
    conn->connect(host, port);
    debug("Sending query...");
    shared_ptr<MultiplexerMessage> msg =
            conn->query("AmplifierChannelsToRecord", types::DICT_GET_REQUEST_MESSAGE).second;
    std::string s_channels = msg->message();
    std::stringstream ss_chan(s_channels);
    std::string tmp;
    vector<std::string> channels;


    std::string sp = "sample";
    ext_number_of_channels = 0;
    while (ss_chan >> tmp) {
      if (tmp != sp)
	channels.push_back(tmp);
      else
	ext_number_of_channels = 1;
    };

    number_of_channels = channels.size();
    ext_number_of_channels += number_of_channels;
    driver = driv;
    driver->set_active_channels(channels);
    debug("Sending query");
    msg = conn->query("SamplingRate", types::DICT_GET_REQUEST_MESSAGE).second;
    int samp_rate = atoi(msg->message().c_str());
    set_sampling_rate(samp_rate);
    logger = NULL;
}
void AmplifierServer::set_sampling_rate(int samp_rate)
{
    if (driver->set_sampling_rate(samp_rate) != samp_rate)
        fprintf(stderr, "Warning: sampling rate set to %d Hz instead of %d Hz",
            driver->get_sampling_rate(), samp_rate);
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

void AmplifierServer::do_sampling(void * ptr = NULL) {
    debug("Sampling started\n");
    variables::SampleVector s_vector;
    for (int i = 0; i < ext_number_of_channels; i++)
        s_vector.add_samples();
    std::vector<int> isamples(number_of_channels, 0);
    MultiplexerMessage msg;
    msg.set_from(conn->instance_id());
    msg.set_type(types::AMPLIFIER_SIGNAL_MESSAGE);
    double samples_no = 0.0;
    while (driver->is_sampling()) {
        boost::posix_time::ptime t=boost::posix_time::microsec_clock::local_time();
        double ti=time(NULL);
        ti+=(t.time_of_day().total_nanoseconds()%1000000000)/1000000000.0;
        if (driver->fill_samples(isamples) < 0) {
            stop_sampling();
            return;
        }
        debug("Received samples:\n");
        for (int i = 0; i < number_of_channels; i++) {
            variables::Sample *samp = s_vector.mutable_samples(i);
            samp->set_value(isamples[i]);
            debug("%2d: %d %x\n",i,isamples[i],isamples[i]);
            samp->set_timestamp(ti);
        }

	if (ext_number_of_channels == number_of_channels + 1) {
	  samples_no += 1.0;
	  variables::Sample *samp = s_vector.mutable_samples(number_of_channels);	
	  samp->set_value(samples_no);
	  samp->set_timestamp(ti);
	}
	
        std::string msgstr;
        s_vector.SerializeToString(&msgstr);
        msg.set_id(conn->random64());
        msg.set_message(msgstr);
        Client::ScheduledMessageTracker tracker = conn->schedule_one(msg);
        if (!tracker) {
                fprintf(stderr,"Error: sending failed.\n");
                return;
        }
        conn->flush(tracker, -1);
        check_status(isamples);
        if (logger != NULL) logger->next_sample();
    }
}

void * _do_sampling(void * amp) {
    ((AmplifierServer *) amp)->do_sampling();
    return NULL;
}

void AmplifierServer::start_sampling() {
    driver->start_sampling();
    //  sampling_thread = new boost::thread(t);
    if (logger!=NULL) logger->restart();
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
