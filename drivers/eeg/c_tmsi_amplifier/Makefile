PYTHON_VERSION	:= $(shell python --version 2>&1 | sed 's/^[^0-9]*\([0-9]\+\)\.\([0-9]\+\).*/\1.\2/')
ROOTDIR		= ../../..
AZOUKDIR	= `cd $(ROOTDIR)/multiplexer-install;pwd`
CXX		= g++
O		= -g #-O2
GENERALFLAGS	+= $(O) -Wall \
			-DBOOST_DISABLE_THREADS \
			#
ifdef DEBUG
GENERALFLAGS	+= -DAMP_DEBUG
endif

CXXFLAGS	+= $(GENERALFLAGS) -fpermissive
INCLUDEDIRS =			-I . -I/usr/share/multiplexer/src \
			-I$(AZOUKDIR)/include \
			-I$(ROOTDIR)/openbci \
			-fPIC \
			-Ibuild
			#

LDFLAGS		+= $(GENERALFLAGS) \
			-lprotobuf \
			-lpthread \
			-lpython$(PYTHON_VERSION) -ldl -lpthread -lutil \
			-Wl,--rpath,$(AZOUKDIR)/lib


#WINDOWS :=1
ifdef WINDOWS
GENERALFLAGS	+= -DWINDOWS -D__USE_W32_SOCKETS
LDFLAGS	+=-lboost_program_options-mt \
			-lboost_signals-mt \
			-lboost_system-mt \
			-lboost_python-mt
LDFLAGS_TEST	= -lboost_date_time-mt
else
GENERALFLAGS	+=	-DBLUETOOTH -DBOOST
LDFLAGS_TEST +=	-lbluetooth -lboost_date_time -lboost_program_options
LDFLAGS	+=	-lboost_signals \
			-lboost_system \
			-lboost_python
endif
LDFLAGS +=	$(LDFLAGS_TEST) 
BUILD = build

LIBRARIES	:= -L$(AZOUKDIR)/lib -lmultiplexer

TARGETS = tmsi_driver_server signal_receiver
TESTS=  test_server test_tmsi_driver test_dummy_driver  test_logger  dummy_receiver dummy_tmsi_driver_server
AMPLIFIER_DRIVER = AmplifierDriver.o AmplifierDescription.o
AMPLIFIER_SERVER = variables.pb.o AmplifierServer.o
TMSI_DRIVER = $(AMPLIFIER_DRIVER) TmsiAmplifier.o TmsiChannels.o TmsiDriverDesc.o tmsi.o

all: $(TARGETS)

clean:
	rm -rf $(BUILD)
	rm $(TARGETS) $(TESTS)
tests : $(TESTS)

tmsi_install:
	cd tmsi; \
	make
	sudo make install
test_server: $(addprefix $(BUILD)/, $(AMPLIFIER_DRIVER) $(AMPLIFIER_SERVER) test_server.o)
	$(CXX) -o $@ $^ $(LDFLAGS) $(LIBRARIES) 
	
dummy_tmsi_driver_server: $(addprefix $(BUILD)/, $(AMPLIFIER_DRIVER) $(AMPLIFIER_SERVER) dummy_tmsi_driver_server.o)
	$(CXX) -o $@ $^ $(LDFLAGS) $(LIBRARIES)


test_tmsi_driver: src/tests/test_driver.h $(addprefix $(BUILD)/, test_tmsi_driver.o  $(TMSI_DRIVER))
	$(CXX) -o $@ $(CXXFLAGS) $^ $(LDFLAGS_TEST) 

test_dummy_driver: src/tests/test_driver.h $(addprefix $(BUILD)/, test_driver.o  $(AMPLIFIER_DRIVER))
	$(CXX) -o $@ $(CXXFLAGS) $^ $(LDFLAGS_TEST) 

tmsi_driver_server: $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) $(TMSI_DRIVER) tmsi_driver_server.o)
	$(CXX) -o $@ $(CXXFLAGS) $(INCLUDEDIRS) $(LDFLAGS) $(LIBRARIES) $^  

dummy_receiver: $(BUILD)/DummyReceiver.o
	$(CXX) -o $@ $(LDFLAGS) $(LIBRARIES) $^

signal_receiver: $(BUILD)/SignalReceiver.o  $(BUILD)/variables.pb.o
	$(CXX) -o $@ $(LDFLAGS) $(LIBRARIES) $^

test_logger: $(BUILD)/test_logger.o
	$(CXX) -o $@ $<

$(BUILD)/%: $(BUILD)

$(BUILD)/AmplifierDriver.o: src/AmplifierDriver.cpp src/AmplifierDriver.h src/Logger.h $\
						$(addprefix $(BUILD)/, AmplifierDescription.o)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@


$(BUILD)/TmsiAmplifier.o: src/TmsiAmplifier.cpp src/TmsiAmplifier.h src/Logger.h \
						$(addprefix $(BUILD)/, AmplifierDriver.o TmsiChannels.o TmsiDriverDesc.o)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@

$(BUILD)/AmplifierServer.o: src/AmplifierServer.cpp src/AmplifierServer.h $(BUILD)/variables.pb.o
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@

$(BUILD)/%.o :  src/%.cpp src/%.h src/Logger.h
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@
	
$(BUILD)/%.o :  src/%.cpp
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@

$(BUILD)/%.o :  src/tests/%.cpp src/tests/%.h
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -I src/ -c $< -o $@


$(BUILD)/%.o :  src/tests/%.cpp
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -I src/ -c $< -o $@

	

src/AmplifierServer.h: $(BUILD)/variables.pb.h

$(BUILD)/tmsi.o: src/nexus/tmsi.c src/nexus/tmsi.h
	mkdir -p $(BUILD)
	$(CXX) -o $@ -c $<

$(BUILD):
	mkdir -p $(BUILD)
$(BUILD)/variables.pb.cc:	$(BUILD)/variables.pb.h
$(BUILD)/variables.pb.h: $(ROOTDIR)/configs/variables.proto
	mkdir -p $(BUILD)
	protoc --cpp_out='$(BUILD)' --proto_path $(ROOTDIR)/configs/ $<

$(BUILD)/variables.pb.o: $(addprefix $(BUILD)/, variables.pb.cc variables.pb.h)
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@
