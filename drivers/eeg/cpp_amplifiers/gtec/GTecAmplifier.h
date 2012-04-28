/*
 * GTecDriver.h
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#ifndef GTECDRIVER_H_
#define GTECDRIVER_H_

#include "Amplifier.h"

class GTecAmplifier: public Amplifier {
private:
	string name;
	vector<string> device_names;
	float * sample_data;
	pid_t simple_driver_id;
	int simple_driver_output;
	void spawn_simple_driver(const char * name);
	void wait_simple_driver();
public:
	GTecAmplifier();
	boost::program_options::options_description get_options();
	void init(boost::program_options::variables_map &vm);
	void start_sampling();
	void stop_sampling(bool disconnecting);
	double next_samples();
	virtual ~GTecAmplifier();
	void get_data();
};

#endif /* GTECDRIVER_H_ */
