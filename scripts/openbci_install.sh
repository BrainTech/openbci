#!/bin/sh
deps='git-core python-dev libboost-all-dev libbluetooth-dev xsel python-dev python-serial python-pygame python-scipy python-numpy python-sip python-qt4 python-bluetooth python-xlib libzmq-dev python-zmq python-pyaudio libprotobuf-dev'

sudo wget -O /etc/apt/sources.list.d/deb.braintech.pl-ubuntu-precise.list http://deb.braintech.pl/deb.braintech.pl-ubuntu-precise.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1452AFDF
sudo apt-get update
sudo apt-get install $deps tmsi-dkms

sudo python obci_env_prepare.py `cd openbci && pwd` `whoami`
