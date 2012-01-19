#!/bin/bash
cur=`pwd`
cd ../drivers/eeg/c_tmsi_amplifier/tmsi/
sudo make install
cd ..
make
cd $cur
