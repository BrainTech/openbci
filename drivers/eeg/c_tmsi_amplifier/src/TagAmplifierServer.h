/*
 * TagAmplifierServer.h
 *
 *  Created on: 13-04-2012
 *      Author: Macias
 */

#ifndef TAGAMPLIFIERSERVER_H_
#define TAGAMPLIFIERSERVER_H_

#include "AmplifierServer.h"

class SerializedTag{
public:
	double timestamp;
	int type;
	string data;
	SerializedTag(string str="");
	SerializedTag(double timestamp,int type, string data):timestamp(timestamp),type(type),data(data){}
	static SerializedTag* parseTag(string str);
	static vector<SerializedTag*> parseTags(string str);
	bool send(double sample_time);
};
istream & operator>>(istream in,SerializedTag &tag);

class TagAmplifierServer: public AmplifierServer {
private:
	vector<SerializedTag*> tags;
	double first_timestamp;
public:
	TagAmplifierServer(AmplifierDriver* driver):AmplifierServer(driver),first_timestamp(-1){}
	virtual ~TagAmplifierServer();
	void set_tags(vector<SerializedTag*> tags);
	virtual bool do_command(string command,istream& cin);
	string get_commands();
protected:
	virtual bool fetch_samples();
};

#endif /* TAGAMPLIFIERSERVER_H_ */
