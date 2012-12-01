If you want to test virtual amplifier in c++ you must have property compiled c_tmsi_amplifier in ../../openbci/amplifiers/c_tmsi_amplifier!!!

Files:
- ./run_mx - fires multiplexer


- ./run_amplifier - fires virtual amplifier, 
- - called with parameters: ./run_amplifier NUMBER_OF_CHANNELS SAMPLING DURATION VALUE_TYPE where:
- - NUMBER_OF_CHANNELS - number of channels to be amplified (eg. 20)
- - SAMPLING - sampling rate (eg. 256)
- - DURATION - time (in seconds) after which the driver will stop amplifying
- - VALUE_TYPE - by now it is 1 or 0; 0 means that channel values will be random values, 1 means that channel values will be sample numbers
- - eg run: ./run_amplifier 25 1024 100 1


- ./run_mx_amplifier - fires multiplexer and amplifier, parameters are as in ./run_amplifier
- - eg run: ./run_mx_amplifier 25 1024 100 1


- ./run_receiver - fires signal receiver
- - called with parameters: ./run_receiver DURATION CACHE_SIZE DUMP_FILE where:
- - DURATION - time (in seconds) after which receiver will stop receiving
- - CACHE_SIZE - size (in samples) of the buffer in which samples will be buffered
- - DUMP_FILE - file path to which data will be written every time the buffer is filled (not working by now see  signal_receiver._dump_cache() )
- - eg run: ./run_receiver 10 1024 ./nic.txt


- ./stop - kills MX and other modules


- multiplexer.rules - rules with which MX will be fired


- signal_receiver.py - python MX peer - signal receiver


- virtual_amplifier.py - python MX peer - amplifier
