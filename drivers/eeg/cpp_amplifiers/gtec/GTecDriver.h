/*
 * GTecDriver.h
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#ifndef GTECDRIVER_H_
#define GTECDRIVER_H_

#include "../AmplifierDriver.h"
//#include "semaphore.h"
//class BufferData{
//	char *data;
//	uint size;
//	uint valid;
//};
//class CircularBuffer{
//	vector<char> data;
//	uint read;
//	uint write;
//public:
//	void write(char *,uint size);
//
//	void read(char *,uint size);
//
//};

class GTecDriver: public AmplifierDriver {
private:
	string name;
	vector<string> device_names;
//	CircularBuffer data;
	float * sample_data;
	pid_t simple_driver_id;
	int simple_driver_output;
	void spawn_simple_driver(const char * name);
	void wait_simple_driver();
public:
	GTecDriver();
	boost::program_options::options_description get_options();
	void init(boost::program_options::variables_map &vm);
	void start_sampling();
	void stop_sampling(bool disconnecting);
	double next_samples();
	virtual ~GTecDriver();
	void get_data();
};

#endif /* GTECDRIVER_H_ */
