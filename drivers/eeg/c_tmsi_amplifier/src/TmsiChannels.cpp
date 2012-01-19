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
int TmsiChannel::get_sample_int(){
	return amplifier->get_sample_int(index);
}
//double TmsiChannel::get_sample_double(){
//	return amplifier->get_sample_double(index);
//}
int DigiChannel::get_sample_int(){
	return amplifier->get_digi(index);
}
double DigiChannel::get_sample_double(){
	return get_sample_int();
}
int SpecialChannel::get_sample_int(){
		vector<Channel *> digi_chan=((TmsiDriverDesc*)amplifier)->get_digi_channels();
		uint res=0;
		uint tmp;
		for (uint i=0;i<digi_chan.size();i++){
			res=(res<<1);
			digi_chan[i]->fill_sample(&tmp);
			if (tmp&mask)
				res|=1;
		}
		return res;
	}

SpecialChannel::SpecialChannel(string name,uint mask,TmsiDriverDesc *description):GeneratedChannel(name,description){
		this->bit_length=description->get_digi_channels().size();
		this->mask=mask;
		}
