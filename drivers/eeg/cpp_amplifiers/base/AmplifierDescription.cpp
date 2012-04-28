/*
 * AmplifierDescription.cpp
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */

#include "AmplifierDescription.h"
#include "Amplifier.h"
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
	if (channel->is_generated())
		add_generated_channel(channel);
	else physical_channels++;
}
vector<Channel*> AmplifierDescription::get_channels() {
	return channels;
}
AmplifierDescription::~AmplifierDescription() {
	clear_channels();
}
AmplifierDescription::AmplifierDescription(string name,Amplifier *driver):name(name),physical_channels(0),driver(driver) {}
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
			<< ", \"offset\": " << offset << ",\n \"idle\": " << get_idle();
	out << ", \"type\": \"" << get_type() << "\", \"unit\": \"" << get_unit();
	out << "\",\n \"other_params\": [";
	for (uint i=0;i<other_params.size();i++)
		out << (i!=0?",":"") << other_params[i];
	out << "]}";
	return out.str();
}
Channel::Channel(string name,Amplifier *amp) :
		amplifier(amp),name(name), gain(1.0), offset(0),is_signed(true),bit_length(32){
}
string Channel::get_idle() {
	ostringstream out;
	if (is_signed)
		out << (int) (-1 << (bit_length - 1));
	else
		out << (uint) (1 << (bit_length - 1));
	return out.str();
}
int SawChannel::get_raw_sample() {
	return amplifier->cur_sample;
}
double SinusChannel::get_value(){
	return sin((amplifier->cur_sample%period)*2*M_PI/period);
}
double CosinusChannel::get_value(){
	return cos((amplifier->cur_sample%period)*2*M_PI/period);
}
double ModuloChannel::get_value(){
	return (amplifier->cur_sample%period)/(double)period;
}

FunctionChannel::FunctionChannel(Amplifier *amp,uint period,string function_name):
	GeneratedChannel(function_name,amp){
	this->period=period;
	amplitude=rand()%100+1;
	char tmp[100];
	sprintf(tmp,"[%d]%dVolt-3",period,amplitude);
	name+=tmp;
	exp=(rand()%3+1)*(-3);
	for (int i=exp;i<-3;i++)
		amplitude*=10;
	uint max=1<<(rand()%22+10);
	gain=rand()%3+rand()/(float)RAND_MAX;
	offset=amplitude-max*gain;

//	cout <<"max: "<<max<<" amp:"<<amplitude<<" gain:"<< gain<<" offset:" << offset <<" a:" << a<< " b: "<<b << " i_g:" << i_g << " i_o:"<< i_o;
}
int FunctionChannel::get_raw_sample(){
	return(get_adjusted_sample()-offset)/gain;
//	printf("(%d * %f + %f) * %f + %f = %f  <=>  %f * %d = %f \n",temp,gain,offset,a,b,(temp*gain+offset)*a+b,get_value(),amplitude,get_value()*amplitude);
}
double FunctionChannel::get_adjusted_sample(){
	return get_value()*amplitude;
}
DummyAmpDesc::DummyAmpDesc(Amplifier *driver):AmplifierDescription("Dummy Amplifier",driver){

	add_channel(new SinusChannel(driver,128));
	add_channel(new CosinusChannel(driver,128));
	add_channel(new ModuloChannel(driver,128));
	add_channel(new FunctionChannel(driver,128));

	add_channel(new SinusChannel(driver,256));
	add_channel(new CosinusChannel(driver,256));
	add_channel(new ModuloChannel(driver,256));
	add_channel(new FunctionChannel(driver,256));

	add_channel(new SinusChannel(driver,512));
	add_channel(new CosinusChannel(driver,512));
	add_channel(new ModuloChannel(driver,512));
	add_channel(new FunctionChannel(driver,512));

	add_channel(new SinusChannel(driver,1024));
	add_channel(new CosinusChannel(driver,1024));
	add_channel(new ModuloChannel(driver,1024));
	add_channel(new FunctionChannel(driver,1024));

	add_channel(new SinusChannel(driver,1024));
	add_channel(new CosinusChannel(driver,1024));
	add_channel(new ModuloChannel(driver,1024));
	add_channel(new FunctionChannel(driver,1024));

	add_channel(new SinusChannel(driver,2048));
	add_channel(new CosinusChannel(driver,2048));
	add_channel(new ModuloChannel(driver,2048));
	add_channel(new FunctionChannel(driver,2048));

	add_channel(new SinusChannel(driver,4096));
	add_channel(new CosinusChannel(driver,4096));
	add_channel(new ModuloChannel(driver,4096));
	add_channel(new FunctionChannel(driver,4096));

	add_channel(new Channel("temp2",driver));
	SawChannel *saw=new SawChannel(driver);
	saw->name="Saw";
	add_channel(saw);
	add_channel(new SawChannel(driver));
	add_channel(new BoolChannel("Trigger",driver));
	sampling_rates.push_back(128);
	sampling_rates.push_back(256);
	sampling_rates.push_back(2048);
}

