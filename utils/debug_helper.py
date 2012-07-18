#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

def get_str_variable_vector(vect):
    ret = ''
    for v in vect.variables:
        ret = ''.join([ret, v.key, " : ",v.value, "\n"])
    return ret
