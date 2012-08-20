#!/bin/sh
deps='git-core python-dev libboost-all-dev libbluetooth-dev xsel python-dev python-serial python-pygame python-scipy python-numpy python-sip python-qt4 python-bluetooth python-xlib libzmq-dev python-zmq python-pyaudio libprotobuf-dev'

./openbci_add_deb_repo_precise.sh
sudo apt-get update
sudo apt-get install $deps tmsi-dkms openbci-libmultiplexer-dev openbci-dummy-amplifier openbci-file-amplifier openbci-libmultiplexer0 openbci-multiplexer openbci-multiplexer-python openbci-tmsi-amplifier

sudo python obci_env_prepare.py `cd openbci && pwd` `whoami`
