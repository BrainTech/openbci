# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#      Łukasz Polak <l.polak@gmail.com>
#
"""Module file for UGM - builds GUI to configure it"""

from gui.ugm.ugm_config_manager import UgmConfigManager
from gui.frontend.modules.ugm.ugm_module_dock_widget import UGMModuleDockWidget

class UgmModule(object):
    """Module file for UGM. Creates and manages its configuration GUI"""

    #name of this module, that will be shown in GUI
    name = u"UGM"
    
    def __init__(self): 
        self.dockWidget = None
        self.ugmConfigManager = UgmConfigManager()
    
    def buildGui(self, p_parent):
        """Return configuration GUI in form of dock widget"""
        if self.dockWidget == None:
            self.dockWidget = UGMModuleDockWidget(self.ugmConfigManager, p_parent)
        return self.dockWidget
    
