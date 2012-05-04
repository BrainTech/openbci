include Makefile.common

ALL = dummy_amplifier test_server test_logger test_dummy_amplifier

#This is for command line completion
$(ALL):


$(BIN)/dummy_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) dummy_amplifier_main.o)
	$(LD_SERVER)

$(BIN)/test_server: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) test_server.o)
	$(LD_SERVER)

$(BIN)/test_logger:  $(CHECK_BIN) $(addprefix $(BUILD)/,test_logger.o Logger.o) 
	$(LD_AMPLIFIER)

$(BIN)/test_dummy_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER) test_amplifier.o test_dummy_amplifier.o)
	$(LD_AMPLIFIER)
