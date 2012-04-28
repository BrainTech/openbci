include ../base/Makefile.common

CXXFLAGS += -DBLUETOOTH

TMSI = TmsiAmplifier.o TmsiChannels.o TmsiAmplifierDesc.o nexus.o

test_tmsi_amplifier: $(addprefix $(BUILD)/, $(AMPLIFIER) $(TMSI) test_amplifier.o test_tmsi_amplifier.o)
	$(CXX) -o $@ $^	$(LD_AMPLIFIER) -lbluetooth

tmsi_amplifier: $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) $(TMSI) tmsi_amplifier_main.o)
	$(CXX) -o $@ $^	$(LD_SERVER) -lbluetooth

install_tmsi: force_look
	cd driver;make install
	