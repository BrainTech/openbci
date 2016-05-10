#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import sys
import os
import os.path
import importlib
import traceback


def lchop(astring, trailing):
    thelen = len(trailing)
    if astring[:thelen] == trailing:
        return astring[thelen:]
    return astring


def rchop(astring, trailing):
    thelen = len(trailing)
    if astring[-thelen:] == trailing:
        return astring[:-thelen]
    return astring


def sanitize_module_name(name):
    digits = '0123456789'
    allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_' + digits
    name = str(name)
    name_filtered = ''
    for ch in name:
        if ch in allowed_chars:
            name_filtered += ch
    name = name_filtered
    while len(name) > 0 and name[0] in digits:
        name = name[1:]
    return name


def sanitize_path(path):
    path = str(path).strip()
    path = os.path.expanduser(path)
    path = os.path.realpath(path)
    return path


def try_local_path_file():
    try:
        if sys.platform.startswith('win'):
            obci_dir_name = 'obci'
        else:
            obci_dir_name = '.obci'

        fname = os.path.join(os.path.expanduser('~'), '.obci', 'local_path')

        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                return f.read().strip()
        else:
            return None
    except Exception as ex:
        print(ex)
        return None


def try_env_variable():
    try:
        if 'OBCI_INSTALL_DIR' in os.environ:
            return os.environ['OBCI_INSTALL_DIR']
    except Exception as ex:
        print(ex)
        return None


if __name__ == '__main__':
    opt_name = '--obci-run-module='
    for v in sys.argv:
        if v.startswith(opt_name):
            bin_name = lchop(v, opt_name).strip()
            sys.argv.remove(v)
            break
    else:
        # this mode assumes this file is symlinked from a file with module name
        bin_name = os.path.basename(__file__)
        bin_name = rchop(bin_name, '.py')
        bin_name = rchop(bin_name, '.pyc')
        bin_name = rchop(bin_name, '.pyo')

    bin_name = sanitize_module_name(bin_name)

    try_list = [try_local_path_file, try_env_variable]

    for try_func in try_list:
        local_path = try_func()
        if local_path is None:
            continue
        local_path = sanitize_path(local_path)
        if local_path and os.path.isdir(local_path):
            sys.path.insert(1, os.path.realpath(local_path))
            break

    try:
        if bin_name == 'obci_run_proxy':
            try:
                peer_file_name = sys.argv[1]
            except IndexError:
                raise Exception("No Python script file specified.")

            sys.argv.remove(peer_file_name)
            sys.argv[0] = peer_file_name

            try:
                with open(peer_file_name) as f:
                    code = compile(f.read(), peer_file_name, 'exec')
            except IOError as ex:
                raise Exception("Error reading script file: {}".format(ex))

            exec(code)
            sys.exit(0)
        elif bin_name == 'obci':
            import obci.cmd.obci as module
        elif bin_name == 'obci_gui':
            import obci.cmd.obci_gui as module
        elif bin_name == 'obci_tray':
            import obci.cmd.obci_tray as module
        elif bin_name == 'obci_server':
            import obci.cmd.obci_server as module
        elif bin_name == 'obci_experiment':
            import obci.cmd.obci_experiment as module
        else:
            module_name = 'obci.cmd.{}'.format(bin_name)
            module = importlib.import_module(module_name)
        sys.exit(module.run())
    except Exception:
        print('--------------------------------------')
        print('--- OpenBCI Run Proxy Script Error ---')
        print('--------------------------------------')
        print('Script location: \'{}\''.format(os.path.abspath(__file__)))

        if bin_name == 'obci_run_proxy':
            print('Traceback while running: \'{}\''.format(peer_file_name))
        else:
            print('Couldn\'t import \'obci.cmd.{}\' module.'.format(bin_name))

        print('')
        traceback.print_exc()
        print('')
        print('Import path:')
        for i, p in enumerate(sys.path):
            print('{:2d}. {:s}'.format(i+1, p))
        print('---------------------------------------------')
        print('--- End of OpenBCI Run Proxy Script Error ---')
        print('---------------------------------------------')
        sys.exit(1)

