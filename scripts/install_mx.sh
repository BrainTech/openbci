#!/bin/bash

az_path=$1
if [ -z $az_path ]
then
    az_path=../../azouk-libraries
fi
curr=`pwd`
top=`cd ../;pwd`
cd $az_path
./bootstrap.sh
./configure RULES=$top/configs/multiplexer.rules --prefix=$top/multiplexer-install && make && make install 
cd $curr
