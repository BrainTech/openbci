# -*- coding: utf-8 -*-
#!/usr/bin/env python
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

import generic_info_file_proxy
import signal_logging as logger
LOGGER = logger.get_logger("info_file_proxy")

class InfoDocument(generic_info_file_proxy.OpenBciDocument):
    """Subclass xml_document, so that we can add rs: prefix before every
    tag name."""
    prefix = 'rs:'
    def createElement(self, tagName):
        """Redefine the method so that every added tag has 'rs:' prefix."""
        return super(InfoDocument, self).createElement(
            ''.join([InfoDocument.prefix, tagName]))

class InfoFileWriteProxy(generic_info_file_proxy.GenericInfoFileWriteProxy):
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
        #'rs:amplifierNull',
        'rs:firstSampleTimestamp',
        ]
    def _create_xml_factory(self):
        """Redefine the method - return Svarog document."""
        return InfoDocument() 

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
        for order_key in InfoFileWriteProxy.ORDER:
            try:
                elem = self._xml_factory.getElementsByTagName(order_key)[0]
                elems.append(elem)
                l_xml_root.appendChild(elem)
            except IndexError:
                LOGGER.warning("Couldn`t find '"+str(order_key)+"' attribute. Created info file will not be totally correct!!!!")

        self._xml_factory = new_factory

class InfoFileReadProxy(generic_info_file_proxy.GenericInfoFileReadProxy):
    """Sublassed read proxy - every get_ method need to be subclassed 
    to add rs: prefix before tag name."""
    def _get_simple_param(self, p_param_name):
        """Return text value from tag in format:
        <param id=p_param_name>text_value</param>."""
        return super(InfoFileReadProxy, self)._get_simple_param(
            ''.join([InfoDocument.prefix, p_param_name]))

    def _get_list_param(self, p_param_name, p_subparam_name):
        """Return a list of text values form tag in format:
        <p_param_name>
            <param>text value1</param>
            <param>text value2</param>
            ...
        </p_param_name>
        """
        return super(InfoFileReadProxy, self)._get_list_param(
            ''.join([InfoDocument.prefix, p_param_name]),
            ''.join([InfoDocument.prefix, p_subparam_name]))

