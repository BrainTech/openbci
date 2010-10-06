from openbci.data_storage import csv_manager
from openbci import settings
import os.path
f = os.path.join(settings.module_abs_path(), "csv_test.csv")
mgr = csv_manager.Writer(f)

mgr.write_row([u'a',u'b',u'c'])
mgr.write_row(['', ''])
mgr.write_row([1,2.1, 3])
mgr.close()

print("See csv_test.csv file.")

mgr2 = csv_manager.Reader(f)
for i in mgr2:
    print(i)

mgr2.close()
