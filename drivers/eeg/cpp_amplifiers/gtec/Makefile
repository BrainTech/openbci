include ../base/Makefile.common

LIBS = -l:libgusbampapi.so.1.11
OBJS = $(BUILD)/simple_gtec_driver.o
SIMPLE = simple_gtec_driver
BOOST_LIBS = signals thread regex date_time
BOOST_VERSION= 1.42.0
BOOST_LIBS_PATHS = $(addsuffix .so.$(BOOST_VERSION), $(addprefix lib/libboost_, $(BOOST_LIBS)))
API_INSTALLED = /usr/include/gAPI.h
LIB_PATH = $(abspath lib)
GTEC = GTecAmplifier.o GTecDescription.o
all: simple_gtec_driver

boost_1_42_0.tar.bz2:
	wget http://sourceforge.net/projects/boost/files/boost/1.42.0/boost_1_42_0.tar.bz2/download -O boost_1_42_0.tar.bz2

boost_1_42_0: 
	make boost_1_42_0.tar.bz2 
	tar --bzip2 -xf boost_1_42_0.tar.bz2
	cd boost_1_42_0;sh bootstrap.sh
	
lib/libboost%: boost_1_42_0
	cd boost_1_42_0;./bjam $(addprefix --with-,$(BOOST_LIBS)) --stagedir=../ 

simple_gtec_driver:  $(OBJS) $(BOOST_LIBS_PATHS) $(API_INSTALLED)
	$(CC) $(CFLAGS) -o $@ $(OBJS) -L$(LIB_PATH) -Wl,--rpath=$(LIB_PATH) $(addprefix -lboost_,$(BOOST_LIBS)) $(LIBS)

$(API_INSTALLED):
	make install_gtec


install_gtec:
	cd api;sudo sh install.sh

clean::
	rm -f *.o
	rm $(TARGET)

test_gtec_amplifier: $(SIMPLE) $(addprefix $(BUILD)/, $(AMPLIFIER) $(GTEC) test_gtec_amplifier.o test_amplifier.o)
	$(CXX) -o $@ $(wordlist 2,100,$^)	$(LD_AMPLIFIER)
 
gtec_amplifier:$(SIMPLE) $(addprefix $(BUILD)/, $(AMPLIFIER_SERVER) $(GTEC) gtec_amplifier_main.o)
	$(CXX) -o $@ $(wordlist 2,100,$^)	$(LD_SERVER)

