# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> import os, os.path

>>> from obci.analysis.obci_signal_processing import smart_tags_manager as mgr

>>> from obci.analysis.obci_signal_processing.tags import smart_tag_definition as df    

>>> d = df.SmartTagDurationDefinition(start_tag_name='trigger', start_offset=0, end_offset=0, duration=1.0)

>>> pth = os.path.abspath(mgr.__file__)

>>> f = {'info':  os.path.join(pth[:-len(os.path.basename(pth))], 'tests', 'data', 'nic.obci.svarog.info'), 'data':'nic.obci.dat', 'tags': os.path.join(pth[:-len(os.path.basename(pth))], 'tests', 'data', 'nic.obci.svarog.tags')}

>>> fabricate_data_file(f['data'])

>>> m = mgr.SmartTagsManager(d, f['info'], f['data'], f['tags'])

>>> print(len(m._smart_tags))
51

>>> tags, num = iter_all_tags(m)

>>> print(num)
51

>>> print(repr(tags[0].get_start_timestamp()))
0.36085605621337891

>>> print(repr(tags[50].get_end_timestamp()))
79.996880054473877

>>> print(tags[2].get_channel_samples('Fp1')[0])
19389.0

>>> print(tags_len_ok(tags))
True

>>> dd = df.SmartTagEndTagDefinition(start_tag_name='trigger', start_offset=0, end_offset=0, end_tags_names=['trigger'])

>>> mm = mgr.SmartTagsManager(dd, f['info'], f['data'], f['tags'])

>>> tags, num = iter_all_tags(mm)

>>> print(num)
50

>>> print(not_duration_tags_data_len(tags))
20131

>>> print(not_duration_tags_data_sub(tags))
True

>>> # Another test

>>> from ..tags import tags_file_writer as p

>>> px = p.TagsFileWriter('./tescik.obci.tags')

>>> px.tag_received({'start_timestamp':1.0, 'end_timestamp':5.0, 'name': 'A', 'channels':'', 'desc': {'x':123, 'y':456, 'z': 789}})


>>> px.tag_received({'start_timestamp':6.0, 'end_timestamp':10.0, 'name': 'A', 'channels':'', 'desc': {'x':1234, 'y':4567, 'z': 789}})

>>> px.tag_received({'start_timestamp':6.1, 'end_timestamp':6.5, 'name': 'B', 'channels':'', 'desc': {'x':123, 'y':456, 'z': 789}})

>>> px.tag_received({'start_timestamp':7.0, 'end_timestamp':7.0, 'name': 'B', 'channels':'', 'desc': {'x':123, 'y':456, 'z': 789}})

>>> px.tag_received({'start_timestamp':7.5, 'end_timestamp':8.7, 'name': 'B', 'channels':'', 'desc': {'x':123, 'y':456, 'z': 789}})


