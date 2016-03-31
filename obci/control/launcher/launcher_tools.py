#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import sys

NOT_READY = 'not_ready'
READY_TO_LAUNCH = 'ready_to_launch'
LAUNCHING = 'launching'
FAILED_LAUNCH = 'failed_launch'
RUNNING = 'running'
FINISHED = 'finished'
FAILED = 'failed'
TERMINATED = 'terminated'

EXP_STATUSES = [NOT_READY, READY_TO_LAUNCH, LAUNCHING,
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED]

POST_RUN_STATUSES = [FINISHED, FAILED, TERMINATED, FAILED_LAUNCH]
RUN_STATUSES = [LAUNCHING, RUNNING]


class ExperimentStatus(object):

    def __init__(self):
        self.status_name = NOT_READY
        self.details = {}
        self.peers_status = {}

    def set_status(self, status_name, details={}):
        self.status_name = status_name
        self.details = details

    def as_dict(self):
        d = dict(status_name=self.status_name,
                 details=self.details,
                 peers_status={})
        for peer_id, st in self.peers_status.iteritems():
            d['peers_status'][peer_id] = st.as_dict()
        return d

    def peer_status(self, peer_id):

        return self.peers_status.get(peer_id, None)

    def peer_status_exists(self, status_name):
        return status_name in [st.status_name for st in self.peers_status.values()]

    def del_peer_status(self, peer_id):
        del self.peers_status[peer_id]


class PeerStatus(object):

    def __init__(self, peer_id, status_name=NOT_READY):
        self.peer_id = peer_id
        self.status_name = status_name
        self.details = {}

    def set_status(self, status_name, details=()):
        self.status_name = status_name
        self.details = details

    def as_dict(self):
        return dict(peer_id=self.peer_id, status_name=self.status_name,
                    details=self.details)


def obci_root():
    path = os.path.realpath(os.path.dirname(__file__))
    path = os.path.split(path)[0]
    path = os.path.split(path)[0]
    return path


def obci_root_relative(path):
    _path = path
    if path:
        print("---- ", path)
        root = obci_root()
        if os.path.commonprefix([path, root]).startswith(root):
            _path = path[len(root):]
            if _path.startswith('/') or _path.startswith('\\'):
                _path = _path[1:]
    return _path


def obci_pythonpath():
    root = obci_root()
    lib_python_dir = ''.join(['python', str(sys.version_info[0]), '.',
                              str(sys.version_info[1])])
    try:
        import multiplexer.multiplexer_constants
        mx_python_path = ""
    except ImportError:
        mx_python_path = os.path.join(root, 'multiplexer-install', 'lib',
                                      lib_python_dir, 'site-packages')
    return mx_python_path  # os.pathsep.join([root, mx_python_path])


def update_obci_syspath(paths_str=None):
    paths_str = paths_str or obci_pythonpath()
    for direct in paths_str.split(os.pathsep):
        if direct != '':
            sys.path.insert(1, direct)


def update_pythonpath(obci_paths=None):
    obci_paths = obci_paths or obci_pythonpath()
    pythonpath = os.environ["PYTHONPATH"] if "PYTHONPATH" in os.environ else ''
    pythonpath = os.pathsep.join([pythonpath, obci_paths])
    os.environ["PYTHONPATH"] = pythonpath


def mx_path():
    return os.path.join(obci_root(), 'multiplexer-install', 'bin', 'mxcontrol')


def mx_rules_path():
    return os.path.join(obci_root(), 'configs', 'multiplexer.rules')


def module_path(module):
    path = module.__file__
    path = '.'.join([path.rsplit('.', 1)[0], 'py'])
    return os.path.normpath(path)


def default_config_path(peer_program_path):
    file_endings = ['py', 'java', 'jar', 'class', 'exe', 'sh', 'bin']
    base = peer_program_path
    sp = peer_program_path.rsplit('.', 1)
    if len(sp) > 1:
        if len(sp[1]) < 3 or sp[1] in file_endings:
            base = sp[0]
    conf_path = expand_path(base + '.ini')
    if os.path.exists(conf_path):
        return conf_path
    else:
        return ''


def expand_path(program_path, base_dir=None):
    if base_dir is None:
        base_dir = obci_root()
    if not program_path:
        return program_path
    program_path = os.path.normpath(program_path)
    p = os.path.expanduser(program_path)
    if os.path.isabs(p):
        return p
    else:
        return os.path.realpath(os.path.join(base_dir, p))

if __name__ == '__main__':
    print(obci_pythonpath())
