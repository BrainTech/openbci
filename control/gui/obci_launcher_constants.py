#!/usr/bin/env python
# -*- coding: utf-8 -*-

from launcher.launcher_tools import NOT_READY, READY_TO_LAUNCH, LAUNCHING, \
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED

STATUS_COLORS = {
    NOT_READY : 'dimgrey',
    READY_TO_LAUNCH : 'bisque',
    LAUNCHING : 'lightseagreen',
    FAILED_LAUNCH : 'red',
    RUNNING : 'lightgreen',
    FINISHED : 'lightblue',
    FAILED : 'red',
    TERMINATED : 'khaki'
    }


