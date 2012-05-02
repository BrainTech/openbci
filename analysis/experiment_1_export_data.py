
import smart_tags
from openbci.data_storage import csv_manager
import os.path
CSV_HEADER ="condition;amplitude"
def get_data_from_smart_tag(p_smart_tag):
    #first set condition
    l_string_data = [p_smart_tag.get_start_tag()['ugm_config']]
    #now set amplitude
    l_ch_data = p_smart_tag.get_samples()
    l_amp = 1.0 #compute amplitude from selected channels
    l_string_data.append(l_amp)
    return l_string_data
def run(p_files_name, p_files_path):
    
    l_tags_def = smart_tags.SmartTagDefinition(...)
    l_st_mgr = smart_tags.SmartTagsManager(l_tags_def)

    l_csv_writer = csv_manager.Writer(
        os.path.join(
            p_files_path, 
            p_files_name+".csv"))
    l_csv_writer.write_row(CSV_HEADER)
    for i_smart_tag in l_st_mgr.iter_smart_tags():
        l_data_list = get_data_from_smart_tag(i_smart_tag)
        l_csv_writer.write_row(l_data_list)
    l_csv_writer.close()

if __name__ = "__main__":
    run()
