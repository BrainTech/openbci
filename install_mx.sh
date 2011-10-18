#!/bin/bash

p=$1
if [ -z $p ]
then
    p=$HOME
fi

curr=`pwd`
az_path=$p/azouk-libraries


cd $az_path
./bootstrap.sh
./configure RULES=$curr/multiplexer.rules --prefix=$HOME/usr && make -j4 && make install 
cd $curr
ln -s $HOME/usr/ azouk-install
