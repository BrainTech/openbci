#!/usr/bin/env python
import sys
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import variables_pb2

def configure_amplifier(number_of_channels, sampling, values_type):
    print("Start configuring amplifier...")
    c = connect_client(type = peers.AMPLIFIER)
    set_hashtable_value(c, "SamplingRate", str(sampling))
    set_hashtable_value(c, "NumOfChannels", str(number_of_channels))
    set_hashtable_value(c, "Gain", ' '.join(['1.0']*number_of_channels))
    set_hashtable_value(c, "Offset", ' '.join(['0.0']*number_of_channels))
    if values_type == 1: #set last channel to sample number ...
        set_hashtable_value(c, "ChannelsNames", ';'.join([str(i) for i in range(number_of_channels-1)]+['SAMPLE_NUMBER']))
        set_hashtable_value(c, "AmplifierChannelsToRecord", ' '.join([str(i) for i in range(number_of_channels-1)]+['sample']))
    else:
        set_hashtable_value(c, "ChannelsNames", ';'.join([str(i) for i in range(number_of_channels)]))
        set_hashtable_value(c, "AmplifierChannelsToRecord", ' '.join([str(i) for i in range(number_of_channels)]))

    print("Amplifier configured!")

def set_hashtable_value(connection, key, value):
        l_var = variables_pb2.Variable()
        l_var.key = key
        l_var.value = value
        connection.send_message(message = l_var.SerializeToString(), 
                                type = types.DICT_SET_MESSAGE, flush=True)


if __name__ == "__main__":
    number_of_channels = 25
    sampling = 64
    #duration = 5
    values_type = 0
    if len(sys.argv) >= 2:
        number_of_channels = int(sys.argv[1])
    if len(sys.argv) >= 3:
        sampling = int(sys.argv[2])
    if len(sys.argv) >= 4:
        values_type = int(sys.argv[3])
    #if len(sys.argv) >= 5:
    #    values_type = int(sys.argv[4])

    configure_amplifier(number_of_channels, sampling, values_type)

 
