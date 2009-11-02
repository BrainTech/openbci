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
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#


import serial

ser = serial.Serial('/dev/ttyUSB0', baudrate=9600)

def ct(a):
	return 16 *  (10 ** 6) / 256 / a

def to_hex_word(a):
	return chr(a / 256) + chr(a % 256)

def magic(a, x=0.5):
	w = ct(a)
	return to_hex_word(int(w * x)) + to_hex_word(int(w * (1 - x)))

def mrygaj(czym, jak, x=0.5, on=True):
	ser.write(chr(czym) + chr(0 if on else 2) + magic(jak, x))


  
