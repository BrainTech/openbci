#!/usr/bin/env python
#
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

from openbci.core import core_logging as logger
LOGGER = logger.get_logger("hashtable")#, "error")

def channels_gen(num):
    return ' '.join([str(i) for i in range(num)])

def gains_gen(num):
    return ' '.join(['1']*num)

def offsets_gen(num):
    return ' '.join(['0.0715']*num)    

def names_gen(num):
    return ' '.join(['nazwa']*num)

CHANNELS = 26

class Hashtable(BaseMultiplexerServer):

    #

    data = {
        "MinData": "-1000",
        "MaxData": "1000",
        "DataScale": "1.0",
        "TMSiDeviceName": "/dev/rfcomm0",
        "AmplifierChannelsToRecord": channels_gen(CHANNELS),
        #"ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;C7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2;NIC;OKO",
        "ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;C7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2;NIC;EOG_UP_DOWN;EOG_LEFT_RIGHT", #26
        #"ChannelsNames": "Fp1;Fpz;Fp2;F7;F3;Fz;F4;F8;M1;T7;C3;Cz;C4;T8;M2;P7;P3;Pz;P4;P8;O1;Oz;O2;NIC;EOG", #23
        #"ChannelsNames": "a;b;c;",

        #"ChannelsNames":"REKA",
        #"ChannelsNames":"A;B",
        "Gain":gains_gen(CHANNELS),
        "Offset": offsets_gen(CHANNELS),
        "NumOfChannels": CHANNELS,
        "BraintronicsDeviceName": "/dev/ttyUSB0",
        "SamplingRate": "128",
        "VirtualAmplifierFunction": "math.sin(2 * math.pi * offset / 128. * 12)", #"100. * math.sin((channel_number + 1) * offset / 100.)",
        "SignalCatcherBufferSize": "1024",
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
        "Freqs": "0 0 0 0 0 0 0 0",

#        "Borders": "0.8 0.8 0.8 0.8 0.8 0.8 0.8 0.8",
        "Borders": "0.6 0.4 1.2 .4 .6 .8 1 .2",
        #"Borders": ".7 .2 .7 .7 .7 .2 .6 .6",

        "Reps": "1 1 1 1 1 1 1 1" ,
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
        "BlinkPeriod": "0.25",
        "HeightBar": "0.6",
        "DiodSequence": "1,2",
        "TrainingSequence": "0 1",
        "Session": "NormalSession",
    	"BlinkingMode": "SSVEP",
        "AmpBattery": "0",
        "Trigger": "0",
	"FloorTimeBoundry" : "0.25",
	"CeilingTimeBoundry" : "0.4",
        "SaveFileName" : "test_save",
        "SaveFilePath" : "./temp",
        #"SaveFilePath" : "/home/mati/bci_dev/google_openbci/openbci/openbci/experiment_builder/alpha_ass/data_20_07_2010/",
        "FilterLevel": "3",
        "FilterBand": "bandpass",
        "FilterUp": "32",
        "FilterDown": "2",
        "AppendTriggerInDriver":"0",
        "AmplifierNull":"8388608.0",
        "P300Rows":"5",
        "P300Cols":"5",
        "P300BlinkMode":"square",
        "P300BlinkColor":"#ffffff",
        "P300BlinkPeriod":"0.1",
        "P300BlinkBreak":"0.4",
        "P300SquareSize":"50.0",
        "P300FontSize":"30",
        "P300Letters": "A B C D E F G H I J K L M N O P R S T U W Y Z _ <",

    }  # temporarily we enter here default values. In future it will be set using SVAROG probably


    def __init__(self, addresses):
        super(Hashtable, self).__init__(addresses=addresses, type=peers.HASHTABLE)
        self.update_driver_trigger()

    def update_driver_trigger(self):
        """Check AppendTriggerInDriver value.
        If it is set to true ("1") then update other self.data values
        depending on the information that driver will append auxilary channel."""
        if int(self.data.get("AppendTriggerInDriver","0")):
            # If that value is set to "1" We append required data to channelNames Gains etc
            # so that stream readers will not be confused by one-more channel
            self.data["ChannelsNames"] = ''.join([self.data["ChannelsNames"],";TRIGGER"])
            self.data["Gain"] = ''.join([self.data["Gain"], " 100.0"])
            self.data["Offset"] = ''.join([self.data["Offset"], " 0.0"])
            self.data["NumOfChannels"] = self.data["NumOfChannels"]+1
        
    def handle_message(self, mxmsg):
        if mxmsg.type == types.DICT_SET_MESSAGE:
            pair = variables_pb2.Variable()
            pair.ParseFromString(mxmsg.message)
            key = pair.key
            value = pair.value
            self.data[key] = value
            self.no_response()
            LOGGER.info("Got DICT_SET_MESSAGE with: key="+key+", value="+value)
        elif mxmsg.type == types.DICT_GET_REQUEST_MESSAGE:
            #pair = variables_pb2.Variable()
            key = mxmsg.message
            value = self.data[key] if key in self.data else ""
            LOGGER.info("Got DICT_GET_RESPONSE_MESSAGE with key="+key+
                        ". Send response value="+str(value))

            #self.send_message(message=str(value), type=types.DICT_GET_RESPONSE_MESSAGE)

            self.send_message(message=str(value), type=types.DICT_GET_RESPONSE_MESSAGE, to=int(mxmsg.from_), flush=True)


if __name__ == "__main__":
    Hashtable(settings.MULTIPLEXER_ADDRESSES).loop()
