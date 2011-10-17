#!/bin/bash

p=$1
if [ -z $p ]
then
    p=$HOME
fi

ln -s $p/azouk-libraries azouk-libraries
cd azouk-libraries/
./bootstrap.sh
./configure RULES=../multiplexer.rules --prefix=$HOME/usr && make -j4 && make install 
cd ..
ln -s $HOME/usr/ azouk-install
cd openbci/amplifiers/c_tmsi_amplifier/tmsi/
sudo make install
cd ..
make


