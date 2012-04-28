/*
 * GTecDescription.h
 *
 *  Created on: 23-04-2012
 *      Author: Macias
 */

#ifndef GTECDESCRIPTION_H_
#define GTECDESCRIPTION_H_

#include "AmplifierDescription.h"

class GTecChannel: public Channel{
	float scale;
	float g_offset;
	float cur_sample;
public:
	GTecChannel(uint index,float scale,float offset,Amplifier *amp):Channel("",amp),scale(scale),g_offset(offset){
		char tmp[20];
		sprintf(tmp,"Analog %d",index);
		name=tmp;
		other_params.push_back(scale);
		other_params.push_back(offset);
	}
	inline int get_raw_sample(){
		return get_sample()/scale+g_offset;
	}

	virtual inline float get_sample(){
		return cur_sample;
	}
	virtual inline double get_adjusted_sample(){
		return get_sample();
	}
	inline void set_sample(float sample){
		cur_sample=sample;
	}
	virtual string get_type() {
			return "Analog";
		}
	virtual string get_unit() {
			return "Volt-6";
		}
};

class GTecDescription: public AmplifierDescription {
public:
	GTecDescription(string name,Amplifier* driver);
	virtual ~GTecDescription();
};

#endif /* GTECDESCRIPTION_H_ */
