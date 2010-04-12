from openbci.data_storage import csv_manager

mgr = csv_manager.Writer("csv_test.csv")
mgr.write_row(['a','b','c'])
mgr.write_row(['1',2.1, 3])
mgr.close()

print("See csv_test.csv file.")
