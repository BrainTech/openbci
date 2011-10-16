#!/bin/bash
ln -s $HOME/azouk-libraries azouk-libraries
cd azouk-libraries/
./configure RULES=../multiplexer.rules --prefix=$HOME/usr && make -j4 && make install 
cd ..
ln -s $HOME/usr/ azouk-install
