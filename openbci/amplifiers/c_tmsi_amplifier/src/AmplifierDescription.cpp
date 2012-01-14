/*
 * AmplifierDescription.cpp
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */

#include "AmplifierDescription.h"
#include "AmplifierDriver.h"
#include "math.h"
#include <iostream>
#include <limits>
void AmplifierDescription::clear_channels() {
	while (channels.size()) {
		delete channels.back();
		channels.pop_back();
	}
}
void AmplifierDescription::add_channel(Channel * channel) {
	channels.push_back(channel);
}
vector<Channel*> AmplifierDescription::get_channels() {
	return channels;
}
AmplifierDescription::~AmplifierDescription() {
	clear_channels();
}
AmplifierDescription::AmplifierDescription(string name,AmplifierDriver *driver) {
	this->name = name;
	this->driver=driver;
}
vector<uint> AmplifierDescription::get_sampling_rates() {
	return sampling_rates;
}

string AmplifierDescription::get_name() {
	return name;
}

string AmplifierDescription::get_json() {
	stringstream out;
	out << "{\t\"name\":\"" << get_name() << "\",\n";
	out << "\t\"physical_channels\": " << get_physical_channels() << ",\n";
	out << "\t\"sampling_rates\":[";
	for (uint i = 0; i < sampling_rates.size(); i++) {
		if (i)
			out << ',';
		out << sampling_rates[i];
	}
	out << "],\n\t\"channels\": [";
	for (uint i = 0; i < channels.size(); i++)
		out << (i ? ",\n\t\t" : "\t\t") << channels[i]->get_json();
	out << "]}";
	return out.str();
}
Channel * AmplifierDescription::find_channel(string channel) {
	istringstream stream(channel);
	int tmp;
	if (!((stream >> tmp).fail())) {
		if (tmp < 0)
			return generated_channel(-tmp);
		else if ((uint) tmp < channels.size())
			return channels[tmp];
	}
	for (uint j = 0; j < channels.size(); j++)
		if (channels[j]->name == channel)
			return channels[j];
	return NULL;
}

NoSuchChannel::~NoSuchChannel() throw () {
}
string Channel::get_json() {
	ostringstream out;
	out.setf(ios::scientific, ios::floatfield);
	out.precision(numeric_limits<double>::digits10+1);
	out << "{\"name\": \"" << name << "\", \"gain\": " << gain
			<< ", \"offset\": " << offset << ",\n \"a\": " << a;
	out << ", \"b\": " << b << ", \"idle\": " << get_idle();
	out << ", \"type\": \"" << get_type() << "\", \"unit\": \"" << get_unit()
			<< "\"}";
	return out.str();
}
Channel::Channel(string name) :
		name(name), gain(1.0), offset(0), a(1.0), b(0) {
}
string Channel::get_idle() {
	ostringstream out;
	if (is_signed)
		out << (int) (-1 << (bit_length - 1));
	else
		out << (uint) (1 << (bit_length - 1));
	return out.str();
}
int SawChannel::get_sample_int() {
	return amplifier->get_driver()->cur_sample;
}
double SinusChannel::get_value(){
	return sin((amplifier->get_driver()->cur_sample%period)*2*M_PI/period);
}
double CosinusChannel::get_value(){
	return cos((amplifier->get_driver()->cur_sample%period)*2*M_PI/period);
}
double ModuloChannel::get_value(){
	return (amplifier->get_driver()->cur_sample%period)/(double)period;
}

FunctionChannel::FunctionChannel(AmplifierDescription *amp,uint period,string function_name):
	GeneratedChannel(function_name,amp){
	this->period=period;
	amplitude=rand()%100+1;
	char tmp[100];
	sprintf(tmp,"[%d]%dVolt-3",period,amplitude);

	exp=(rand()%3+1)*(-3);
	for (int i=exp;i<-3;i++)
		amplitude*=10;
	uint max=1<<(rand()%22+10);
	offset=rand()%32000+rand()/(float)RAND_MAX;
	gain=rand()%4+rand()/(float)RAND_MAX;
	a=((double)amplitude)/gain/max;
	b=-offset*a;
	name+=tmp;
	i_g=1/(gain*a);
	i_o=-(b-offset*a)/(gain*a);
//	cout <<"max: "<<max<<" amp:"<<amplitude<<" gain:"<< gain<<" offset:" << offset <<" a:" << a<< " b: "<<b << " i_g:" << i_g << " i_o:"<< i_o;
}
int FunctionChannel::get_sample_int(){
	int temp= get_sample_double()*i_g+i_o;
	return temp;
//	printf("(%d * %f + %f) * %f + %f = %f  <=>  %f * %d = %f \n",temp,gain,offset,a,b,(temp*gain+offset)*a+b,get_value(),amplitude,get_value()*amplitude);

}
double FunctionChannel::get_sample_double(){
	return get_value()*amplitude;
}
DummyAmplifier::DummyAmplifier(AmplifierDriver *driver):AmplifierDescription("Dummy Amplifier",driver){

	add_channel(new SinusChannel(this,128));
	add_channel(new CosinusChannel(this,128));
	add_channel(new ModuloChannel(this,128));
	add_channel(new FunctionChannel(this,128));

	add_channel(new SinusChannel(this,256));
	add_channel(new CosinusChannel(this,256));
	add_channel(new ModuloChannel(this,256));
	add_channel(new FunctionChannel(this,256));

	add_channel(new SinusChannel(this,512));
	add_channel(new CosinusChannel(this,512));
	add_channel(new ModuloChannel(this,512));
	add_channel(new FunctionChannel(this,512));

	add_channel(new SinusChannel(this,1024));
	add_channel(new CosinusChannel(this,1024));
	add_channel(new ModuloChannel(this,1024));
	add_channel(new FunctionChannel(this,1024));

	add_channel(new SinusChannel(this,1024));
	add_channel(new CosinusChannel(this,1024));
	add_channel(new ModuloChannel(this,1024));
	add_channel(new FunctionChannel(this,1024));

	add_channel(new SinusChannel(this,2048));
	add_channel(new CosinusChannel(this,2048));
	add_channel(new ModuloChannel(this,2048));
	add_channel(new FunctionChannel(this,2048));

	add_channel(new SinusChannel(this,4096));
	add_channel(new CosinusChannel(this,4096));
	add_channel(new ModuloChannel(this,4096));
	add_channel(new FunctionChannel(this,4096));

	add_channel(new Channel("temp2"));
	add_channel(new SawChannel(this));
	add_channel(new BoolChannel("Trigger",this));
	sampling_rates.push_back(128);
	sampling_rates.push_back(256);
	sampling_rates.push_back(2048);
}

