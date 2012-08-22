#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import socket
import struct
import fcntl
import os
import ConfigParser
import threading
import logging
import time

from common.obci_control_settings import PORT_RANGE, INSTALL_DIR, OBCI_HOME_DIR, MAIN_CONFIG_NAME
from common.config_helpers import OBCISystemError



def is_net_addr(addr):
    return not addr.startswith('ipc') \
            and not addr.startswith('inproc')

def addr_is_local(addr):
    return addr.startswith('tcp://localhost') or\
                    addr.startswith('tcp://0.0.0.0') or\
                    addr.startswith('tcp://127.0.0.1')

def choose_local(addrs, ip=False):
    result = []
    if not ip:
        result = [a for a in addrs if a.startswith('ipc://')]
    if not result:
        result += [a for a in addrs if addr_is_local(a)]
    return result

def choose_not_local(addrs):
    result = [a for a in addrs if a.startswith('tcp://') and not a.startswith('tcp://'+lo_ip()) and not\
                            a.startswith('tcp://localhost')]
    #if not result:
    #    result += [a for a in addrs if a.startswith('tcp://')]
    return result

def choose_addr(addr_list):
    nl = choose_not_local(addr_list)
    if nl:
        return nl[0]
    else:
        loc = choose_local(addr_list)
        return loc[0] if loc else None


def lo_ip():
    return '127.0.0.1'

