#!/bin/bash
cd
mkdir tmp
cd tmp

H=linux-headers-3.1.0-030100rc10-generic_3.1.0-030100rc10.201110200610_i386.deb
H_WWW=http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.1-rc10-oneiric/linux-headers-3.1.0-030100rc10-generic_3.1.0-030100rc10.201110200610_i386.deb

H_GEN=linux-headers-3.1.0-030100rc10_3.1.0-030100rc10.201110200610_all.deb
H_GEN_WWW=http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.1-rc10-oneiric/linux-headers-3.1.0-030100rc10_3.1.0-030100rc10.201110200610_all.deb

I=linux-image-3.1.0-030100rc10-generic_3.1.0-030100rc10.201110200610_i386.deb
I_WWW=http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.1-rc10-oneiric/linux-image-3.1.0-030100rc10-generic_3.1.0-030100rc10.201110200610_i386.deb

wget $H_WWW
wget $H_GEN_WWW
wget $I_WWW

sudo dpkg -i $H_GEN
sudo dpkg -i $H
sudo dpkg -i $I