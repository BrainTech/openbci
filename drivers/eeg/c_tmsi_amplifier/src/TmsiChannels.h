#ifndef TMSICHANNELS_H
#define	TMSICHANNELS_H

#define DIGI_CHANNEL 4
#define ON_OFF_BUTTON 0x01
#define TRIGGER_ACTIVE 0x04
#define BATTERY_LOW 0x40


#include <vector>
#include <string>
#include "nexus/tmsi.h"
#include "AmplifierDescription.h"
#include "TmsiDriverDesc.h"

using namespace std;
class TmsiAmplifier;
class AmplifierDescription;
class TmsiDriverDesc;

class TmsiChannel: public Channel{
private:
	uint subtype;
	uint type;
	uint unitId;
protected:
	TmsiAmplifier *amplifier;
	uint index;

public:
    TmsiChannel(tms_channel_desc_t & t_chan,TmsiAmplifier * amplifier,uint index):Channel(t_chan.ChannelDescription){
    	gain = t_chan.Type.a;
        offset = t_chan.Type.b;
        other_params.push_back(t_chan.GainCorrection);
        other_params.push_back(t_chan.OffsetCorrection);
        other_params.push_back(t_chan.Type.a);
        other_params.push_back(t_chan.Type.b);
        exp = t_chan.Type.Exp;
        type = t_chan.Type.Type;
        subtype = t_chan.Type.SubType;
        is_signed = t_chan.Type.Format & 0x100;
        bit_length = t_chan.Type.Format & 0xFF;
        unitId=t_chan.Type.UnitId;
        this->amplifier=amplifier;
        this->index=index;
        if (get_main_type()=="ZAAG")
        	name="Saw";
    }
    virtual string get_main_type(){
    	switch (type) {
			case 0: return "UNKNOWN";
			case 1: return "EXG";
			case 2: return "BIP";
			case 3: return "AUX";
			case 4: return "DIG";
			case 5: return "TIME";
			case 6: return "LEAK";
			case 7: return "PRESSURE";
			case 8: return "ENVELOPE";
			case 9: return "MARKER";
			case 10: return "ZAAG";
			case 11: return "SAO2";
		}
		return "UNKNOWN";
    }
    virtual string get_subtype() {
        switch (subtype) {
            case 0: return "";
            case 1: return "EEG";
            case 2: return "EMG";
            case 3: return "ECG";
            case 4: return "EOG";
            case 5: return "EAG";
            case 6: return "EGG";
            case 257: return "EEGREF"; //	(for specific unipolar reference)";
            case 10: return "resp";
            case 11: return "flow";
            case 12: return "snore";
            case 13: return "position";
            case 522: return "resp/impref"; // (impedance reference)";
            case 20: return "SaO2";
            case 21: return "plethysmogram";
            case 22: return "heartrate";
            case 23: return "sensor status";
            case 30: return "PVES";
            case 31: return "PURA";
            case 32: return "PABD";
            case 33: return "PDET";
        }
        return "Unknown";
    }
    virtual string get_type();

    virtual string get_main_unit() {
        switch (unitId){
        case 0: return "bit";
        case 1: return "Volt";
        case 2: return "%";
        case 3: return "Bpm";
        case 4: return "Bar";
        case 5: return "Psi";
        case 6: return "mH2O";
        case 7: return "mHg";
        case 8: return "bit";
        }
        return "Unknown";
    }
    virtual string get_unit(){
    	ostringstream out;
    	out << get_main_unit();
    	if (exp)
    		out <<" "<<exp;
    	return out.str();
    }
    int get_raw_sample();
};
class DigiChannel:public TmsiChannel{
public:
	DigiChannel(tms_channel_desc_t & t_chan,TmsiAmplifier * amplifier,uint index):TmsiChannel(t_chan,amplifier,index){}
	int get_raw_sample();
};
class SpecialChannel:public GeneratedChannel{
	uint mask;
public:
	SpecialChannel(string name,uint mask,TmsiDriverDesc *description);
	virtual int get_raw_sample();
	virtual string get_type(){
		return "BITMAP";
	}
	virtual string get_unit(){
		return "bit";
	}
};
class OnOffChannel:public SpecialChannel{
public:
	OnOffChannel(TmsiDriverDesc *description):SpecialChannel("onoff",ON_OFF_BUTTON,description){}
};
class TriggerChannel:public SpecialChannel{
public:
	TriggerChannel(TmsiDriverDesc *description):SpecialChannel("trig",TRIGGER_ACTIVE,description){}
};
class BatteryChannel:public SpecialChannel{
public:
	BatteryChannel(TmsiDriverDesc *description):SpecialChannel("bat",BATTERY_LOW,description){}
};

#endif
