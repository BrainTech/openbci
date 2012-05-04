include ../base/Makefile.common

CXXFLAGS += -DBLUETOOTH

TMSI = TmsiAmplifier.o TmsiChannels.o TmsiAmplifierDesc.o nexus.o

ALL = tmsi_amplifier test_tmsi_amplifier


$(ALL): #This is for command line completion

$(BIN)/test_tmsi_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER) $(TMSI) test_amplifier.o test_tmsi_amplifier.o)
	$(LD_AMPLIFIER) -lbluetooth

$(BIN)/tmsi_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) $(TMSI) tmsi_amplifier_main.o)
	$(LD_SERVER) -lbluetooth

install_tmsi:
	cd driver;make install