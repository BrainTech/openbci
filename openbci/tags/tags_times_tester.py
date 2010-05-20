from openbci.tags import tags_file_reader as reader

class Tester(object):
    def __init__(self, file_name, tag_type=""):
        self.reader = reader.TagsFileReader(file_name)
        self.reader.start_tags_reading()
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
        while True:
            tag = self.reader.get_next_tag()
            if not tag:
                break
            if self.type == "" or self.type == tag['name']:
                tags.append(tag)
        return tags
            
