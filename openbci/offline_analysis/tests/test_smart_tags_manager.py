
"""
>>> from openbci.offline_analysis import smart_tags_manager as mgr

>>> from openbci.offline_analysis import smart_tag_definition as df        

>>> d = df.SmartTagDurationDefinition(start_tag_name='ugm_update', start_offset=0, end_offset=0, duration=5000)

>>> f = {'info': 'openbci/offline_analysis/tests/lukasz_experyment_1.obci.info', 'data':'openbci/offline_analysis/tests/lukasz_experyment_1.obci.dat', 'tags':'openbci/offline_analysis/tests/lukasz_experyment_1.obci.tags'}

>>> m = mgr.SmartTagsManager(d, f)

>>> print(len(m._smart_tags))
69

>>> iter_first_tag(m)
640

>>> iter_all_tags(m)
69


>>> dd = df.SmartTagEndTagDefinition(start_tag_name='ugm_update', start_offset=0, end_offset=0, end_tags_names=['ugm_update'])

>>> mm = mgr.SmartTagsManager(d, f)

>>> iter_all_tags(m)
69

"""
    
def iter_first_tag(m):
    for st in m.iter_smart_tags():
        print(len(st.get_data()[0]))
        break

def iter_all_tags(m):
    count = 0
    for st in m.iter_smart_tags():
        count = count + 1
    print(count)

if __name__=='__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    print("All tests succeeded!")
