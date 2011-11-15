/*
 * AmplifierDescription.cpp
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */

#include "AmplifierDescription.h"
#include "AmplifierDriver.h"
#include <iostream>
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
	out.setf(ios::fixed, ios::floatfield);
	cout.precision(10);
	out << "{\"name\": \"" << name << "\", \"gain\": " << gain
			<< ", \"offset\": " << offset << ",\n \"a\": " << a;
	out << ", \"b\": " << b << ", \"idle\": " << get_idle();
	out << ", \"type\": \"" << get_type() << "\", \"unit\": \"" << get_unit()
			<< "\"}";
	return out.str();
}
Channel::Channel(string name) :
		name(name), gain(0), offset(0), a(0), b(0) {
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
