include ../base/Makefile.common
INCLUDEDIRS += -I$(BUILD)

signal_receiver: $(BUILD)/SignalReceiver.o

dummy_receiver: $(BUILD)/DummyReceiver.o

signal_receiver dummy_receiver: $(addprefix $(BUILD)/, Logger.o variables.pb.o)
	$(CXX) -o $@ $^	$(LD_SERVER)