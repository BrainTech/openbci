/*
 * FileAmplifier.h
 *
 *  Created on: 19-03-2012
 *      Author: Macias
 */

#ifndef FILEAMPLIFIER_H_
#define FILEAMPLIFIER_H_

#include "Amplifier.h"
#include <fstream>
class FileAmplifier: public Amplifier {
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
	virtual double next_samples(bool synchonize=true);
	inline char * get_channel_data(){
		return channel_data+channel_data_index*channel_data_len;
	}

};
enum FileChannelType{
	DOUBLE,FLOAT,INT32,UINT32
};
class FileChannel:public Channel{
private:
	uint data_offset;
	FileChannelType type;

public:
	FileChannel(string name,uint offset,string type,FileAmplifier *amp);
	virtual	~FileChannel(){}
	inline int get_raw_sample(){
		return get_sample();
	}
	inline virtual float get_sample(){
		char * data=((FileAmplifier*)amplifier)->get_channel_data()+this->data_offset;
		switch (this->type){
		case DOUBLE:
			return *((double*)data);
		case FLOAT:
			return *((float*)data);
		case INT32:
			return *((int32_t*)data);
		case UINT32:
			return *((uint32_t*)data);
		}
	}
};
class FileAmplifierDescription:public AmplifierDescription{
public:
	FileAmplifierDescription(string name,FileAmplifier *amp,vector<string> names,
			vector<string>types,vector<string>gains,vector<string>offsets);
	uint channel_data_len;
};
class FileAmplifierException:public exception{
private:
	string message;
public:
	FileAmplifierException(string message):message(message){}
	virtual const char * what() const throw(){
		return message.c_str();
	}
	virtual ~FileAmplifierException() throw(){};
};
#endif /* FILEAMPLIFIER_H_ */
