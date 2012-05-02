include Makefile.common

 

dummy_amplifier: $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) dummy_amplifier_main.o)
	$(CXX) -o $@ $^ $(LD_SERVER)

test_server: $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) test_server.o)
	$(CXX) -o $@ $^ $(LD_SERVER)

test_logger:  $(addprefix $(BUILD)/,test_logger.o Logger.o) 
	$(CXX) -o $@ $^

test_dummy_amplifier: $(addprefix $(BUILD)/, $(AMPLIFIER) test_amplifier.o test_dummy_amplifier.o)
	$(CXX) -o $@ $^	$(LD_AMPLIFIER)

force_look:
	@true