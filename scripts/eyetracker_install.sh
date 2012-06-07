#!/bin/bash
cd ~
wget http://www.openframeworks.cc/versions/preRelease_v0.07/of_preRelease_v007_linux64.tar.gz
tar -xf of_preRelease_v007_linux64.tar.gz
mv of_preRelease_v007_linux64 openFrameworks
cd ~/openFrameworks/scripts/linux/ubuntu
sudo ./install_dependencies.sh
cd
sudo apt-get install libgsl0-dev
git clone git://escher.fuw.edu.pl/git/eyetracker
cd ~/eyetracker/eyetracker/
make
sudo make install




