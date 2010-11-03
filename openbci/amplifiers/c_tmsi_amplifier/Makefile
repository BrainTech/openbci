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
			-lpython$(PYTHON_VERSION) -ldl -lpthread -lutil -lboost_python
    			#

LIBRARIES	:= $(shell find $(SOURCEDIRS) -name '*.o' | grep -v '\.svn')

AmplifierDriver.o: AmplifierDriver.cpp AmplifierDriver.h
	g++ -c $(CXXFLAGS) $<
	
test_driver: TmsiAmplifier.o tmsi.o tests/test_driver.cpp AmplifierDriver.o
	g++ -o $@ $(CXXFLAGS) -lboost_date_time $^

TmsiAmplifier.o: TmsiAmplifier.cpp
	g++ -c $(CXXFLAGS) $<
tmsi.o: nexus/tmsi.c
	g++ -c $(CXXFLAGS) $<
	
SOURCES := AmplifierServer.cpp tests/testAmplifierServer.cpp tmsiAmpServer.cpp


testServer: AmplifierServer.o testAmplifierServer.o variables.pb.o AmplifierDriver.o
	g++ -o $@ $(LDFLAGS) $^ $(LIBRARIES)

objects: $(SOURCES)
	g++ -c $(CXXFLAGS) $(INCLUDEDIRS) $^

AmplifierServer.o: AmplifierServer.cpp
	g++ -c $(CXXFLAGS) $(INCLUDEDIRS) $<

testAmplifierServer.o: tests/testAmplifierServer.cpp
	g++ -c $(CXXFLAGS) $(INCLUDEDIRS) $<

tmsiAmpServer.o: tmsiAmpServer.cpp
	g++ -c $(CXXFLAGS) $(INCLUDEDIRS) $^

variables.pb.cc: $(ROOTDIR)/openbci/variables.proto
	protoc --cpp_out='.' --proto_path $(ROOTDIR)/openbci/ $<

variables.pb.o: variables.pb.cc
	g++ -c $(CXXFLAGS) $<

tmsiAmpServer:  AmplifierServer.o variables.pb.o tmsiAmpServer.o TmsiAmplifier.o tmsi.o Logger.h AmplifierDriver.o
	g++ -o $@ $(LDFLAGS) $^ $(LIBRARIES)

clean:
	rm tmsi.o TmsiAmplifier.o

test_logger: tests/test_logger.cpp Logger.h
	g++ -o $@ $<

dummyReceiver: DummyReceiver.cpp DummyReceiver.h
	g++ -o $@ $(LDFLAGS) $(INCLUDEDIRS) $(LIBRARIES) $^ 