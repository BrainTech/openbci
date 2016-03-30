#!/bin/bash
all_libs=libgusbampapi*

if [ `uname -m` == x86_64 ]; then
	lib_src="libgusbampapi*64*.1.11.*"
else
	lib_src="libgusbampapi*32*.1.11.*"
fi

lib_target="/usr/lib/";
header_src="gAPI.h";
header_target="/usr/include/";
filter_src="*filter*.bin";
filter_target="/etc/gtec/filter_files/";
doc_license_src="license.pdf";
doc_api_src="gUSBamp_PC_API_for_Linux_1_11_*.pdf";
doc_target="/usr/share/doc/gtec/gUSBampAPI_1_11_00/";

echo COPYRIGHT © 2011 G.TEC MEDICAL ENGINEERING GMBH, AUSTRIA
echo ... install the g.USBamp API
mkdir -p $doc_target ;
cp $doc_api_src $doc_target ;
cp $doc_license_src $doc_target ;
rm -f $lib_target$all_libs ;
ldconfig
cp $lib_src $lib_target ;
ldconfig
cp $header_src $header_target ;
mkdir -p $filter_target ;
cp $filter_src $filter_target ;
cp gtec.rules /etc/udev/rules.d
udevadm control --reload-rules
echo ... done
