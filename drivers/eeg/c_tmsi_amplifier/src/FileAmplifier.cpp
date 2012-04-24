/*
 * FileAmplifier.cpp
 *
 *  Created on: 19-03-2012
 *      Author: Macias
 */

#include "FileAmplifier.h"
namespace po=boost::program_options;
FileAmplifier::FileAmplifier():channel_data(NULL),pack_size(1) {
	// TODO Auto-generated constructor stub
	logger.name="FileAmplifier";
}

FileAmplifier::~FileAmplifier() {
	if (channel_data!=NULL)
		delete channel_data;
	channel_data=NULL;

}
inline uint FileAmplifier::get_pack_size(){
	return sampling_rate;
}
boost::program_options::options_description FileAmplifier::get_options(){
	po::options_description options("FileAmplifier Options");
	options.add_options()
				("file,f",po::value<string>(&file_path),"Path to a file with sample data")
				("channel_names,n",po::value<string>(),"Names of channels in the file separated by semicolons")
				("channel_types,t",po::value<string>(),
						"String with channel types separated by semicolons");
	return AmplifierDriver::get_options().add(options);
}
void FileAmplifier::init(boost::program_options::variables_map &vm){
	FileAmplifierDescription * desc=new FileAmplifierDescription(file_path,this,
			split_string(vm["channel_names"].as<string>(),';'),
			split_string(vm["channel_types"].as<string>(),';'));
	set_description(desc);
	AmplifierDriver::init(vm);
	samples.open(file_path.c_str(),ios::in);
	if (!samples)
		throw new FileAmplifierException("Could not open file: "+file_path);
	pack_size=get_pack_size();
	channel_data_len=desc->channel_data_len;
	channel_data=new char[pack_size*channel_data_len];
	channel_data_index=pack_size;
	data_len=0;
}
double FileAmplifier::next_samples(){
	channel_data_index++;
	if (channel_data_index*channel_data_len>=data_len){
		channel_data_index=0;
		samples.read(channel_data,pack_size*channel_data_len);
		data_len=samples.gcount();
		if (data_len==0){
			stop_sampling();
			return 0.0;
		}
	}
	return AmplifierDriver::next_samples();
}

FileChannel::FileChannel(string name,uint offset, string type,FileAmplifier *amp):Channel(name,amp){
	this->offset=offset;
	if (type=="double"){
		this->bit_length=64;
		this->type=DOUBLE;
	}else if (type=="float"){
		this->type=FLOAT;
	}else if (type=="int32"){
		this->type = INT32;
	}else if (type=="uint32"){
		this->is_signed = false;
		this->type = UINT32;
	}
}
FileAmplifierDescription::FileAmplifierDescription(string name,FileAmplifier *amp,vector<string> names,vector<string>types):AmplifierDescription(name,amp){
	if (names.size()>types.size())
		throw new FileAmplifierException("Not enough channel types!");
	if (names.size()<types.size())
		throw new FileAmplifierException("To many channel types!");
	uint offset=0;
	for (uint i=0;i<names.size();i++){
		FileChannel * channel=new FileChannel(names[i],offset,types[i],amp);
		add_channel(channel);
		offset+=channel->bit_length/8;
	}
	sampling_rates.push_back(amp->get_sampling_rate());
	channel_data_len=offset;
}
