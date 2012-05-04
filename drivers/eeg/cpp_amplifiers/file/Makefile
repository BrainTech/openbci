include ../base/Makefile.common

ALL = file_amplifier test_file_amplifier 


$(ALL): #This is for command line completion

$(BIN)/test_file_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER) FileAmplifier.o test_file_amplifier.o test_amplifier.o)
	$(LD_AMPLIFIER)
 
$(BIN)/file_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) FileAmplifier.o TagAmplifierServer.o file_amplifier_main.o)
	$(LD_SERVER)

