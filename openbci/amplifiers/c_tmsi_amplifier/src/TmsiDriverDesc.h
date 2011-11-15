/*
 * TmsiDriverDesc.h
 *
 *  Created on: 09-11-2011
 *      Author: Macias
 */

#ifndef TMSIDRIVERDESC_H_
#define TMSIDRIVERDESC_H_
#include "AmplifierDescription.h"
#include "TmsiChannels.h"
class TmsiAmplifier;
class TmsiDriverDesc:public AmplifierDescription{
	vector<Channel *> digi_channels;
public:
	TmsiDriverDesc(tms_input_device_t &dev,TmsiAmplifier *amp);
	inline vector<Channel *> get_digi_channels(){
		return digi_channels;
	}
};

#endif /* TMSIDRIVERDESC_H_ */
