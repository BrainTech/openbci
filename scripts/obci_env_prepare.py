	#!/usr/bin/env python

import os, sys
import shutil
import argparse
import ConfigParser
import subprocess
from pwd import getpwnam  



def make_obci_config_dir(config_path):
	if not os.path.exists(config_path):
		os.mkdir(config_path)
		os.mkdir(os.path.join(config_path, 'scenarios'))
		os.mkdir(os.path.join(config_path, 'sandbox'))

def get_args():
	parser = argparse.ArgumentParser(description="Prepare obci configuration and environment")
	parser.add_argument("obci_dir", help="OBCI install directory")
	parser.add_argument("admin_account_name", help="Source of configuration")
	return parser.parse_args()

if __name__ == '__main__':
	print("Run for instance: python obci_env_prepare.py /home/mati/obci mati")
	args = get_args()
	base = '/home'
	main_account = args.admin_account_name#'administrator' #
	print 'main_account:', main_account 
	
	obci_dir = args.obci_dir#'/home/administrator/obci' #
	print 'obci_dir:', obci_dir

	admin_main = os.path.join(base, main_account, '.obci', 'main_config.ini')
	print 'main config:', admin_main

	for direc in os.listdir(base):
		config_path = os.path.join(base, direc, '.obci')
		print 'config_dir: ', config_path
		make_obci_config_dir(config_path)
	
	config_template = os.path.join(obci_dir, 'control', 'templates', 'main_config.ini')
	print 'config_template', config_template
	shutil.copyfile(config_template, admin_main)
	config = ConfigParser.RawConfigParser()
	config.read(admin_main)
	config.set('server', 'ifname', 'lo')
	with open(admin_main, 'wb') as configfile:
    		config.write(configfile)

	for direc in os.listdir(base):
		dir_path = os.path.join(base, direc, '.obci')
		config_path = os.path.join(dir_path, 'main_config.ini')
		
		if direc != admin_main and not os.path.exists(config_path):
			os.symlink(admin_main, config_path)
		os.system("chown -R " + direc + " " + dir_path)
		os.system("ls -l " + dir_path)
		for (dr, dirs, files) in os.walk(dir_path):
			for fil in files:

				os.system("ls -l " + os.path.join(dr, fil))
		
		bashrc = os.path.join(base, direc, '.bashrc')
		if not "LD_LIBRARY_PATH" in  subprocess.Popen(['cat', bashrc], stdout=subprocess.PIPE).communicate()[0]:
			print "adding LD_LIBRARY_PATH to ", bashrc
			os.system("echo 'export LD_LIBRARY_PATH=" + '"/usr/local/lib"' + "'" + " >> " + bashrc )
			os.system("cat " + bashrc)

	with open('/etc/environment', 'r') as env:
		lines = env.readlines()
		isset = [line for line in lines if line.startswith('OBCI_INSTALL_DIR') or\
						line.startswith('LD_LIBRARY_PATH')]
	print 'env:', isset
	if len(isset) < 2:
		print "updating /etc/environment"
		with open('/etc/environment', 'a') as env:
			env.write('LD_LIBRARY_PATH="/usr/local/lib"\n')
			env.write('OBCI_INSTALL_DIR="' + obci_dir + '"\n')

	if not os.path.exists('/usr/bin/obci'):
		print "linking obci command"
		os.symlink(os.path.join(obci_dir, 'control', 'launcher', 'obci'),
				'/usr/bin/obci')
	if not os.path.exists('/usr/bin/obci_gui'):
		print "linking obci_gum command"
		os.symlink(os.path.join(obci_dir, 'control', 'gui', 'obci_gui'),
				'/usr/bin/obci_gui')
	if not os.path.exists('/usr/bin/obci_x_tray'):
		print "linking obci_x_tray command"
		os.symlink(os.path.join(obci_dir, 'control', 'gui', 'obci_x_tray'),
				'/usr/bin/obci_x_tray')


		
