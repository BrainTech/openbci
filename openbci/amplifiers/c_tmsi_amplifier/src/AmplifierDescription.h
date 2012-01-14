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
class DummyAmplifier:public AmplifierDescription{
public:
	DummyAmplifier(AmplifierDriver *driver);
};


class Channel {
public:
	string name;
	Channel(string name);
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
	double a; // Information for converting bits to units:
	double b; // Unit  = a * Bits  + b ;

	short exp; // Unit exponent, 3 for Kilo, -6 for micro, etc.
	virtual string get_json();
	virtual ~Channel(){}
	virtual inline int get_sample_int(){
		return rand() % 100;
	}
	virtual inline double get_sample_double(){
		return (get_sample_int()*gain+offset)*a+b;
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
class FunctionChannel: public GeneratedChannel{
	uint amplitude;
	uint exp;
	double i_g,i_o;
public:
	FunctionChannel(AmplifierDescription *amp,uint period,string name="Random");
	string get_unit(){
		char tmp[100];
		sprintf(tmp,"Volt %d",exp);
		return tmp;
	}
	int get_sample_int();
	double get_sample_double();
protected:
	uint period;
	virtual double get_value(){return (rand()%period)/(float)period;}
};
class SinusChannel:public FunctionChannel{
public:
	SinusChannel(AmplifierDescription *amp,uint period):FunctionChannel(amp,period,"Sinus"){};
protected:
	virtual double get_value();
};

class CosinusChannel:public FunctionChannel{
public:
	CosinusChannel(AmplifierDescription *amp,uint period):FunctionChannel(amp,period,"Cos"){};
protected:
	virtual double get_value();
};
class ModuloChannel:public FunctionChannel{
public:
	ModuloChannel(AmplifierDescription *amp,uint period):FunctionChannel(amp,period,"Modulo"){};
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
