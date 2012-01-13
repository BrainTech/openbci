/* 
 * File:   AmplifierServer.h
 * Author: Macias
 *
 * Created on 14 październik 2010, 15:31
 */

#ifndef AMPLIFIERSERVER_H
#define	AMPLIFIERSERVER_H
#define BOOST
#include "boost.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "variables.pb.h"
#include "azouk/util/kwargs.h"
#include "AmplifierDriver.h"
#include "Logger.h"

#include <pthread.h>
#include <string>
#include <vector>

using namespace std;
using namespace multiplexer;
#ifdef AMP_DEBUG
#define debug(...) fprintf(stderr,"AmplifierServer: " __VA_ARGS__)
#else
#define debug(...) ;
#endif
#ifdef BOOST
#include <boost/program_options.hpp>
#endif
class AmplifierServer:public backend::BaseMultiplexerServer {
public:
    AmplifierServer(AmplifierDriver *);

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
    void connect(string host,uint port);
#ifdef BOOST
    virtual boost::program_options::options_description  get_options();
    void init(boost::program_options::variables_map vm);
#endif
protected:
    uint samples_per_vector;
    std::vector<int> channels;
    pthread_t sampling_thread,receiving_thread;
    AmplifierDriver * driver;
    Logger *logger;
};

#endif	/* AMPLIFIERSERVER_H */

