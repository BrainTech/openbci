#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import csv
import codecs
import cStringIO
from openbci.core import types_utils
DELIMITER = ';'
STRING = '"'

class Writer(object):
    """Utf8 writer, code taken from:
    http://docs.python.org/library/csv.html
    """
    def __init__(self, p_file_path, d=DELIMITER, q=csv.QUOTE_NONNUMERIC):
        self._file = open(p_file_path, "wb")
        self._queue = cStringIO.StringIO()
        self._writer = csv.writer(self._queue,
                                  quoting=q,
                                  delimiter=d)

        self._encoder = codecs.getincrementalencoder("utf-8")()

    def write_row(self, p_row):
        row = []
        for s in p_row:
            try:
                # numeric?
                s + 1
                row.append(repr(s))
            except TypeError:
                # string?
                row.append(s)

        self._writer.writerow([s.encode("utf-8") for s in row])
        data = self._queue.getvalue()
        data = data.decode("utf-8")

        # ... and reencode it into the target encoding
        data = self._encoder.encode(data)
        # write to the target stream
        self._file.write(data)
        # empty queue
        self._queue.truncate(0)

    def close(self):
        self._file.close()

class Reader(object):
    """Utf8 Reader, code taken from:
    http://docs.python.org/library/csv.html
    """

    def __init__(self, p_file_path, d=DELIMITER, q=csv.QUOTE_NONNUMERIC):
        self._file = UTF8Recoder(p_file_path, 'utf-8')
        self._reader = csv.reader(self._file,
                                  delimiter=d,
                                  quoting=q)

    def __iter__(self):
        return self

    def next(self):
        row = self._reader.next()
        return [unicode(s, "utf-8") for s in row]

    def close(self):
        self._file.close()



class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8,
    code taken from:
    http://docs.python.org/library/csv.html
    """

    def __init__(self, f, encoding):
        self._file = open(f, "rb")
        self.reader = codecs.getreader(encoding)(self._file)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

    def close(self):
        self._file.close()

