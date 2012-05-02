#!/bin/bash

sudo apt-get install git-core g++ python-dev maven2 openjdk-6-jdk patch libboost-all-dev libbluetooth-dev fxload xsel python-dev python-serial python-pygame python-scipy python-numpy python-sip python-qt4 python-bluetooth gnulib python-xlib screen libzmq-dev python-zmq unzip python-pyaudio

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
wget https://github.com/zeromq/jzmq/zipball/master/zeromq-jzmq-semver-51-g736341e.zip
unzip zeromq-jzmq-semver-51-g736341e.zip
cd ~/zeromq*
./autogen.sh && ./configure && make && sudo make install

cd
git clone git://escher.fuw.edu.pl/git/azouk-libraries
git clone git://escher.fuw.edu.pl/git/openbci obci
cd ~/obci
git checkout mult
cd scripts/
./install_mx_and_drivers.sh
sudo python obci_env_prepare.py `cd ~/obci && pwd` `whoami`
