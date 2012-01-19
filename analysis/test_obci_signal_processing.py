from obci_signal_processing.tests import test_data_file_proxy, test_info_file_proxy, test_read_data_source, test_read_tags_source, test_smart_tag_definition, test_file_tags_writer_reader, test_read_manager, test_smart_tags_manager


if __name__ == "__main__":
    test_data_file_proxy.run()
    test_info_file_proxy.run()
    test_read_data_source.run()
    test_read_tags_source.run()
    test_smart_tag_definition.run()
    test_file_tags_writer_reader.run()
    test_read_manager.run()
    test_smart_tags_manager.run()
