#coding: utf-8
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Marian Dovgialo <marian.dowgialo@gmail.com>
#
'''
Contains HapticStimulator class to control FTDI FT2232HL in bitbang 
mode as haptic stimulator.
Tested on pyftdi 0.11.3 and pyusb 1.0.0.b2
To work requires user to have access to usb device.
On systems with udev:
add file/etc/udev/rules.d/99-FTDI.rules
with line (idVendor and idProduct might be differentfor your
stimulator):
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", MODE="666"
'''

from pyftdi.ftdi import Ftdi
import threading
import time

VENDORID = 0x0403
PRODUCTID = 0x6010
DEFAULTINTERFACE = 2 # Interface to controll
DEFAULTDIRECTION = 0xFF # All pins - output


class HapticStimulator(object):
    '''
    Class to initialise and send commands to sensory stimulator built 
    on FTDI FT2232HL with power trasistors board
    ("fMRI Pneumatic 5V version") from Politechnika Warszawska
    '''
    def __init__(self, vendorid=VENDORID, productid=PRODUCTID,
                        interface=DEFAULTINTERFACE):
        '''
        Initialises FTDI device as Haptic Stimulator
        
        :param vendorid: int or hex NOT string
        gotten from lsusb for FTDI device
        :param productid: int or hex NOT string
        gotten from lsusb for FTDI device
        :param interface: int - for tested board is always 2'''
        self.ftdi = Ftdi()
        self.ftdi.open_bitbang(vendorid, productid, interface, 
                                direction = 0xFF)
                                # direction FF - all ports output
        self.lock = threading.RLock()
        self.ftdi.write_data([0]) # turn off all channels
        
    def __del__(self):
        self.close()
    
    def _turn_off(self, chnl):
        '''
        Will turn off selected channel, used by stimulate method on
        on timer
        
        :param chnl: int - number of channel to turn off
        '''
        with self.lock:
            apins = self.ftdi.read_pins()
            activation_mask = ~(1 << (chnl-1)) & 0xFF #select only 
                                                      #needed channel
            self.ftdi.write_data([apins & activation_mask])
    
    def stimulate(self, chnl, time):
        '''
        Turn on stimulation on channel number chnl for time seconds
        
        :param chnl: integer - channel number starting from 1
        :param time: float - stimulation length in seconds
        '''
        t = threading.Timer(time, self._turn_off, [chnl]) # we expect 
                                                #short times ~ seconds
                                                #handling timers 
                                                #should not matter
        t.daemon = True # timer thread shall end immediately at main
                        # program shutdown, because interface must be
                        # closed by then and every channel turned off by
                        # .close() method. No need to wait for 
                        # schedueled stimulation end.
        t.start()
        with self.lock:
            apins = self.ftdi.read_pins()
            activation_mask = 1 << (chnl-1) # create byte with bit on
                                            # corresponding channel
                                            # enabled
            self.ftdi.write_data([apins | activation_mask]) #add active bit
                                                       # to other active
                                                       # channels
        
        
    def bulk_stimulate(self, chnls, times):
        '''
        Enables multiple channels for some time in seconds
        
        len(chnls) should be equal to len(times)
        
        :param chnls: list of integers - channels to activate
        :param times: list of floats - activation time lenghts for
        corresponding channel
        '''
        if len(chnls) != len(times):
            raise Exception(
              'Stimulation channels and times are not the same length!'
                )
        for c, t in zip(chnls, times):
            self.stimulate(c, t)
    
    def close(self):
        '''Releasing device'''
        self.ftdi.write_data([0]) # turn off all channels
        self.ftdi.usb_dev.reset() # release device
        
                                
if __name__ == "__main__":
    g = HapticStimulator()
    g.bulk_stimulate([1, 2], [0.5, 0.3])
    time.sleep(1)
    g.stimulate(1, 3)
    time.sleep(1)
    g.stimulate(2, 1)
    time.sleep(3)
        
