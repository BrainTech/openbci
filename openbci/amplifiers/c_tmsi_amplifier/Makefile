PYTHON_VERSION	:= $(shell python --version 2>&1 | sed 's/^[^0-9]*\([0-9]\+\)\.\([0-9]\+\).*/\1.\2/')
ROOTDIR		= ../../..
AZOUKDIR	= $(ROOTDIR)/multiplexer-install
CXX		= g++
O		?= #-O3
GENERALFLAGS	+= $(O) -Wall \
			-DBOOST_DISABLE_THREADS \
			#-DAMP_DEBUG
			 \
			#
ifdef DEBUG
GENERALFLAGS	+= -DAMP_DEBUG
endif
CXXFLAGS	+= $(GENERALFLAGS)
INCLUDEDIRS =			-I . -I/usr/share/multiplexer/src \
			-I$(AZOUKDIR)/include \
			-I$(ROOTDIR)/openbci \
			-fPIC \
			-Ibuild
			#

LDFLAGS		+= $(GENERALFLAGS) \
			-lboost_date_time\
    			-lprotobuf \
			-lboost_program_options \
			-lboost_signals \
			-lboost_system \
			-lpthread \
			-lbluetooth \
			-lpython$(PYTHON_VERSION) -ldl -lpthread -lutil -lboost_python
    			#
BUILD = build

LIBRARIES = -L$(AZOUKDIR)/lib -lmultiplexer
TARGETS = tmsi_server test_server test_driver dummy_receiver signal_receiver
all: $(TARGETS)

clean:
	rm -rf $(BUILD)
	rm $(TARGETS)

fusbi_install:
	cd fusbi; \
	sudo make install
tmsi_server:  $(addprefix $(BUILD)/, AmplifierServer.o tmsiAmpServer.o variables.pb.o TmsiAmplifier.o tmsi.o AmplifierDriver.o)
	$(CXX) -o $@ $(LDFLAGS) $^ $(LIBRARIES)

test_server: $(addprefix $(BUILD)/, AmplifierServer.o testAmplifierServer.o variables.pb.o AmplifierDriver.o)
	$(CXX) -o $@ $(LDFLAGS) $^ $(LIBRARIES)

test_driver: $(addprefix $(BUILD)/, TmsiAmplifier.o tmsi.o test_driver.o AmplifierDriver.o)
	$(CXX) -o $@ $(CXXFLAGS) -lboost_date_time -lbluetooth $^

dummy_receiver: $(BUILD)/DummyReceiver.o
	$(CXX) -o $@ $(LDFLAGS) $(LIBRARIES) $^

signal_receiver: $(BUILD)/SignalReceiver.o  $(BUILD)/variables.pb.o
	$(CXX) -o $@ $(LDFLAGS) $(LIBRARIES) $^


test_logger: $(BUILD)/test_logger.o
	$(CXX) -o $@ $<

$(BUILD)/%: $(BUILD)

$(BUILD)/%.o : src/%.cpp src/%.h src/Logger.h
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@

$(BUILD)/%.o :  src/tests/%.cpp
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -I src/ -c $< -o $@

src/AmplifierServer.h: $(BUILD)/variables.pb.h

$(BUILD)/tmsi.o: src/nexus/tmsi.c src/nexus/tmsi.h
	mkdir -p $(BUILD)
	$(CXX) -o $@ -c $<

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/variables.pb.h: $(ROOTDIR)/openbci/variables.proto
	mkdir -p $(BUILD)
	protoc --cpp_out='$(BUILD)' --proto_path $(ROOTDIR)/openbci/ $<

$(BUILD)/variables.pb.o: $(addprefix $(BUILD)/, variables.pb.cc variables.pb.h)
	g++ -c $(CXXFLAGS) -o $@ $<
