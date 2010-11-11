
"""
>>> from openbci.offline_analysis import smart_tags_manager as mgr

>>> from openbci.offline_analysis import smart_tag_definition as df    

>>> d = df.SmartTagDurationDefinition(start_tag_name='ugm_update', start_offset=0, end_offset=0, duration=5.0)

>>> f = {'info': 'openbci/offline_analysis/tests/MATI_FULL_EXP_28_10_2010_2.obci.info', 'data':'openbci/offline_analysis/tests/MATI_FULL_EXP_28_10_2010_2.obci.dat', 'tags':'openbci/offline_analysis/tests/MATI_FULL_EXP_28_10_2010_2.obci.tags'}

>>> fabricate_data_file(f['data'])

>>> m = mgr.SmartTagsManager(d, f)

>>> print(len(m._smart_tags))
337

>>> tags, num = iter_all_tags(m)

>>> print(num)
337

>>> print(repr(tags[0].get_start_timestamp()))
1275066798.1484799

>>> print(repr(tags[336].get_end_timestamp()))
1275067017.938139

>>> print(repr(tags[2].get_start_timestamp()))
1275066802.4346509

>>> print(tags[2].get_data_for(0)[0])
372117.0

>>> print(tags[2].get_data_for(2)[0])
372119.0

>>> print(len(tags[38].get_data_for(0)))
1280

>>> print(len(tags[66].get_data_for(10)))
1280

>>> print(len(tags[222].get_data_for(12)))
1280

>>> print(len(tags[311].get_data_for(20)))
1280

>>> print(len(tags[300].get_data_for(1)))
1280

>>> print(tags[335].get_data_for(15)[2])
1602793.0

>>> dd = df.SmartTagEndTagDefinition(start_tag_name='ugm_update', start_offset=0, end_offset=0, end_tags_names=['ugm_update'])

>>> mm = mgr.SmartTagsManager(dd, f)

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
