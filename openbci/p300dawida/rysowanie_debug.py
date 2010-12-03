# -*- coding: utf-8 -*-
## imports essential moduls 
import numpy as np
import sys, os, math
import PyQt4

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

## As can be read: MULTIPLEXER
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings


#import samples_pb2
import variables_pb2


class PlotHandler(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(PlotHandler, self).__init__(addresses=addresses, type=peers.ANALYSIS)
        print "created plot handler" 
        #self.importData()
        
        # Creats class resposible for plotting data
        #app = PyQt4.QtGui.QApplication(sys.argv)
        #self.plot = PlotingAnalysis(self.data)
        #self.plot.show()
    
        #sys.exit(app.exec_())

        
    def handle_message(self, mxmsg):
	print "handle ", mxmsg.type
	
        if mxmsg.type == DIODE_MESSAGE:
	    print "DIODE MESSAGE"
            t = variables_pb2.Blink()
            t.ParseFromString(mxmsg.message)
            self.diodeTime = t.timestamp             
            self.dataBank.ParseFromString(self.conn.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
            print "self.dataBank ",  self.dataBank  
            self.drawPlot()
                    
        self.no_response()

if __name__ == "__main__":
    PlotHandler(settings.MULTIPLEXER_ADDRESSES).loop()
