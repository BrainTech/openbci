/* 
 * File:   TmsiAmplifier.h
 * Author: Macias
 *
 * Created on 13 październik 2010, 13:14
 */

#ifndef TMSIAMPLIFIER_H
#define	TMSIAMPLIFIER_H
#include <string>
#include <vector>

#include "nexus/tmsi.h"
#include "AmplifierDriver.h"

#define BLUETOOTH_AMPLIFIER 1
#define USB_AMPLIFIER 2
#define MESSAGE_SIZE 1024*1024
#define ON_OFF_BUTTON 0x01
#define TRIGGER_ACTIVE 0x04
#define BATTERY_LOW 0x40

using namespace std;

struct channel_desc {
    string name;
    float gain;
    float offset;
    int type; // Channel type id code
    //	0 UNKNOWN
    //	1 EXG
    //	2 BIP
    //	3 AUX
    //	4 DIG
    //	5 TIME
    //	6 LEAK
    //	7 PRESSURE
    //	8 ENVELOPE
    //	9 MARKER
    //	10 ZAAG
    //	11 SAO2
    int subtype; // Channel subtype
    // (+256: unipolar reference, +512: impedance reference)
    //	.0 Unknown
    //	.1 EEG
    //	.2 EMG
    //	.3 ECG
    //	.4 EOG
    //	.5 EAG
    //	.6 EGG
    //	.257 EEGREF	(for specific unipolar reference)
    //	.10 resp
    //	.11 flow
    //	.12 snore
    //	.13 position
    //	.522 resp/impref (impedance reference)
    //	.20 SaO2
    //	.21 plethysmogram
    //	.22 heartrate
    //	.23 sensor status
    //	.30 PVES
    //	.31 PURA
    //	.32 PABD
    //	.33 PDET
    bool is_signed;
    short bit_length;
    float a; // Information for converting bits to units:
    float b; // Unit  = a * Bits  + b ;
    short unitId; // Id identifying the units
    //	0 bit (no unit) (do not use with front6)
    //	1 Volt
    //	2 %
    //	3 Bpm
    //	4 Bar
    //	5 Psi
    //	6 mH2O
    //	7 mHg
    //	8 bit
    short exp; // Unit exponent, 3 for Kilo, -6 for micro, etc.

};
class TmsiAmplifier:public AmplifierDriver {
private:
    int fd,read_fd; //device descriptor
    vector<channel_desc> channels_desc;
    tms_frontendinfo_t fei;
    tms_vldelta_info_t vli;
    tms_input_device_t dev;
    tms_acknowledge_t ack;
    tms_rtc_t rtc;
    tms_channel_data_t *channel_data;
    uint8_t msg[MESSAGE_SIZE];
    int br; //actual msg length;
    int channel_data_index;
    int sample_rate_div;
    int get_digi();
public:
    TmsiAmplifier(const char *address, const char *read_address=NULL,int type = USB_AMPLIFIER);
    TmsiAmplifier(const TmsiAmplifier& orig);
    int number_of_channels()
    {
        return fei.nrofswchannels;
    }
    int set_sampling_rate(int sample_rate) {
        int tmp = 0, bsr = fei.basesamplerate;
        while (tmp < 4 && abs(sample_rate - bsr >> tmp) > abs(sample_rate - bsr >> (tmp + 1))) tmp++;
        sample_rate_div = tmp;
        sampling_rate = bsr>>tmp;
        return sampling_rate;
    }
    void set_sampling_rate_div(int sampling_rate_div) {
        sampling_rate_div = sampling_rate_div;
    }

    int get_sampling_rate_div() {
        return sample_rate_div;
    }
    void start_sampling();
    void stop_sampling();
    int fill_samples(vector<int> &samples);
    int fill_samples(vector<float> &samples);
    void set_active_channels(vector<int> &channels);
    bool is_battery_low()
    {
        return get_digi()&BATTERY_LOW;
    }
    bool is_trigger()
    {
        return get_digi()&TRIGGER_ACTIVE;
    }
    bool is_onoff_pressed()
    {
        return get_digi()&ON_OFF_BUTTON;
    }
    int refreshInfo();

    ~TmsiAmplifier();
private:
    void init();
    int connect_usb(const char * address);
    int connect_bluetooth(const char *address);
    int send_request(int type);
    bool update_info(int type);
    void _refreshInfo(int type);
    void load_channel_desc();
    tms_channel_data_t* alloc_channel_data();
    void free_channel_data(tms_channel_data_t * &channel_data)
    {
        if (channel_data!=NULL)
        {
            for (int i=0;i<dev.NrOfChannels;i++)
                free(channel_data[i].data);
            free(channel_data);
            channel_data=NULL;
        }
    }

    void refreshFrontEndInfo() {
        _refreshInfo(TMSFRONTENDINFO);
    }

    void refreshIDData() {
        _refreshInfo(TMSIDDATA);
        load_channel_desc();
    }

    void refreshVLDeltaInfo() {
        free_channel_data(channel_data);
        _refreshInfo(TMSVLDELTAINFO);
        channel_data=alloc_channel_data();
    }
    bool get_samples();
    void print_message(FILE *);
    void receive();
    const char * get_type_name(int type);
};

#endif	/* TMSIAMPLIFIER_H */

