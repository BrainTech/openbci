import csv
import codecs
class Writer(object):
    def __init__(self, p_file_path):
        self._file = codecs.open(p_file_path, "wb", "utf-8")
        self._writer = csv.writer(self._file, delimiter=';')
    def write_row(self, p_row):
        for i, i_elem in enumerate(p_row):
            #If i_elem is float replace . with , before writing it to csv
            try:
                i_elem + 1
                p_row[i] = repr(i_elem).replace('.',',')
            except TypeError: #i_elem is string
                pass
        self._writer.writerow(p_row)
    def close(self):
        self._file.close()
