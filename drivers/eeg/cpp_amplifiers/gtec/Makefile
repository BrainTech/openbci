include ../base/Makefile.common

LIBS = -l:libgusbampapi.so.1.11
OBJS = $(BUILD)/simple_gtec_driver.o
SIMPLE = $(BIN)/simple_gtec_driver
BOOST_LIBS = signals thread regex date_time
BOOST_VERSION= 1.42.0
BOOST_LIBS_PATHS = $(addsuffix .so.$(BOOST_VERSION), $(addprefix lib/libboost_, $(BOOST_LIBS)))
API_INSTALLED = /usr/include/gAPI.h
LIB_PATH = $(abspath lib)
GTEC = GTecAmplifier.o GTecDescription.o

ALL = gtec_amplifier test_gtec_amplifier

#This is for command line completion
$(ALL):

boost_1_42_0.tar.bz2:
	wget http://sourceforge.net/projects/boost/files/boost/1.42.0/boost_1_42_0.tar.bz2/download -O boost_1_42_0.tar.bz2

boost_1_42_0/bjam:
	make boost_1_42_0.tar.bz2
	tar --bzip2 -xf boost_1_42_0.tar.bz2
	cd boost_1_42_0;sh bootstrap.sh

lib/libboost%:
	make boost_1_42_0/bjam
	cd boost_1_42_0;./bjam $(addprefix --with-,$(BOOST_LIBS)) --stagedir=../

$(SIMPLE):  $(OBJS) $(BOOST_LIBS_PATHS) $(API_INSTALLED)
	$(CXX) $(CFLAGS) -o $@ $(OBJS) -L$(LIB_PATH) -Wl,--rpath=$(LIB_PATH) $(addprefix -lboost_,$(BOOST_LIBS)) $(LIBS)

$(API_INSTALLED):
	make install_gtec

install_gtec:
	cd api;sudo sh install.sh

$(BIN)/test_gtec_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER) $(GTEC) test_gtec_amplifier.o test_amplifier.o)
	$(LD_AMPLIFIER)
	make $(SIMPLE)
	
$(BIN)/gtec_amplifier: $(CHECK_BIN) $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) $(GTEC) gtec_amplifier_main.o)
	$(LD_SERVER)
	make $(SIMPLE)