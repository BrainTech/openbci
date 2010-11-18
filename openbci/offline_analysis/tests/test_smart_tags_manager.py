
"""
>>> from openbci.offline_analysis import smart_tags_manager as mgr

>>> from openbci.offline_analysis import smart_tag_definition as df    

>>> d = df.SmartTagDurationDefinition(start_tag_name='trigger', start_offset=0, end_offset=0, duration=1.0)

>>> f = {'info': 'openbci/offline_analysis/tests/nic.obci.svarog.info', 'data':'openbci/offline_analysis/tests/nic.obci.dat', 'tags':'openbci/offline_analysis/tests/nic.obci.svarog.tags'}

>>> fabricate_data_file(f['data'])

>>> m = mgr.SmartTagsManager(d, f)

>>> print(len(m._smart_tags))
51

>>> tags, num = iter_all_tags(m)

>>> print(num)
51

>>> print(repr(tags[0].get_start_timestamp()))
0.36085605621337891

>>> print(repr(tags[50].get_end_timestamp()))
79.996880054473877

>>> print(tags[2].get_data_for(0)[0])
19389.0

>>> print(tags_len_ok(tags))
True

>>> dd = df.SmartTagEndTagDefinition(start_tag_name='trigger', start_offset=0, end_offset=0, end_tags_names=['trigger'])

>>> mm = mgr.SmartTagsManager(dd, f)

>>> tags, num = iter_all_tags(mm)

>>> print(num)
50

>>> print(not_duration_tags_data_len(tags))
20131

>>> print(not_duration_tags_data_sub(tags))
True

""" 
    
def iter_first_tag(m):
    for st in m.iter_smart_tags():
        print(len(st.get_data()[0]))
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
            if len(tag.get_data_for(i)) != 256:
                return False
    return True

def not_duration_tags_data_len(tags):
    l = 0
    for tag in tags:
        l += len(tag.get_data_for(0))
    return l

def not_duration_tags_data_sub(tags):
    """True if data in tags are sequential - 
    they should be, as we have trigger-to-trigger tags
    and data in file are sequential."""
    d = tags[0].get_data_for(0)[0]-1
    x = []
    ret = True
    for tag in tags:
        td_len = len(tag.get_data_for(0))
        for j in range(td_len):
            for i in range(23):
                td = tag.get_data_for(i)
                if td[j] != d+1:
                    print td[j]
                    ret = False
                d = td[j]
    return ret
    
def fabricate_data_file(f):
    import struct
    freq, ch_count = (256, 23)
    data_file = open(f, 'wb')
    for i in range(100000*ch_count):
            data_file.write(struct.pack('d', i))
    data_file.close()


if __name__=='__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    print("All tests succeeded!")
