/*
 * FileAmplifier.h
 *
 *  Created on: 19-03-2012
 *      Author: Macias
 */

#ifndef FILEAMPLIFIER_H_
#define FILEAMPLIFIER_H_

#include "AmplifierDriver.h"
#include <fstream>
class FileAmplifier: public AmplifierDriver {
private:
	char * channel_data;
	uint channel_data_index;
	uint channel_data_len;
	streamsize data_len;
	uint pack_size;
	ifstream samples;
	inline uint get_pack_size();
public:
	string file_path;
	FileAmplifier();
	virtual ~FileAmplifier();
	virtual boost::program_options::options_description get_options();
	virtual void init(boost::program_options::variables_map &vm);
	virtual double next_samples();
	inline char * get_channel_data();
};
enum FileChannelType{
	DOUBLE,FLOAT,INT32,UINT32
};
class FileChannel:public Channel{
private:
	FileAmplifier *amplifier;
	uint offset;
	FileChannelType type;

public:
	FileChannel(string name,uint offset,string type,FileAmplifier *amp);
	virtual	~FileChannel(){}
	inline virtual int get_raw_sample();
	inline virtual float get_sample();
};
class FileAmplifierDescription:public AmplifierDescription{
public:
	FileAmplifierDescription(string name,FileAmplifier *amp,vector<string> names,vector<string>types);
	uint channel_data_len;
};
class FileAmplifierException:public exception{
private:
	string message;
public:
	FileAmplifierException(string message):message(message){}
	const char * what(){
		return message.c_str();
	}
	virtual ~FileAmplifierException() throw(){};
};
#endif /* FILEAMPLIFIER_H_ */
