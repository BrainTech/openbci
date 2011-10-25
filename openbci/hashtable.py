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

CHANNELS = 5

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
        "ChannelsNames": "A;B;C;D;E",
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
        "SaveFileName" : 'etr_test2', #"p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_ublinkShot150_lukasz",
        "SaveFilePath" : "./temp/", #"/media/windows/titanis/bci/projekty/eksperyment_mikolaj/dane_07_12_2010/",
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


        # ------------ ANALYSIS --------------------------------------------------------------------------------
        # ------------ START -----------------------------------------------------------------------------------

        # Define from which moment in time (ago) we want to get samples (in seconds)
        'ANALYSIS_BUFFER_FROM':'1.0', 
        # Define how many samples we wish to analyse every tick (in seconds)
        'ANALYSIS_BUFFER_COUNT':'1.0',
        # Define a tick duration (in seconds).
        'ANALYSIS_BUFFER_EVERY':'1.0',
        # To SUMP UP - above default values (0.5, 0.4, 0.25) define that
        # every 0.25s we will get buffer of length 0.4s starting from a sample 
        # that we got 0.5s ago.
        # Some more typical example would be for values (0.5, 0.5 0.25). 
        # In that case, every 0.25 we would get buffer of samples from 0.5s ago till now.

        # possible values are: 'PROTOBUF_SAMPLES', 'NUMPY_CHANNELS'
        # it indicates format of buffered data returned to analysis
        # NUMPY_CHANNELS is a numpy 2D array with data divided by channels
        # PROTOBUF_SAMPLES is a list of protobuf Sample() objects
        'ANALYSIS_BUFFER_RET_FORMAT':'NUMPY_CHANNELS', 

        #we will not modify data, so no need to copy it
        'ANALYSIS_BUFFER_COPY_ON_RET':"0", 


        # ------------ END -------------------------------------------------------------------------------------
        # ------------ ANALYSIS --------------------------------------------------------------------------------


        # ------------ UGM ------------------------------------------------------------------------------
        # ------------ START -----------------------------------------------------------------------------------
        
        #'UGM_CONFIG': 'speller_config_nesw',
        #'UGM_CONFIG': 'speller_config_6',
        'UGM_CONFIG': 'p300_ssvep',
        #'UGM_CONFIG': 'speller_config_8',
        'UGM_USE_TAGGER':'1',
        'UGM_INTERNAL_IP':'127.0.0.1',
        'UGM_INTERNAL_PORT':'5028',
        # ------------ END -------------------------------------------------------------------------------------
        # ------------ UGM ------------------------------------------------------------------------------


        # ------------ SPELLER --------------------------------------------------------------------------------
        # ------------ START -----------------------------------------------------------------------------------
        #'SPELLER_CONFIG':'speller_config_nesw',
        #~ 'SPELLER_CONFIG':'speller_config_6',
        'SPELLER_CONFIG':'speller_config_8',
        #'SPELLER_AREA_COUNT':'6',
        'SPELLER_AREA_COUNT':'8',

        'SPELLER_START_TEXT_ID':'1001',
        'SPELLER_TEXT_ID':'54321',
        # ------------ END -------------------------------------------------------------------------------------
        # ------------ SPELLER --------------------------------------------------------------------------------


        # ------------ EYETRACKER ------------------------------------------------------------------------------
        # ------------ START -----------------------------------------------------------------------------------
        'ETR_TYPE':'NESW',
        #'ETR_TYPE':'CLASSIC',
        #'ETR_DEC_TYPE':'FRACTION',
        #'ETR_PUSH_DEC_COUNT':'0.7', 
        #'ETR_PUSH_FEED_COUNT':'0.1',
        'ETR_DEC_TYPE':'COUNT',
        'ETR_PUSH_DEC_COUNT':'10', 
        'ETR_PUSH_FEED_COUNT':'3',
        'ETR_BUFFER_SIZE':'5.0',
        'ETR_IGNORE_MISSED':'1',
        'ETR_DEC_BREAK':'0.3',
        
        'ETR_NESW_RATIO':'0.6',
        'ETR_NESW_STACK':'200',
        'ETR_NESW_DEC_COUNT':'5',
        'ETR_NESW_DELAY':'20',
        'ETR_NESW_FEED_FADE':'15',
        
        'ETR_START_AREA_ID': '101',
        'ETR_FIX_ID': '12345',

        'ETR_AMPLIFIER_IP':'127.0.0.1',
        'ETR_AMPLIFIER_PORT':'20320',
        'ETR_DASHER_PORT':'20321',
        # ------------ END -------------------------------------------------------------------------------------
        # ------------ EYETRACKER ------------------------------------------------------------------------------


        # ------------ BLINKING UGM ------------------------------------------------------------------------------
        # ------------ BEGIN -------------------------------------------------------------------------------------
        # An algorithm generating ids. Possible values:
        # RANDOM - random values from range [0;BLINK_ID_COUNT]
        # SEQUENTIAL - sequental values from range [0;BLINK_ID_COUNT]
        # RANDOM_SEQUENTIAL - random, but not repeated values from range [0;BLINK_ID_COUNT]. Eg. for [0,1,2,3] we`ll get
        # sth like 0 2 3 1  2 3 0 1  3 1 0 2  0 2 1 3 .... 
        'BLINK_ID_TYPE': 'RANDOM',
        #'BLINK_ID_TYPE': 'RANDOM_SEQUENTIAL',
        #'BLINK_ID_TYPE': 'SEQUENTIAL',

        # blink ids will be genereated from range [0;BLINK_ID_COUNT]
        'BLINK_ID_COUNT':'1',

        # Time (in secs) between two blinks will be generated as float from range[BLINK_MIN_BREAK;BLINK_MAX_BREAK]
        'BLINK_MIN_BREAK':'1.5',
        'BLINK_MAX_BREAK':'2.5',
        
        # Duration of a single blink (in secs)
        'BLINK_DURATION':'0.1',

        # An algorithm generating counts. Possible values:
        # INF - always returns -1 (should indicate infinity - blink forever)
        # RANDOM - random values from range [0;BLINK_ID_COUNT]
        # SEQUENTIAL - sequental values from range [0;BLINK_ID_COUNT]
        # RANDOM_SEQUENTIAL - random, but not repeated values from range [0;BLINK_ID_COUNT]. Eg. for [0,1,2,3] we`ll get
        # sth like 0 2 3 1  2 3 0 1  3 1 0 2  0 2 1 3 .... 
        #'BLINK_COUNT_TYPE': 'INF',
        'BLINK_COUNT_TYPE': 'RANDOM',
        #'BLINK_COUNT_TYPE': 'RANDOM_SEQUENTIAL',
        #'BLINK_COUNT_TYPE': 'SEQUENTIAL',

        # blink counts will be genereated from range [BLINK_COUNT_MIN;BLINK_COUNT_MAX]
        'BLINK_COUNT_MIN':'4',
        'BLINK_COUNT_MAX':'6', 


        # Blinker type, possible values:
        # SINGLE - every time one choosen field performs blink
        # CLASSIC - matrix-like blinker - blinks the whole row or whole column
        'BLINK_UGM_TYPE':'SINGLE',
        #'BLINK_UGM_TYPE':'CLASSIC',
        'BLINK_UGM_ROW_COUNT':'1', # A number of rows in CLASSIC blinker
        'BLINK_UGM_COL_COUNT':'1', # A number of cols in CLASSIC blinker
        #'BLINK_UGM_TYPE':'CLASSIC',
        # We should have always: BLINK_ID_COUNT == BLINK_UGM_ROW_COUNT + BLINK_UGM_COL_COUNT
        # We should have always: BLINK_UGM_ID_COUNT == BLINK_UGM_ROW_COUNT * BLINK_UGM_COL_COUNT
        # IN SINGLE blinker we whould have always: BLINK_UGM_ID_COUNT == BLINK_ID_COUNT



        # Start id and count of ugm components that are considered 'blinking' elements
        # It is assumed that to-be-blinked components are enumerated sequentially, eg. from 101 to 106 -
        # - then BLINK_UGM_ID_START would be 101, BLINK_UGM_COL_COUNT would be 5
        'BLINK_UGM_ID_START':'101',
        'BLINK_UGM_ID_COUNT':'1',

        # What property (KEY) and how (VALUE) should be changed on blink.
        # Eg. BLINK_UGM_KEY migh be 'color' and BLINK_UGM_VALUE migt be '#ff0000'
        'BLINK_UGM_KEY':'font_size',
        'BLINK_UGM_VALUE':'50',
        # ------------ END -------------------------------------------------------------------------------------
        # ------------ BLINKING UGM ------------------------------------------------------------------------------




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
