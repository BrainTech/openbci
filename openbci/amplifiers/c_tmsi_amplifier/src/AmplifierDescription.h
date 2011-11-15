/*
 * AmplifierDescription.h
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */

#ifndef AMPLIFIERDESCRIPTION_H_
#define AMPLIFIERDESCRIPTION_H_
#include <vector>
#include <string>
#include <sstream>
#include <typeinfo>
#include <stdlib.h>
using namespace std;
class Channel;
class AmplifierDriver;
class AmplifierDescription {
private:
	string name;
	vector<Channel *> channels;
	vector<Channel *> generated_channels;
protected:
	uint physical_channels;
	vector<uint> sampling_rates;
	AmplifierDriver *driver;
public:
	AmplifierDescription(string name,AmplifierDriver *);
	virtual ~AmplifierDescription();
	virtual vector<uint> get_sampling_rates();
	virtual string get_name();
	virtual string get_json();
	vector<Channel *> get_channels();
	void add_channel(Channel * channel);
	void add_generated_channel(Channel *channel){
		generated_channels.push_back(channel);
	}
	void clear_channels();
	virtual Channel* generated_channel(uint index) {
			if (index<generated_channels.size())
				return generated_channels[index];
			return NULL;
		}
	virtual Channel *find_channel(string channel);
	uint get_physical_channels(){
		return physical_channels;
	}
	inline AmplifierDriver * get_driver(){
		return driver;
	}
};

class Channel {
public:
	string name;
	Channel(string name);
	float gain;
	float offset;
	virtual string get_type() {
		return "UNKNOWN";
	}
	virtual string get_unit() {
		return "Unknown";
	}

	bool is_signed;
	short bit_length;
	virtual string get_idle();
	float a; // Information for converting bits to units:
	float b; // Unit  = a * Bits  + b ;

	short exp; // Unit exponent, 3 for Kilo, -6 for micro, etc.
	virtual string get_json();
	virtual ~Channel(){}
	virtual inline int get_sample_int(){
		return rand() % 100;
	}
	virtual inline double get_sample_double(){
		return get_sample_int();
	}
	inline void fill_sample(int *sample) {
			(*sample) = get_sample_int();
		}
	inline void fill_sample(uint *sample){
		int tmp;
		fill_sample(&tmp);
		(*sample)=tmp;
	}
	inline void fill_sample(double *sample){
		(*sample)=get_sample_double();
	}
};
class GeneratedChannel:public Channel{
protected:
	AmplifierDescription * amplifier;
public:
	GeneratedChannel(string name,AmplifierDescription *amp):Channel(name){
		this->amplifier=amp;
		this->amplifier->add_generated_channel(this);
		is_signed=0;
		a=1;
		b=0;
		gain=1;
		offset=0;
	}
};
class BoolChannel: public GeneratedChannel {
public:
	BoolChannel(string name,AmplifierDescription *amp):GeneratedChannel(name,amp){
		bit_length=1;

	}
	virtual string get_type() {
		return "Boolean";
	}
	virtual string get_unit() {
		return "Bit";
	}
	virtual void fill_sample(int *sample) {
		(*sample) = rand() % 2;
	}
};
class SawChannel: public GeneratedChannel {
public:
	SawChannel(AmplifierDescription *amp,string name = "Driver_Saw") :
		GeneratedChannel(name,amp) {
		bit_length=32;
	}
	int get_sample_int();
	virtual string get_unit(){
		return "Integer";
	}
	virtual string get_type(){
		return "ZAAG";
	}
};
class NoSuchChannel: public exception {
	string name;
public:
	NoSuchChannel(string& name) throw() {
		this->name = "No such channel or channel index not in range: "+name;
	}
	virtual const char* what() const throw () {
		return name.c_str();
	}
	virtual ~NoSuchChannel() throw ();
};
#endif /* AMPLIFIERDESCRIPTION_H_ */
