#!/bin/bash
p=$1
if [ -z $p ]
then
	echo "Add ssh user name as a first argument, eg: ./openbci_download_and_install_dev.sh mati"
	exit -1
fi
sudo apt-get install git-core g++ python-dev maven2 openjdk-6-jdk patch libboost-all-dev libbluetooth-dev fxload xsel python-dev python-serial python-pygame python-scipy python-numpy python-sip python-qt4 python-bluetooth gnulib python-xlib
cd
wget http://protobuf.googlecode.com/files/protobuf-2.4.1.tar.bz2
tar -xvf protobuf-2.4.1.tar.bz2
cd protobuf-2.4.1
./configure --prefix=/usr/
make
sudo make install
cd python
echo "export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp; python setup.py install" | sudo sh
cd ../java
mvn test && mvn install
cd
git clone ssh://$1@escher.fuw.edu.pl/git/azouk-libraries
git clone ssh://$1@escher.fuw.edu.pl/git/openbci
cd openbci
./install_mx_and_drivers.sh
