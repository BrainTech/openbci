#!/bin/bash
cur=`pwd`
cd ../drivers/eeg/cpp_amplifiers/
make install
cd $cur
