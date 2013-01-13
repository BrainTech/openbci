#!/bin/sh               

sudo apt-get install git

git clone -b stable git://git.braintech.pl/openbci.git openbci
cd openbci/scripts
./openbci_install.sh
