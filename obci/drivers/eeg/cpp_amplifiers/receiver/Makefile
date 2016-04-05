include ../base/Makefile.common
INCLUDEDIRS += -I$(BUILD)

$(BIN)/signal_receiver: $(BUILD)/SignalReceiver.o

$(BIN)/dummy_receiver: $(BUILD)/DummyReceiver.o

$(BIN)/signal_receiver $(BIN)/dummy_receiver: $(addprefix $(BUILD)/, Logger.o variables.pb.o)
	$(LD_SERVER)