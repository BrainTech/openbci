/* 
 * File:   AmplifierServer.h
 * Author: Macias
 *
 * Created on 14 październik 2010, 15:31
 */

#ifndef AMPLIFIERSERVER_H
#define	AMPLIFIERSERVER_H


#include "multiplexer/Multiplexer.pb.h"
#include "multiplexer/multiplexer.constants.h"
#include "multiplexer/Client.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "variables.pb.h"
#include "azouk/util/kwargs.h"
#include "AmplifierDriver.h"
#include "Logger.h"

#include <pthread.h>
#include <string>

using namespace multiplexer;
#ifdef AMP_DEBUG
#define debug(...) printf("AmplifierServer: " __VA_ARGS__)
#else
#define debug(...) ;
#endif
class AmplifierServer:public backend::BaseMultiplexerServer {
public:
    AmplifierServer(const std::string& host, boost::uint16_t port,AmplifierDriver *);
    virtual void start_sampling();
    virtual void stop_sampling();
    virtual void handle_message(MultiplexerMessage & msg);
    int loop_in_thread();
    void do_sampling(void * ptr /* = NULL */);
    virtual ~AmplifierServer();
    void set_logger(Logger *log)
    {
        logger=log;
    }
protected:
    int number_of_channels;
    std::vector<int> channels;
    pthread_t sampling_thread,receiving_thread;
    AmplifierDriver * driver;
    Logger *logger;
    virtual void check_status(std::vector<int> &isamples){};
};

#endif	/* AMPLIFIERSERVER_H */

