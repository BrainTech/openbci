# -*- coding: utf-8 -*-

#import sip
#sip.setapi('QVariant', 2)

from ugm import UgmConfigManager
from modules.ugm.gui.ugm_module_dock_widget import UGMModuleDockWidget

class ugm_module(object):
    name = u"UGM"
    
    def __init__(self): 
        self.dockWidget = None
        self.ugmConfigManager = UgmConfigManager()
    
    def buildGui(self, p_parent):
        if self.dockWidget == None:
            self.dockWidget = UGMModuleDockWidget(self.ugmConfigManager, p_parent)
        return self.dockWidget
    
