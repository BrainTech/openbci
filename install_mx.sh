#!/bin/bash

az_path=$1
if [ -z $az_path ]
then
    az_path=$HOME/azouk-libraries
fi
curr=`pwd`
cd $az_path
./bootstrap.sh
./configure RULES=$curr/multiplexer.rules --prefix=$curr/multiplexer-install && make -j4 && make install 
cd $curr