>>> px.tag_received({'start_timestamp':9.0, 'end_timestamp':15.0, 'name': 'A', 'channels':'', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> px.tag_received({'start_timestamp':10.2, 'end_timestamp':11.0, 'name': 'B', 'channels':'', 'desc': {'x':123, 'y':456, 'z': 789}})

>>> px.tag_received({'start_timestamp':12.0, 'end_timestamp':12.5, 'name': 'B', 'channels':'', 'desc': {'x':123, 'y':456, 'z': 789}})


>>> px.tag_received({'start_timestamp':20.0, 'end_timestamp':25.0, 'name': 'A', 'channels':'', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> px.finish_saving(0.0)
'./tescik.obci.tags'

>>> fabricate_data_file('./tescik.obci.dat', 1)

>>> fabricate_info_file('./tescik.obci.info', 1)

>>> dd = df.SmartTagEndTagDefinition(start_tag_name='A', start_offset=0, end_offset=0, end_tags_names=['A'])

>>> mm = mgr.SmartTagsManager(dd, './tescik.obci.info', './tescik.obci.dat', './tescik.obci.tags')

>>> tags = [i for i in mm.iter_smart_tags()]

>>> len(tags)
3

>>> tags2 = [i for i in mm]

>>> len(tags2)
3

>>> tags == tags2
True

>>> print(tags[1].get_samples()[0][0])
768.0


>>> dd = df.SmartTagDurationDefinition(start_tag_name='B', start_offset=0, end_offset=0, duration=1.0)

>>> mm = mgr.SmartTagsManager(dd, None, None, None, tags[1])

>>> tss = [i for i in mm.iter_smart_tags()]

>>> len(tss)
3

>>> tss_tags = [t.get_start_tag() for t in tss]

>>> print(tss_tags)
[{'channels': '', 'start_timestamp': 6.0999999999999996, 'desc': {u'y': u'456', u'x': u'123', u'z': u'789'}, 'name': u'B', 'end_timestamp': 6.5}, {'channels': '', 'start_timestamp': 7.0, 'desc': {u'y': u'456', u'x': u'123', u'z': u'789'}, 'name': u'B', 'end_timestamp': 7.0}, {'channels': '', 'start_timestamp': 7.5, 'desc': {u'y': u'456', u'x': u'123', u'z': u'789'}, 'name': u'B', 'end_timestamp': 8.6999999999999993}]


>>> print(tss[0].get_samples()[0][0])
780.0


>>> dd = df.SmartTagDurationDefinition(start_tag_name='B', start_offset=0, end_offset=0, duration=1.0)

>>> mm = mgr.SmartTagsManager(dd, None, None, None, tags[2])

>>> tss = [i for i in mm.iter_smart_tags()]

>>> len(tss)
2

>>> tss_tags = [t.get_start_tag() for t in tss]

>>> print(tss_tags)
[{'channels': '', 'start_timestamp': 10.199999999999999, 'desc': {u'y': u'456', u'x': u'123', u'z': u'789'}, 'name': u'B', 'end_timestamp': 11.0}, {'channels': '', 'start_timestamp': 12.0, 'desc': {u'y': u'456', u'x': u'123', u'z': u'789'}, 'name': u'B', 'end_timestamp': 12.5}]



>>> import os

>>> os.system('rm tescik*')
0

>>> os.system('rm nic.obci*')
0

""" 
    
def iter_first_tag(m):
    for st in m.iter_smart_tags():
        print(len(st.get_samples()[0]))
        break

def iter_all_tags(m):
    count = 0
    sts = []
    for st in m.iter_smart_tags():
        count = count + 1
        sts.append(st)
    return sts, count

def tags_len_ok(tags):
    for tag in tags:
        for i in range(23):
            if len(tag.get_samples()[i]) != 256:
                return False
    return True

def not_duration_tags_data_len(tags):
    l = 0
    for tag in tags:
        l += len(tag.get_samples()[0])
    return l

def not_duration_tags_data_sub(tags):
    """True if data in tags are sequential - 
    they should be, as we have trigger-to-trigger tags
    and data in file are sequential."""
    d = tags[0].get_samples()[0][0]-1
    x = []
    ret = True
    for tag in tags:
        td_len = len(tag.get_samples()[0])
        for j in range(td_len):
            for i in range(23):
                td = tag.get_samples()[i]
                if td[j] != d+1:
                    print td[j]
                    ret = False
                d = td[j]
    return ret
    
def fabricate_data_file(f, ch=23):
    import struct
    freq, ch_count = (256, ch)
    data_file = open(f, 'wb')
    for i in range(100000*ch_count):
            data_file.write(struct.pack('d', i))
    data_file.close()


def fabricate_info_file(f, ch=23):
    from ..signal import info_file_proxy
    p = info_file_proxy.InfoFileWriteProxy(f)
    l_signal_params = {}
    l_freq = '128.0'
    l_ch_nums = [str(i) for i in range(ch)]
    l_ch_names = [str(i) for i in range(ch)]
    l_ch_gains = [str(i) for i in range(ch)]
    l_ch_offsets = [str(i) for i in range(ch)]

    l_signal_params['number_of_channels'] = len(l_ch_nums)
    l_signal_params['sampling_frequency'] = l_freq
    l_signal_params['channels_numbers'] = l_ch_nums
    l_signal_params['channels_names'] = l_ch_names
    l_signal_params['channels_gains'] = l_ch_gains
    l_signal_params['channels_offsets'] = l_ch_offsets
    l_signal_params['number_of_samples'] = 100
    l_signal_params['file'] = 'tescik.obci.dat'
    l_signal_params['first_sample_timestamp'] = 1.0
    p.finish_saving(l_signal_params)

def run():
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    print("All tests succeeded!")

if __name__=='__main__':
    run()
