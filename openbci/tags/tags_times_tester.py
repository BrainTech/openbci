from openbci.offline_analysis.obci_signal_processing.tags import tags_file_reader as reader

class Tester(object):
    def __init__(self, file_name, tag_type=""):
        self.reader = reader.TagsFileReader(file_name)
        self.type = tag_type
    def show_times_diffs(self):
        tags = self.get_tags()
        d = []
        for i, tag in enumerate(tags):
            try:
                d.append(tags[i+1]['start_timestamp'] - tag['start_timestamp'])
            except:
                break
        return d
            
    def get_tags(self):
        tags = []
        for tag in self.reader.get_tags():
            if self.type == "" or self.type == tag['name']:
                tags.append(tag)
        return tags

import sys            
if __name__ == "__main__":
    print(Tester(sys.argv[1], sys.argv[2]).show_times_diffs())
