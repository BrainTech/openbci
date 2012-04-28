BASE = dummy_amplifier test_server test_logger test_dummy_amplifier
TMSI = tmsi_amplifier test_tmsi_amplifier 
GTEC = gtec_amplifier test_gtec_amplifier 
FILE = file_amplifier test_file_amplifier
RECEIVER = dummy_receiver signal_receiver

INSTALLS = install_gtec install_tmsi

TARGETS = tmsi_amplifier gtec_amplifier file_amplifier dummy_amplifier
TESTS = $(addprefix test_,$(TARGETS)) test_server test_logger

LN = @cp -f



all: $(TARGETS) $(RECEIVER) $(TESTS)

tests: $(TESTS)

amplifiers: $(TARGETS)

receivers: $(RECEIVER)

$(BASE): force_look
	@cd base;make $@
	$(LN) base/$@ $@

$(TMSI): force_look
	@cd tmsi;make $@
	$(LN) tmsi/$@ $@

$(FILE): force_look
	@cd file;make $@
	$(LN) file/$@ $@

$(GTEC): force_look
	@cd gtec;make $@
	$(LN) gtec/$@ $@
	$(LN) gtec/simple_gtec_driver simple_gtec_driver

$(RECEIVER): force_look
	@cd receiver;make $@
	$(LN) receiver/$@ $@
$(INSTALL) : force_look

install_gtec:
	@cd gtec;make $@
    
install_tmsi:
	@cd tmsi;make $@
    
	
force_look:
	@true
 