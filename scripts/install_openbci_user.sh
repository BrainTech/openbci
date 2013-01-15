#!/usr/bin
cd
sudo apt-get update && sudo apt-get install tmsi-dkms
sudo apt-get remove openbci-core
git clone git://git.braintech.pl/openbci.git
cd openbci/scripts
./install_mx.sh
mkdir -p ~/bin
ln -s ~/openbci/control/gui/obci_gui ~/bin/obci_gui
ln -s ~/openbci/control/launcher/obci ~/bin/obci
echo 'export OBCI_INSTALL_DIR=~/openbci' >> ~/.bahsrc
mkdir -p ~/.local/lib/python2.7/site-packages/obci
ln -s  ~/openbci ~/.local/lib/python2.7/site-packages/obci
