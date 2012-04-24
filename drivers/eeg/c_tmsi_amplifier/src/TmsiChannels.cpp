/*
 * TmsiChannels.cpp
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */
#include "TmsiChannels.h"
#include "TmsiAmplifier.h"
#include "TmsiDriverDesc.h"
string TmsiChannel::get_type(){
	return get_main_type()+" "+get_subtype();
}
int TmsiChannel::get_raw_sample(){
	return ((TmsiAmplifier*)amplifier)->get_sample_int(index);
}
int DigiChannel::get_raw_sample(){
	return ((TmsiAmplifier*)amplifier)->get_digi(index);
}
int SpecialChannel::get_raw_sample(){
		vector<Channel *> digi_chan=((TmsiDriverDesc*)amplifier->get_description())->get_digi_channels();
		uint res=0;
		uint tmp;
		for (uint i=0;i<digi_chan.size();i++){
			res=(res<<1);
			tmp=digi_chan[i]->get_raw_sample();
			if (tmp&mask)
				res|=1;
		}
		return res;
	}

SpecialChannel::SpecialChannel(string name,uint mask,TmsiAmplifier *amp):GeneratedChannel(name,amp){
		this->bit_length=((TmsiDriverDesc*)amplifier->get_description())->get_digi_channels().size();
		this->mask=mask;
		}
