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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
"""Module implements specific info file manifest for svarog.
What is different from info_file_proxy:
- root name (here we haver rs:rawSignal and xmlns)
- tags namespace (here every tag has rs: previx)
- tags ordering (svarog requires specific tags ordering)
- additional tags (svarog requires only and only tags described in
  SvarogFileWriteProxy.ORDER)
"""

import info_file_proxy
class SvarogDocument(info_file_proxy.OpenBciDocument):
    """Subclass xml_document, so that we can add rs: prefix before every
    tag name."""
    prefix = 'rs:'
    def createElement(self, tagName):
        """Redefine the method so that every added tag has 'rs:' prefix."""
        return super(SvarogDocument, self).createElement(
            ''.join([SvarogDocument.prefix, tagName]))

class SvarogFileWriteProxy(info_file_proxy.InfoFileWriteProxy):
    """Subclass write proxy - ensure that every element has rs: prefix,
    ensure tags ordering, ensure tags required by svarog."""
    ORDER = [
        'rs:exportFileName',
        'rs:sourceFileName',
        'rs:sourceFileFormat',
        'rs:samplingFrequency',
        'rs:channelCount',
        'rs:sampleCount',
        'rs:calibration',
        'rs:sampleType',
        'rs:byteOrder',
        'rs:pageSize',
        'rs:blocksPerPage',
        'rs:channelLabels',
        'rs:calibrationGain',
        'rs:calibrationOffset',
        'rs:firstSampleTimestamp',
        ]
    def _create_xml_factory(self):
        """Redefine the method - return Svarog document."""
        return SvarogDocument() 

    def _set_remaining_tags(self):
        """Set all default (hardcoded) tags and other tags as now we
        we have all needed data."""
        self.set_attributes({
                'file_format':[''],
                'export_file_name':'name',
                'calibration':1.0,
                'sample_type':'DOUBLE',
                'byte_order':'LITTLE_ENDIAN',
                'page_size':20.0,
                'blocks_per_page':5,
                #'export_date':'2010-04-26T11:02:51'
                })
        self._reorder_elements()
    def _reorder_elements(self):
        """Redefine self._xml_factory so that it has tags required by
        svarog in required order."""

        new_factory = self._create_xml_factory()
        l_xml_root = new_factory.createElement('rawSignal') 
        l_xml_root.setAttribute('xmlns:rs', 
                                    "http://signalml.org/rawsignal")
        new_factory.appendChild(l_xml_root)

        elems = []
        for order_key in SvarogFileWriteProxy.ORDER:
                elem = self._xml_factory.getElementsByTagName(order_key)[0]
                elems.append(elem)
                l_xml_root.appendChild(elem)

        self._xml_factory = new_factory

class SvarogFileReadProxy(info_file_proxy.InfoFileReadProxy):
    """Sublassed read proxy - every get_ method need to be subclassed 
    to add rs: prefix before tag name."""
    def _get_simple_param(self, p_param_name):
        """Return text value from tag in format:
        <param id=p_param_name>text_value</param>."""
        return super(SvarogFileReadProxy, self)._get_simple_param(
            ''.join([SvarogDocument.prefix, p_param_name]))

    def _get_list_param(self, p_param_name, p_subparam_name):
        """Return a list of text values form tag in format:
        <p_param_name>
            <param>text value1</param>
            <param>text value2</param>
            ...
        </p_param_name>
        """
        return super(SvarogFileReadProxy, self)._get_list_param(
            ''.join([SvarogDocument.prefix, p_param_name]),
            ''.join([SvarogDocument.prefix, p_subparam_name]))

