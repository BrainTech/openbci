#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os

def restart_scenario(new_scenario, comment="Wait..."):
    os.system("sleep 3 && obci srv_kill && sleep 5 && obci launch "+new_scenario+" &")    
