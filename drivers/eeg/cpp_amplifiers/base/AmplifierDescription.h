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
#include <iostream>
#include <sstream>
#include <typeinfo>
#include <stdlib.h>
#include <stdio.h>
using namespace std;
class Channel;
class Amplifier;
class AmplifierDescription {
private:
	
	vector<Channel *> channels;
	vector<Channel *> generated_channels;
protected:
	uint physical_channels;
	vector<uint> sampling_rates;
	Amplifier *driver;
	string name;
public:
	AmplifierDescription(string name,Amplifier *);
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
	inline Amplifier * get_driver(){
		return driver;
	}
};
class DummyAmpDesc:public AmplifierDescription{
public:
	DummyAmpDesc(Amplifier *driver);
};


class Channel {
protected:
	Amplifier * amplifier;
public:
	string name;
	vector<double> other_params;
	Channel(string name,Amplifier * amp);
	double gain;
	double offset;
	virtual string get_type() {
		return "UNKNOWN";
	}
	virtual string get_unit() {
		return "Unknown";
	}

	bool is_signed;
	short bit_length;
	virtual string get_idle();

	short exp; // Unit exponent, 3 for Kilo, -6 for micro, etc.
	virtual string get_json();
	virtual ~Channel(){}

	virtual inline int get_raw_sample(){
		return rand() % 100;
	}

	virtual inline float get_sample(){
		return get_raw_sample();
	}
	virtual inline double get_adjusted_sample(){
		return get_raw_sample()*gain+offset;
	}
	virtual inline bool is_generated(){
		return false;
	}
};
class GeneratedChannel:public Channel{
	AmplifierDescription * desc;
public:
	GeneratedChannel(string name,Amplifier *amp):Channel(name,amp){
		is_signed=0;
	}
	inline bool is_generated(){
		return true;
	}
};
class BoolChannel: public GeneratedChannel {
public:
	BoolChannel(string name,Amplifier *amp):GeneratedChannel(name,amp){
		bit_length=1;

	}
	virtual string get_type() {
		return "Boolean";
	}
	virtual string get_unit() {
		return "Bit";
	}
	int get_raw_sample(){
		return rand()%2;
	}
};
class SawChannel: public GeneratedChannel {
public:
	SawChannel(Amplifier *amp,string name = "Driver_Saw") :
		GeneratedChannel(name,amp) {
		bit_length=32;
	}
	int get_raw_sample();
	virtual string get_unit(){
		return "Integer";
	}
	virtual string get_type(){
		return "ZAAG";
	}
};
class FunctionChannel: public GeneratedChannel{
	uint amplitude;
	uint exp;
public:
	FunctionChannel(Amplifier *amp,uint period,string name="Random");
	string get_unit(){
		char tmp[100];
		sprintf(tmp,"Volt %d",exp);
		return tmp;
	}
	int get_raw_sample();
	double get_adjusted_sample();
protected:
	uint period;
	virtual double get_value(){return (rand()%period)/(float)period;}
};
class SinusChannel:public FunctionChannel{
public:
	SinusChannel(Amplifier *amp,uint period):FunctionChannel(amp,period,"Sinus"){};
protected:
	virtual double get_value();
};

class CosinusChannel:public FunctionChannel{
public:
	CosinusChannel(Amplifier *amp,uint period):FunctionChannel(amp,period,"Cos"){};
protected:
	virtual double get_value();
};
class ModuloChannel:public FunctionChannel{
public:
	ModuloChannel(Amplifier *amp,uint period):FunctionChannel(amp,period,"Modulo"){};
protected:
	virtual double get_value();
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
