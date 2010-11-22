PYTHON_VERSION	:= $(shell python --version 2>&1 | sed 's/^[^0-9]*\([0-9]\+\)\.\([0-9]\+\).*/\1.\2/')
ROOTDIR		:= ../../../
AZOUKDIR	:= $(ROOTDIR)azouk-libraries
SOURCEDIRS	:= azlib multiplexer mxcontrol-commands azouk
SOURCEDIRS	:=$(addprefix $(AZOUKDIR)/build/,$(SOURCEDIRS))
CXX		:= g++
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
INCLUDEDIRS =			-I . \
			-I $(AZOUKDIR)/build \
			-I $(AZOUKDIR)/src/azouk \
			-I $(AZOUKDIR)/build/azlib \
			-I $(ROOTDIR)/openbci \
			-fPIC \
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
LIBRARIES	:= $(shell find $(SOURCEDIRS) -name '*.o' | grep -v '\.svn')
TARGETS = tmsi_server test_server test_driver dummy_receiver
all: $(TARGETS)

clean:
	rm -rf $(BUILD)
	rm $(TARGETS) src/variables.pb.h

fusbi_install:
	cd fusbi; \
	sudo make install

tmsi_server:  $(addprefix $(BUILD)/, AmplifierServer.o variables.pb.o tmsiAmpServer.o TmsiAmplifier.o tmsi.o AmplifierDriver.o)
	$(CXX) -o $@ $(LDFLAGS) $^ $(LIBRARIES)

test_server: $(addprefix $(BUILD)/, AmplifierServer.o testAmplifierServer.o variables.pb.o AmplifierDriver.o)
	$(CXX) -o $@ $(LDFLAGS) $^ $(LIBRARIES)

test_driver: $(addprefix $(BUILD)/, TmsiAmplifier.o tmsi.o test_driver.o AmplifierDriver.o)
	$(CXX) -o $@ $(CXXFLAGS) -lboost_date_time -lbluetooth $^

dummy_receiver: $(BUILD)/DummyReceiver.o
	$(CXX) -o $@ $(LDFLAGS) $(LIBRARIES) $^

test_logger: $(BUILD)/test_logger.o
	$(CXX) -o $@ $<

$(BUILD)/%.o : src/%.cpp src/%.h build/ src/Logger.h
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -c $< -o $@

$(BUILD)/%.o :  src/tests/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDEDIRS) -I src/ -c $< -o $@

build/:
	mkdir $(BUILD)

$(BUILD)/tmsi.o: src/nexus/tmsi.c src/nexus/tmsi.h
	$(CXX) -o $@ -c $<
	

SOURCES := AmplifierServer.cpp tests/testAmplifierServer.cpp tmsiAmpServer.cpp


src/variables.pb.h: $(BUILD)/variables.pb.cc
	ln $(BUILD)/variables.pb.h src/variables.pb.h
$(BUILD)/variables.pb.cc: $(ROOTDIR)/openbci/variables.proto
	protoc --cpp_out='$(BUILD)' --proto_path $(ROOTDIR)/openbci/ $<

$(BUILD)/variables.pb.o: $(addprefix $(BUILD)/, variables.pb.cc variables.pb.h)
	g++ -c $(CXXFLAGS) -o $@ $<



