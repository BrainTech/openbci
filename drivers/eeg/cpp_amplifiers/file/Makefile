include ../base/Makefile.common

 

test_file_amplifier: $(addprefix $(BUILD)/, $(AMPLIFIER) FileAmplifier.o test_file_amplifier.o test_amplifier.o)
	$(CXX) -o $@ $^	$(LD_AMPLIFIER)
 
file_amplifier: $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) FileAmplifier.o TagAmplifierServer.o file_amplifier_main.o)
	$(CXX) -o $@ $^	$(LD_SERVER)
