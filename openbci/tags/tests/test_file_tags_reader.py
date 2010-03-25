from tags import tags_file_reader
if __name__ == "__main__":
    r = tags_file_reader.TagsFileReader('openbci/tags/tests/sample_tags.obci.tags')
    r.start_tags_reading()
    while True:
        l_tag = r.get_next_tag()
        if not l_tag:
            break
        print(l_tag)
        
    print("TEST SUCCEEDED!")
