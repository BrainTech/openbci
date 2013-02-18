BASE = dummy_amplifier test_server test_logger test_dummy_amplifier
TMSI = tmsi_amplifier test_tmsi_amplifier 
GTEC = gtec_amplifier test_gtec_amplifier 
FILE = file_amplifier test_file_amplifier
RECEIVER = dummy_receiver signal_receiver

INSTALLS = install_gtec install_tmsi

TARGETS = tmsi_amplifier file_amplifier dummy_amplifier
TESTS = $(addprefix test_,$(TARGETS)) test_server test_logger

BIN=bin/
BUILD=build/
MAKE_BIN = make $(BIN)$@
LN_= @ln -f
LN = $(LN_) $(BIN)/$@ $@
amplifiers: $(TARGETS)

all: $(TARGETS) $(RECEIVER) $(TESTS)

install:
	sudo make install_tmsi install_gtec
	make $(TARGETS) 
	make gtec_amplifier || true

tests: $(TESTS)



receivers: $(RECEIVER)
base: $(BASE)
tmsi: $(TMSI)
gtec: $(GTEC)
file: $(FILE)

$(BASE): force_look
	@cd base;$(MAKE_BIN)
	$(LN)

$(TMSI): force_look
	@cd tmsi;$(MAKE_BIN)
	$(LN)

$(FILE): force_look
	@cd file;$(MAKE_BIN)
	$(LN)

$(GTEC):: force_look
	cd gtec;$(MAKE_BIN)
	$(LN)

$(GTEC)::
	$(LN_) $(BIN)simple_gtec_driver simple_gtec_driver

$(RECEIVER): force_look
	@cd receiver;$(MAKE_BIN)
	$(LN)

$(INSTALL) : force_look

install_gtec:
	@cd gtec;make $@

install_tmsi:
	@cd tmsi;make $@

force_look:
	@true

clean:
	rm -rf build
	rm -f $(TARGETS) $(TESTS) $(RECEIVER)
