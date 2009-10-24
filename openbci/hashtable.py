#!/usr/bin/env python

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2



class Hashtable(BaseMultiplexerServer):

    #

    data = {
        "TMSiDeviceName": "/dev/rfcomm0",
        "AmplifierChannelsToRecord": "0 1 2 3 4 5 6 7 8 9",
	# "12 6 11 13 17 18 19 21 22 23",
        "BraintronicsDeviceName": "/dev/ttyUSB0",
        "SamplingRate": "128",
        "VirtualAmplifierFunction": "math.sin(2 * math.pi * offset / 128. * 11)", #"100. * math.sin((channel_number + 1) * offset / 100.)",
        "SignalCatcherBufferSize": "1024",
        "NumOfFreq": "8",
        "Border": "1.0",
        "Panel":  " media/lamp_on.png | :: media/fan_on.png |  :: media/turn_on.png | :: media/speller.png | :: media/lamp_off.png | :: media/fan_off.png  | :: media/turn_off.png | :: media/p300.png | ",

        #"gold-letter-A.png | :: gold-letter-B.png |  :: gold-letter-C.png | :: gold-letter-D.png | :: gold-letter-E.png | :: | :: speaker.png | :: arrow-left.png| ",
 
        #" media/lamp_on.png | :: media/fan_on.png |  :: media/turn_on.png | :: media/speller.png | :: media/lamp_off.png | :: media/fan_off.png  | :: media/turn_off.png | :: media/p300.png | ",
	# "| Light on :: | Fan on :: | on :: |  Speller :: | Light off :: | Fan off  :: | off :: | P300  ",
        #" | < :: | say :: | A :: | B :: | C :: | D :: | E :: | back ",
        #        "Panel":  "| ligth on :: | sound on :: | speller :: |  :: | light off :: | sound off :: |  :: | ",
        "Message": "lamp: ON   |   fan: OFF  |  music: PLAY ",
        "Freqs": "9 10 12 11 13 17 15 8",
        "Repeats": "3",
        "FrameWidth": "35",
        "Squares": "8",
        "ScreenH": "700",
        "ScreenW": "1024",
        #"1280",
        "StatusBar": "100",
        "Rows": "2",
        "Cols": "4",
        "RobotIP": "192.168.0.168",
        "Blinks": "1",
        "BlinkPeriod": "0.25",
        "HeightBar": "0.6",
        "DiodSequence": "1,2",
        "TrainingSequence": "0",
        "Session": "TreningSession",
    	"BlinkingMode": "SSVEP"
        

    }  # temporarily we enter here default values. In future it will be set using SVAROG probably


    def __init__(self, addresses):
        super(Hashtable, self).__init__(addresses=addresses, type=peers.HASHTABLE)


    def handle_message(self, mxmsg):
        if mxmsg.type == types.DICT_SET_MESSAGE:
            pair = variables_pb2.Variable()
            pair.ParseFromString(mxmsg.message)
            key = pair.key
            value = pair.value
            #key, value = cPickle.loads(mxmsg.message)
            self.data[key] = value
            #print "SET: ", key, str(value)
            self.no_response()
        elif mxmsg.type == types.DICT_GET_REQUEST_MESSAGE:
            #pair = variables_pb2.Variable()
            key = mxmsg.message
            value = self.data[key] if key in self.data else ""
            # print key, str(value)

            self.send_message(message=str(value), type=types.DICT_GET_RESPONSE_MESSAGE)


if __name__ == "__main__":
    Hashtable(settings.MULTIPLEXER_ADDRESSES).loop()
