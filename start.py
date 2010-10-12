#!/usr/bin/env python

import sys
import os
PATH = "/home/mrygacz/openbci/openbci/"

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		alias_id = "gui"
	#print sys.argv[1]
	else:
		alias_id = sys.argv[1]

	os.system("python " + PATH + "/k2launcher/captain.py --ac init_one_node; python " + PATH + "/k2launcher/captain.py --ac alias --alias_id " + alias_id)


