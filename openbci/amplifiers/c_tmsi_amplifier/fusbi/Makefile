KDIR	:= /lib/modules/$(shell uname -r)/build
UDEVDIR	:= /etc/udev/rules.d
FWDIR	:= /lib/firmware

obj-m	+= fusbi.o

default:
	$(MAKE) -C $(KDIR) SUBDIRS=`pwd` modules

install: default
	$(MAKE) -C $(KDIR) SUBDIRS=`pwd` modules_install
	/sbin/depmod -a

	cp -f fusbi.hex $(FWDIR)
	cp -f fusbi.rules $(UDEVDIR)

uninstall:
	rm -f $(FWDIR)/fusbi.hex $(UDEVDIR)/fusbi.rules

clean:
	rm -Rf .fusbi.ko.cmd fusbi.mod.c fusbi.mod.o .fusbi.mod.o.cmd fusbi.o .fusbi.o.cmd Module.symvers .tmp_versions

distclean: clean
	rm -f fusbi.ko
test: test.c
	gcc -o test test.c
