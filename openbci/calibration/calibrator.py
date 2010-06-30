# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#      Joanna Tustanowska <asia.tustanowska@gmail.com>
#
#"""
#A module displaying amplitude info during experiment.
#"""

import sys
import numpy

import matplotlib.pyplot as plt

import calibration_logging
LOGGER = calibration_logging.get_logger('calibrator')

import signal_prep
import calibration_analysis
import plotting


class OfflineCalibrator(object):
    def __init__(self):

    	if (len(sys.argv) < 2):
    	    print "usage: ./calibrator.py <mode:1|2> \
    	        <base_signal_file_name> <dir> <channel_number>"
            return
        # TODO get params
        self.mode = int(sys.argv[1]) 
    	self.sig_file_name = sys.argv[2]
        self.dir = sys.argv[3]
        self.chan_no = int(sys.argv[4])


    def run(self):
        
        prep = signal_prep.OfflineSignalPrep(
                    base_file_name=self.sig_file_name, dir_path=self.dir)
        LOGGER.info("Offline signal preparation finished: " + \
                    "file_name: " + self.sig_file_name + " dir: " + self.dir)
        
        props = {}
        LOGGER.info("Calibration Mode: " + str(self.mode))
        if self.mode == 1:
            tags, freqs, amplitudes =  calibration_analysis.single_freq_test(prep, self.chan_no)
            LOGGER.info("Analysed chunks of data for single freqs (one field blinking): " + \
                        " \nFREQS: " + str(freqs) + " \nAmplitudes: " + str(amplitudes))
            
            props['fig_title'] = "Test of a sequence of single frequencies"
            props['ax_title'] = "channel: " + str(self.chan_no) + " /// display time: " + str(tags[0]['desc']['desc']['delay']) + \
                                "s"
                                    
            fig = plt.figure()
            fig.subplots_adjust(bottom=0.2)
            ax = fig.add_subplot(111)                        
            plotting.draw_bars_single_freq(ax, freqs, amplitudes, 0.3, tags, squares=True, props=props)
            plt.show()
        elif self.mode == 2:
            tags, diff_chunks = calibration_analysis.multi_freq_stat_test(prep, self.chan_no)
            LOGGER.info("Analysed chunks of data for multi freq test, number of tested frequencies: " + \
                        str(len(diff_chunks)) + " fr set: " + str(diff_chunks[0][1]))
            
            props['fig_title'] = "Differences per frequency, channel: " + '%d'%self.chan_no
            plotting.draw_bars_multi_freq_sequence(diff_chunks, tags, 0.2, squares=True, props=props)
            plotting.draw_multi_freq(diff_chunks, tags, props=props)
        
            plt.show()
        else:
            print "Unknown calibration mode!"
       

if __name__ == "__main__":
    cal = OfflineCalibrator() #settings.MULTIPLEXER_ADDRESSES

    cal.run()
    
