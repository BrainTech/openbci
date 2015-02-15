#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import psutil

def which_binary(program):
    binary = which(program)
    if binary:
        return binary
    binary = os.path.split(program)[-1]
    if os.environ.get('OBCI_INSTALL_DIR'):
        mx = os.path.join(os.getenv('OBCI_INSTALL_DIR'), 'multiplexer-install', 'bin', 'mxcontrol')
        amplifiers = os.path.join(os.getenv('OBCI_INSTALL_DIR'), 'drivers', 'eeg', 'cpp_amplifiers')
        if binary == 'mxcontrol':
            if is_exe(mx):
                return mx
        elif binary == 'tmsi_amplifier' or binary == 'file_amplifier' or binary == 'dummy_amplifier' or binary == 'gtec_amplifier':
            path = os.path.join(amplifiers, binary)
            if is_exe(path):
                return path
    return which(binary)

def is_exe(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)


def which(program):
    
    def ext_candidates(fpath):
        yield fpath
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield fpath + ext

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            for candidate in ext_candidates(exe_file):
                if is_exe(candidate):
                    return candidate
    return False

def checkpidfile(file):   
    lockfile = getpidfile(file) 
    
    if os.access(os.path.expanduser(lockfile), os.F_OK):
        pidfile = open(os.path.expanduser(lockfile), "r")
        pidfile.seek(0)
        try:
            old_pd = int(pidfile.readline())
        except:#assumed error in pidfile
            pidfile.close()
            os.remove(os.path.expanduser(lockfile))
        else:
            if psutil.pid_exists(old_pd) == 1:
                print "You already have an instance of the program running"
                print "It is running as process %s," % str(old_pd)
                return True
            else:
                pidfile.close()
                os.remove(os.path.expanduser(lockfile))

    pidfile = open(os.path.expanduser(lockfile), "w")
    pidfile.write("%s" % os.getpid())
    pidfile.close()
    return False
    
def getpidfile(file):
    try:
        OBCI_HOME_DIR = os.path.join(os.getenv('HOME'), '.obci')
        lockfile = os.path.join(OBCI_HOME_DIR, file)
    except OSError:
        os.makedirs(OBCI_HOME_DIR)
    return lockfile

def removepidfile(file):
    lockfile = getpidfile(file)
    os.remove(os.path.expanduser(lockfile))
