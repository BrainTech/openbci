/* 
 * File:   AmplifierServer.h
 * Author: Macias
 *
 * Created on 14 październik 2010, 15:31
 */

#ifndef AMPLIFIERSERVER_H
#define	AMPLIFIERSERVER_H
#include "boost.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "Amplifier.h"
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
#include <boost/program_options.hpp>
class AmplifierServer: public backend::BaseMultiplexerServer {
public:
	AmplifierServer(Amplifier *);

	virtual void start_sampling();
	virtual void stop_sampling();
	virtual void handle_message(MultiplexerMessage & msg);
	int loop_in_thread();
	void do_sampling(void * ptr /* = NULL */);
	virtual ~AmplifierServer();
	void set_logger(Logger *log) {
		logger = log;
	}
	void connect(string host, uint port);
	virtual bool do_command(string command, istream& cin);
	virtual string get_commands();
	Amplifier *get_driver() {
		return driver;
	}
	virtual boost::program_options::options_description get_options();
	void init(boost::program_options::variables_map vm);
protected:
	uint samples_per_vector;
	std::vector<int> channels;
	pthread_t sampling_thread, receiving_thread;
	Amplifier * driver;
	Logger *logger;
	virtual bool fetch_samples();
};

#endif	/* AMPLIFIERSERVER_H */

