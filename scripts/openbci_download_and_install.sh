#!/bin/bash

sudo apt-get install git-core g++ python-dev maven2 openjdk-6-jdk patch libboost-all-dev libbluetooth-dev fxload xsel python-dev python-serial python-pygame python-scipy python-numpy python-sip python-qt4 python-bluetooth gnulib python-xlib screen python-zmq
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
git clone http://escher.fuw.edu.pl/git/http/azouk-libraries
git clone http://escher.fuw.edu.pl/git/http/openbci
cd openbci/scripts/
./install_mx_and_drivers.sh


