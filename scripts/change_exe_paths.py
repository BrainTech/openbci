#!/usr/bin/python
# -*- coding: utf-8 -*-

import fnmatch
import os
import re

def find_files_ext(dir_name, ext_name):
    matches = []
    for root, dirnames, filenames in os.walk(dir_name):
        for filename in fnmatch.filter(filenames, '*.' + ext_name):
            matches.append(os.path.join(root, filename))
    return matches


def replace_str(match, new_str, filename):
    command = "sed -i 's/" + re.escape(match) + "/" + re.escape(new_str) + "/g' " + filename
    print "processing  ", command
    os.system(command)


REPLACE = {
   "drivers/eeg/cpp_amplifiers/tmsi_amplifier" : "/usr/bin/tmsi_amplifier",
   "drivers/eeg/cpp_amplifiers/file_amplifier" : "/usr/bin/file_amplifier",
   "drivers/eeg/cpp_amplifiers/dummy_amplifier" : "/usr/bin/dummy_amplifier",
   "multiplexer-install/bin" : "/usr/bin"
}

if __name__ == '__main__':
    mtch = find_files_ext(os.environ["OBCI_INSTALL_DIR"], "ini")
    for fname in mtch:
        for old, new in REPLACE.iteritems():
            replace_str(old, new, fname)