def ext_ip(peer_ip=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_ip = ''

    peer_ip = peer_ip if peer_ip else 'google.com'
    try:
        s.connect((peer_ip, 9))
        client_ip = s.getsockname()[0]
    except socket.error as e:
        print "ext_ip(peer_ip: {0}):  {1}".format(peer_ip, e)
        client_ip = lo_ip()

    del s
    return client_ip



def server_address(sock_type='rep', local=False, peer_ip=None):
    parser = __parser_main_config_file()

    if sock_type == 'rep':
        port = parser.get('server', 'port')
    else:
        port = parser.get('server', 'pub_port')


    ip = lo_ip() if local else ext_ip(peer_ip=peer_ip)
    return 'tcp://' + ip + ':' + port


def __parser_main_config_file():
    directory = os.path.abspath(OBCI_HOME_DIR)

    filename = MAIN_CONFIG_NAME
    fpath = os.path.join(directory, filename)

    parser = None
    if os.path.exists(fpath):
        parser = ConfigParser.RawConfigParser()
        with open(fpath) as f:
            parser.readfp(f)
    else:
        print "Main config file not found in {0}".format(directory)
        raise OBCISystemError()
    return parser

def port(addr_string):
    parts = addr_string.rsplit(':', 1)

    if len(parts) < 2:
        return None

    maybe_port = parts[-1]
    try:
        port = int(maybe_port)
    except ValueError, e:
        return None
    else:
        return port

def is_ip(addr_string):
    parts = addr_string.rsplit(':', 1)
    if len(parts) < 2:
        return False
    nums = parts[0].split('.')
    start = nums[0]
    ind = nums[0].find('://')
    if ind > -1:
        start = start[ind+3:]
        nums[0] = start
    if len(nums) < 4:
        return False
    for p in nums:
        try:
            n = int(p)
        except Exception, e:
            return False
    return True

def server_pub_port():
    parser = __parser_main_config_file()
    port = parser.get('server', 'pub_port')
    return port

def server_rep_port():
    parser = __parser_main_config_file()
    port = parser.get('server', 'port')
    return port

def server_bcast_port():
    parser = __parser_main_config_file()
    try:
        port = parser.get('server', 'bcast_port')
    except Exception, e:
        print "[ WARNING! WARNING! ] Config file is not up to date. Taking default bcast_port value!"
        port = '23123'
    return port

def server_tcp_proxy_port():
    parser = __parser_main_config_file()
    try:
        port = parser.get('server', 'tcp_proxy_port')
    except Exception, e:
        print "[ WARNING! WARNING! ] Config file is not up to date. Taking default tcp_proxy_port value!"
        port = '12012'
    return port

class DNS(object):
    def __init__(self, allowed_silence_time=45, logger=None):
        self.__lock = threading.RLock()
        self.__servers = {}
        self.logger = logger or logging.getLogger("dns")

        self.allowed_silence = allowed_silence_time


    def tcp_rep_addr(self, hostname=None, ip=None, uuid=None):
        srv = self._match_srv(hostname, ip, uuid)
        return 'tcp://' + srv.ip + ':' + str(srv.rep_port)

    def _match_srv(self, hostname=None, ip=None, uuid=None):
        matches = []
        if hostname is not None:
            matches = self.__query('hostname', hostname)
        elif ip is not None:
            matches = self.__query('ip')
        elif uuid is not None:
            with self.__lock:
                matches = [self.__servers[uuid]]
        if matches == []:
            raise Exception('Match not found')

        if len(matches) > 1:
            raise Exception('More than one match for given params:\
 hostname: {0}, ip: {1},  uuid: {2} --- {3}'.format(hostname, ip, uuid, matches))
        return matches.pop()

    def __query(self, attribute, value):
        matches = []
        with self.__lock:
            for srv in self.__servers.values():
                if getattr(srv, 'hostname') == value:
                    matches.append(srv)
        return matches


    def http_addr(self, hostname=None, ip=None, uuid=None):
        srv = self._match_srv(hostname, ip, uuid)
        return srv.ip + ':' + srv.http_port

    def hostname(self, ip=None, uuid=None):
        srv = self._match_srv(ip=ip, uuid=uuid)
        return srv.hostname

    def ip(self, hostname=None, uuid=None):
        srv = self._match_srv(hostname=hostname, uuid=uuid)
        return srv.ip

    def this_addr_local(self):
        return socket.gethostname()

    def this_addr_network(self):
        try:
            srv = self._match_srv(hostname=socket.gethostname())
        except:
            return socket.gethostname()
        else:
            return srv.ip

    def is_this_machine(self, address):
        addr = address
        if address.startswith('tcp://'):
            addr = addr[6:]
        parts = addr.split(':')
        if len(parts) > 0:
            addr = parts[0]
        return addr == self.this_addr_network() or addr == self.this_addr_local()

    def update(self, ip, hostname, uuid, rep_port, pub_port, http_port=None):
        with self.__lock:
            old = self.__servers.get(uuid, None)
            new = self.__servers[uuid] = PeerNetworkDescriptor(ip, hostname, uuid,
                                                            rep_port, pub_port,
                                                            http_port)
        changed = old is None
        if not changed:
            changed = old.ip != new.ip or old.hostname != new.hostname
        return changed

    def mass_update(self, server_dict):
        with self.__lock:
            self.__servers = {}
            for uid in server_dict:
                self.__servers[uid] = PeerNetworkDescriptor(**server_dict[uid])

    def clean_silent(self):
        changed = False
        with self.__lock:
            ids = self.__servers.keys()
            check_time = time.time()
            for uid in ids:
                srv = self.__servers[uid]
                if srv.timestamp + self.allowed_silence < check_time:
                    changed = True
                    self.logger.warning("obci_server on " + str(srv.ip) +'   ' +\
                             srv.hostname + " is most probably down.")
                    del self.__servers[uid]
        return changed

    def snapshot(self):
        snapshot = {}
        with self.__lock:
            for uid in self.__servers.keys():
                snapshot[uid] = self.__servers[uid]._copy()
        return snapshot

    def dict_snapshot(self):
        snapshot = {}
        with self.__lock:
            for uid in self.__servers.keys():
                snapshot[uid] = self.__servers[uid].as_dict()
        return snapshot

    def copy(self):
        new = DNS()
        new.allowed_silence = self.allowed_silence
        new.mass_update(self.dict_snapshot())
        return new



class PeerNetworkDescriptor(object):
    def __init__(self, ip, hostname, uuid, rep_port, pub_port, http_port=None, timestamp=None):
        self.ip = ip
        self.hostname = hostname
        self.uuid = uuid
        self.rep_port = rep_port
        self.pub_port = pub_port
        self.http_port = http_port
        self.timestamp = timestamp if timestamp is not None else time.time()

    def __str__(self):
        return str(self.as_dict())

    def _copy(self):
        desc =  PeerNetworkDescriptor(self.ip, self.hostname, self.uuid,
                                    self.rep_port, self.pub_port, self.http_port)
        desc.timestamp = self.timestamp
        return desc

    def as_dict(self):
        # dumb
        return dict(vars(self))



if __name__ == '__main__':
    #print ext_ip()
    print __file__
    print INSTALL_DIR