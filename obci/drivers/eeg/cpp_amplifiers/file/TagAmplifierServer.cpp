/*
 * TagAmplifierServer.cpp
 *
 *  Created on: 13-04-2012
 *      Author: Macias
 */

#include "TagAmplifierServer.h"
#include <algorithm>
#include <iomanip>
bool SerializedTag::send(double sample_time){
//	MultiplexerMessage msg;
//	msg.set_from(conn->instance_id());
//	msg.set_type(type);
//	msg.set_id(conn->random64());
//	msg.set_message(data);
	cout<<setprecision(15)<<get_time_as_double()<<"\n";

	cout.flush();
//	cerr<<"Sending Tag at "<<sample_time<<" type "<<type<<" data:"<<data<<"\n";
//	Client::ScheduledMessageTracker tracker = conn->schedule_one(msg);
//	if (!tracker) {
//		fprintf(stderr,"Error: Tag Sending failed.\n");
//		return false;
//	  }
	return true;
}
SerializedTag* SerializedTag::parseTag(string str){
	istringstream ss(str);
	double ts;
	ss >> ts;
	return new SerializedTag(ts,1,"Tag"+str);
}
vector<SerializedTag*> SerializedTag::parseTags(string str){
	vector<SerializedTag *> res;
	vector<string> timestamps=split_string(str,';');
	for (size_t i=0;i<timestamps.size();i++)
		res.push_back(parseTag(timestamps[i]));
	return res;
}
void TagAmplifierServer::delete_tags(){
	while (tags.size()>0){
			delete tags.back();
			tags.pop_back();
		}
}

TagAmplifierServer::~TagAmplifierServer() {
	delete_tags();
}

bool TagAmplifierServer::fetch_samples(){
	if (AmplifierServer::fetch_samples()){
		double time = driver->get_sample_timestamp();

		if (first_timestamp<=0){
			logger->info()<<"First Sample at: "<<setprecision(10)<<time;
			first_timestamp=time;
		}
		time=time-first_timestamp;
		while (tags.size()>0 && tags.back()->timestamp<=time+2.0/driver->get_sampling_rate()){
			if (!tags.back()->send(time)) return false;
			delete tags.back();
			tags.pop_back();
		}
		return true;
	}
	else return false;
}
void TagAmplifierServer::set_tags(vector<SerializedTag*> tags){
	this->tags=tags;
	reverse(this->tags.begin(),this->tags.end());
}
#define BUF_SIZE 1000000
bool TagAmplifierServer::do_command(string command,istream &cin){
	if (AmplifierServer::do_command(command,cin))
		return true;
	if (command=="tags_start"){
		string buf;
		cin.exceptions(istream::failbit|istream::badbit|istream::eofbit);
		delete_tags();
		while (true){
			getline(cin,buf);
			if (buf.substr(0,8)=="tags_end")
				break;
			istringstream line(buf);
			while (line)
			{
				string tag;
				getline(line,tag,';');
				if (tag.length()>0)
					this->tags.push_back(SerializedTag::parseTag(tag));
			}
		}
		cin.exceptions(istream::goodbit);
		reverse(this->tags.begin(),this->tags.end());
		return true;
	}
	return false;
}
string TagAmplifierServer::get_commands(){
	return AmplifierServer::get_commands()+", tags_start \\n<semicolon_separated_timestamps>\\ntags_end";
}
