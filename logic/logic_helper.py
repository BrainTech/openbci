#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os

def restart_scenario(new_scenario, comment="Wait..."):
    print("NEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEW: "+new_scenario)
    os.system("sleep 2 && obci srv_kill && sleep 10 && obci launch "+new_scenario+" &")    
