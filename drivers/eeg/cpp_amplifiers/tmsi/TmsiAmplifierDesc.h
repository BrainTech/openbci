/*
 * TmsiAmplifierDesc.h
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */

#ifndef TmsiAmplifierDesc_H_
#define TmsiAmplifierDesc_H_
#include "AmplifierDescription.h"
#include "TmsiChannels.h"
class TmsiAmplifier;
class TmsiAmplifierDesc:public AmplifierDescription{
	vector<Channel *> digi_channels;
public:
	TmsiAmplifierDesc(tms_input_device_t &dev,TmsiAmplifier *amp);
	inline vector<Channel *> get_digi_channels(){
		return digi_channels;
	}
};

#endif /* TmsiAmplifierDesc_H_ */
