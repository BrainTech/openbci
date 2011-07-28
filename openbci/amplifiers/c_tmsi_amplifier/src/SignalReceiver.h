/* 
 * File:   SignalReceiver.h
 * Author: Macias
 *
 * Created on 3 listopad 2010, 15:11
 */

#ifndef SIGNALRECEIVER_H
#define	SIGNALRECEIVER_H
#include "multiplexer/Multiplexer.pb.h"
#include "multiplexer/multiplexer.constants.h"
#include "multiplexer/Client.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "variables.pb.h"
#include "azouk/util/kwargs.h"
#include <boost/shared_ptr.hpp>
#include <boost/date_time/posix_time/ptime.hpp>
#include "Logger.h"
#include <pthread.h>
#include <string>
#include <vector>
using namespace multiplexer;

class SignalReceiver:public backend::BaseMultiplexerServer {
private:
    Logger * logger;
    int sample_count;
    int num_of_channels;
    int cached_index;
    int cache_size;
    int monitor_last_channel;
    double prev_last_channel;
    double** cached_samples;

public:

    virtual void handle_message(MultiplexerMessage & msg);
    SignalReceiver(const std::string& host, boost::uint16_t port, int cache_size);
    virtual ~SignalReceiver(){};
};

#endif	/* SIGNALRECEIVER_H */

