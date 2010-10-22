/* 
 * File:   AmplifierServer.cpp
 * Author: Macias
 * 
 * Created on 14 październik 2010, 15:31
 */

#include "AmplifierServer.h"
#include "Logger.h"
#include <boost/shared_ptr.hpp>
#include <vector>
using namespace multiplexer;

AmplifierServer::AmplifierServer(const std::string& host, boost::uint16_t port,
        AmplifierDriver *driv) :
BaseMultiplexerServer(new Client(peers::AMPLIFIER), peers::AMPLIFIER) {

    conn->connect(host, port);
    shared_ptr<MultiplexerMessage> msg =
            conn->query("AmplifierChannelsToRecord", types::DICT_GET_REQUEST_MESSAGE).second;
    std::string s_channels = msg->message();
    std::stringstream ss_chan(s_channels);
    int tmp;
    vector<int> channels;
    while (ss_chan >> tmp)
        channels.push_back(tmp);
    number_of_channels = channels.size();
    driver = driv;
    driver->set_active_channels(channels);
    msg = conn->query("SamplingRate", types::DICT_GET_REQUEST_MESSAGE).second;
    int samp_rate = atoi(msg->message().c_str());
    if (driver->set_sampling_rate(samp_rate) != samp_rate)
        fprintf(stderr, "Warning: sampling rate set to %d Hz instead of %d Hz",
            driver->get_sampling_rate(), samp_rate);
    logger = NULL;
}

void * _receive(void *amp) {
    ((AmplifierServer *) amp)->loop();
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
    for (int i = 0; i < number_of_channels; i++)
        s_vector.add_samples();
    std::vector<int> isamples(number_of_channels, 0);
    MultiplexerMessage msg;
    msg.set_from(conn->instance_id());
    msg.set_type(types::AMPLIFIER_SIGNAL_MESSAGE);
    int j=0;
    while (driver->is_sampling()) {
        time_t t = time(NULL);
        if (driver->fill_samples(isamples) < 0) {
            stop_sampling();
            return;
        }
        for (int i = 0; i < number_of_channels; i++) {
            variables::Sample *samp = s_vector.mutable_samples(i);
            samp->set_value(isamples[i]);
            samp->set_timestamp(t);
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
}

void AmplifierServer::start_sampling() {
    driver->start_sampling();
    //  sampling_thread = new boost::thread(t);
    pthread_create(&sampling_thread, NULL, _do_sampling, (void *) this);
    if (logger!=NULL) logger->restart();
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
