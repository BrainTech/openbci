If you want to test virtual amplifier in c++ you must have property compiled c_tmsi_amplifier in ../../openbci/amplifiers/c_tmsi_amplifier!!!

Files:
- ./run_mx - fires multiplexer


- ./run_amplifier - fires virtual amplifier, 
- - MUST be called with parameters: ./run_amplifier NUMBER_OF_CHANNELS SAMPLING DURATION VALUE_TYPE where:
- - NUMBER_OF_CHANNELS - number of channels to be amplified (eg. 20)
- - SAMPLING - sampling rate (eg. 256)
- - DURATION - time (in seconds) after which the driver will stop amplifying (this parameter is NOT working by now...)
- - VALUE_TYPE - by now it is 1 or 0; 0 means that channel values will be random values, 1 means that channel values willbe random values, except for the last channel which will be sample number
- - eg run: ./run_amplifier 25 1024 1234 1


- ./run_mx_amplifier - fires multiplexer and amplifier, parameters are as in ./run_amplifier
- - eg run: ./run_mx_amplifier 25 1024 1234 1


- ./stop - kills MX and other modules


- multiplexer.rules - rules with which MX will be fired


- configure_amplifier.py - set all needed hashtable values for amplifier; used internally by ./run_amplifier
