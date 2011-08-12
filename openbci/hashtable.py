#!/usr/bin/env python
#
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

from openbci.core import core_logging as logger
LOGGER = logger.get_logger("hashtable")


def channels_gen(num):
    return ' '.join([str(i) for i in range(num)])

def gains_gen(num):
    return ' '.join(['0.0715']*num)

def offsets_gen(num):
    return ' '.join(['0']*num)    

def names_gen(num):
    return ' '.join(['nazwa']*num)

CHANNELS = 1

class Hashtable(BaseMultiplexerServer):

    #

    data = {
        "MinData": "-1000",
        "MaxData": "1000",
        "DataScale": "1.0",
        "TMSiDeviceName": "/dev/rfcomm0",
        "AmplifierChannelsToRecord": channels_gen(CHANNELS), #You dont need to add here special channels names (trigg, bat etc.), use
                                                             #DriverTriggerIndex, DriverOnoffIndex, DriverBatteryIndex values instead,
                                                             #to define special channels indices.
                                                             #Hashtable.update_driver_special_channels() will do the rest.

        #"ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;C7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2;NIC;OKO",
        #"ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;C7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2;NIC;EOG_UP_DOWN;EOG_LEFT_RIGHT", #26
        #"ChannelsNames":"gen1;gen2;gen3",
        #"ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;T7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2", #23
        #"ChannelsNames":"gen1",
        #"ChannelsNames": "SAMPLE_NUMBER",
        #"ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;T7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2;NIC;EOG", #25
        "ChannelsNames": "gsr",
        #"ChannelsNames": "O1;Oz;O2",

        #"ChannelsNames":"REKA",
        #"ChannelsNames":"A;B",
        "Gain":gains_gen(CHANNELS),
        "Offset": offsets_gen(CHANNELS),
        "NumOfChannels": CHANNELS,
        "SamplesPerVector":"4",
        "BraintronicsDeviceName": "/dev/ttyUSB0",
        "SamplingRate": "256",
        "VirtualAmplifierFunction": "100*math.sin(2 * math.pi * offset / 256. * 3)", #"offset", #"100. * math.sin((channel_number + 1) * offset / 100.)",
        "SignalCatcherBufferSize": "4096",
        "NumOfFreq": "8",
        "Border": "0.4",
        "Panel":  " | K :: | L :: | M ::  | del ::  | N ::  | O ::  | say ::  | <- " ,

	# " gr1.jpg | :: gr2.jpg |  :: gr3.jpg | :: gr4.jpg |  :: gr5.jpg | :: gr6.jpg |  :: gr7.jpg| :: gr8.jpg | " ,
 
	#" | K :: | L :: | M :: gr4.jpg |  :: | N ::  | O :: speaker.png | :: gr8.jpg | " ,

	#" gr1.jpg | :: gr2.jpg |  :: gr3.jpg | :: gr4.jpg |  :: gr5.jpg | :: gr6.jpg |  :: gr7.jpg| :: gr8.jpg | " ,

	# " | < :: | A B C D E :: | F G H I J:: | K L M N O :: | P R S T U:: | V W X Y Z :: | main:: | ' ' ." ,
	# "| Light on :: | Fan on :: | on  :: | Speller :: | Light off :: | Fan off  :: | off :: | P300 ",
        #" | < :: | say :: | A :: | B :: | C :: | D :: | E :: | back ",
        #        "Panel":  "| ligth on :: | sound on :: | speller :: |  :: | light off :: | sound off :: |  :: | ",
        "Message": "",
#       "Freqs": "12 13 23 9 16 17 15 19",
        "Freqs": "13 15 7 12 8 9 10 11",

#        "Borders": "0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8",
        "Borders": "1.5 1.5 1.5 1.5 1.5 1.5 1.5 1.5",
        #"Borders": ".7 .2 .7 .7 .7 .2 .6 .6",

        "Reps": "2 2 2 2 2 2 2 2" ,
        "Repeats": "1",
        "FrameWidth": "20",
        "Squares": "8",
        "ScreenH": "650",
        "ScreenW": "1024",
        "StatusBar": "100",
        "Rows": "2",
        "Cols": "4",
        "RobotIP": "192.168.0.168",
        "Blinks": "5",
        "BlinkPeriod": "0.75",
        "HeightBar": "0.6",
        "DiodSequence": "1,2,3,4,5,6,7,8",
        "TrainingSequence": "0 1 2 3 4 5 6 7",
        "Session": "NormalSession",
    	"BlinkingMode": "P300",
        "AmpBattery": "0",
        "Trigger": "0",
	"FloorTimeBoundry" : "0.25",
	"CeilingTimeBoundry" : "0.4",
        "SaveFileName" : "p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_ublinkShot150_lukasz",
        "SaveFilePath" : "./temp/p300/", #"/media/windows/titanis/bci/projekty/eksperyment_mikolaj/dane_07_12_2010/",
        #"SaveFilePath" : "/home/mati/bci_dev/google_openbci/openbci/openbci/experiment_builder/alpha_ass/data_20_07_2010/",
        "FilterLevel": "3",
        "FilterBand": "bandpass",
        "FilterUp": "32",
        "FilterDown": "2",
        "DriverTriggerIndex":"-1", #str(CHANNELS), #,Append trigger at the end
        "DriverOnoffIndex": "-1", #str(CHANNELS),
        "DriverBatteryIndex": "-1",
        "DriverSampleNoIndex": "-1", #str(CHANNELS),
        "SaverTimestampsIndex": "-1", #str(CHANNELS+1),
        "AmplifierNull":"8388608.0",
        "P300Rows":"6",
        "P300Cols":"6",
        "P300BlinkMode":"square",
        "P300BlinkColor":"#ffffff",
        "P300BlinkPeriod":"0.1",
        "P300BlinkBreak":"0.075",
        "P300SquareSize":"50.0",
        "P300FontSize":"30",
        "P300Letters": "A B C D E F G H I J K L M N O P R S T U W Y Z 0 1 2 3 4 5 6 7 8 9 _ > #",
        "P300TrainingBlinksPerChar": "96",
        "P300TrainingCharBreak": "5.0",
        "P300TrainingChars": "C A T D O G F I S H W A T E R B O W L",
        "BlinkCatcherBufSize":"12",

        'ETR_DEC_TYPE':'COUNT',
        'ETR_PUSH_DEC_COUNT':'10', 
        'ETR_PUSH_FEED_COUNT':'2',
        'ETR_BUFFER_SIZE':'3.0',
        'ETR_IGNORE_MISSED':'1',
        'ETR_AREA_COUNT': '6',

        'UGM_CONFIG': 'feedback_speller_config5',
        'ETR_START_AREA_ID': '101',
        'ETR_FIX_ID': '12345'

        

    }  # temporarily we enter here default values. In future it will be set using SVAROG probably


    def __init__(self, addresses):
        super(Hashtable, self).__init__(addresses=addresses, type=peers.HASHTABLE)
        self.update_driver_special_channels()

    def update_driver_special_channels(self):
        """Check Driver...Index values. If any is > -1, then add special channel 
        to specified index and update all related values: 
        gain, offset, number of channels, channel names, amplifier channels to record"""
        d = []
        d.append(('trig', int(self.data.get("DriverTriggerIndex", "-1")), "TRIGGER"))
        d.append(('bat', int(self.data.get("DriverBatteryIndex", "-1")), "BATTERY"))
        d.append(('onoff', int(self.data.get("DriverOnoffIndex", "-1")), "ONOFF"))
        d.append(('sample', int(self.data.get("DriverSampleNoIndex", "-1")), "SAMPLE_NUMBER"))
        for ch_sym, ch_ind, ch_name in d:
            if ch_ind > -1:
                self.data["NumOfChannels"] = self.data["NumOfChannels"]+1

                # Add name to special channel
                ch_r =  self.data["AmplifierChannelsToRecord"].split(" ")
                ch_r.insert(ch_ind, ch_sym)
                self.data["AmplifierChannelsToRecord"] = ' '.join(ch_r)

                # Add name to special channel
                ch_names =  self.data["ChannelsNames"].split(";")
                ch_names.insert(ch_ind, ch_name)
                self.data["ChannelsNames"] = ';'.join(ch_names)

                # Add gain to special channel
                gains = self.data["Gain"].split(" ")
                gains.insert(ch_ind, "100.0")
                self.data["Gain"] = ' '.join(gains)

                # Add offset to special channel
                offsets = self.data["Offset"].split(" ")
                offsets.insert(ch_ind, "0.0")
                self.data["Offset"] = ' '.join(offsets)
        
    def _set_peer_ready(self, peer_type, peer_id):
        r = self.data.get('PEER_READY', {})
        for_key = r.get(peer_type, [])
        for_key.append(peer_id)
        r[peer_type] = for_key
        self.data['PEER_READY'] = r
        
    def _get_peer_ready(self, peer_type):
        if len(peer_type) == 0:
            return self.data.get('PEER_READY', "")
        else:
            value = self.data.get('PEER_READY', {}).get(peer_type, [])
            print("VALUE: ")
            print(value)
            value = ' '.join([str(i) for i in value])
            return value


    def handle_message(self, mxmsg):
        if mxmsg.type == types.DICT_SET_MESSAGE:
            pair = variables_pb2.Variable()
            pair.ParseFromString(mxmsg.message)
            key = pair.key
            value = pair.value
            if key == 'PEER_READY':
                self._set_peer_ready(value, mxmsg.from_)
            else:
                self.data[key] = value
            self.no_response()
            LOGGER.info("Got DICT_SET_MESSAGE with: key="+key+", value="+value)
            #self.conn.send_message(message=pair.SerializeToString(), type=types.SYSTEM_CONFIGURATION)

        elif mxmsg.type == types.DICT_GET_REQUEST_MESSAGE:
            key = mxmsg.message
            if key.startswith('PEER_READY'):
                value = self._get_peer_ready(key[len('PEER_READY'):])
            else:
                value = self.data.get(key, "")
                
            LOGGER.info("Got DICT_GET_RESPONSE_MESSAGE with key="+key+
                        ". Send response value="+str(value))

            #self.send_message(message=str(value), type=types.DICT_GET_RESPONSE_MESSAGE)

            self.send_message(message=str(value), type=types.DICT_GET_RESPONSE_MESSAGE, to=int(mxmsg.from_), flush=True)


if __name__ == "__main__":
    Hashtable(settings.MULTIPLEXER_ADDRESSES).loop()
