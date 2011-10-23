#!/bin/bash
cur=`pwd`
cd openbci/amplifiers/c_tmsi_amplifier/tmsi/
sudo make install
cd ..
make
cd $cur
