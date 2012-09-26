KDIR	:= /lib/modules/$(shell uname -r)/build
UDEVDIR	:= /etc/udev/rules.d
FWDIR	:= /lib/firmware

obj-m	+= tmsi.o

default:
	mkdir -p .tmp_versions
	touch .tmp_versions/tmp
	$(MAKE) -C $(KDIR) SUBDIRS=`pwd` modules

install: default
	@if dpkg -s "fxload" 2>/dev/null 1>/dev/null;  then \
	echo "Package fxload is installed.";\
	else	echo "Package fxload isn't installed.\n Run sudo apt-get install fxload";\
	exit 1;\
	fi
	$(MAKE) -C $(KDIR) SUBDIRS=`pwd` modules_install
	/sbin/depmod -a
	cp -f tmsi.rules $(UDEVDIR)
	cp -f synfi_init_data $(FWDIR)
	cp -f fusbi.hex $(FWDIR)
	make clean
uninstall:
	rm -f $(FWDIR)/synfi_init_data $(UDEVDIR)/tmsi.rules $(FWDIR)/fusbi.hex
	rmmod tmsi || echo 'doesnt matter'
	modprobe -r tmsi || echo 'doesnt matter'
	rm -f `find /lib/ -name 'tmsi*'` || echo 'doesnt matter'

reinstall: uninstall install

clean:
	rm -Rf .tmsi.ko.cmd tmsi.mod.c tmsi.mod.o .tmsi.mod.o.cmd tmsi.o .tmsi.o.cmd Module.symvers .tmp_versions modules.order

distclean: clean
	rm -f tmsi.ko

test: test.c
	gcc -o test test.c
