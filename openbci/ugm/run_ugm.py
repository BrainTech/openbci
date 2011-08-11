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

"""Current script is supposed to be fired if you want to run 
ugm as a part of openbci (with multiplexer and all that stuff)."""
import socket, thread
import os, os.path, time, sys
import variables_pb2


from ugm import ugm_config_manager
from ugm import ugm_server

from tags import tagger
import ugm_logging as logger
import settings

LOGGER = logger.get_logger('run_ugm')
TAGGER = tagger.get_tagger()
import SocketServer
ugm_engine = None
ugm_engine_in_use = False
class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        global ugm_engine_in_use
        l_full_data = self.request[0].strip()
        l_msg = variables_pb2.UgmUpdate()
        try:
            l_msg.ParseFromString(l_full_data)
        except:
            LOGGER.info("PARSER ERROR")
            return
                #LOGGER.debug(''.join(['TcpServer got: ',
                #                      str(l_msg.type),
                #                      ' / ',
                #                      l_msg.value]))
                # Not working properly while multithreading ...
        l_time = time.time()
        if ugm_engine_in_use:
            LOGGER.info("ENGINE IN USE!!!!!!!!!!!!!!")
        else:
            ugm_engine_in_use = True
            ugm_engine.update_from_message(
                l_msg.type, l_msg.value)
            ugm_engine_in_use = False
        #TAGGER.send_tag(l_time, l_time, "ugm_update", 
        #                {"ugm_config":str(l_msg.value)})


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        l_full_data = self.request.recv(1024).strip()
        #print "%s wrote:" % self.client_address[0]
        #print self.data
        # just send back the same data, but upper-cased
        l_msg = variables_pb2.UgmUpdate()
        l_msg.ParseFromString(l_full_data)
                #LOGGER.debug(''.join(['TcpServer got: ',
                #                      str(l_msg.type),
                #                      ' / ',
                #                      l_msg.value]))
                # Not working properly while multithreading ...
        l_time = time.time()
        ugm_engine.update_from_message(
            l_msg.type, l_msg.value)
        TAGGER.send_tag(l_time, l_time, "ugm_update", 
                        {"ugm_config":str(l_msg.value)})

        #self.request.send(self.data.upper())


class TcpServer(object):
    """The class solves a problem with PyQt - it`s main window MUST be 
    created in the main thread. As a result I just can`t fire multiplexer
    and fire ugm_engine in a separate thread because it won`t work. I can`t
    fire ugm_engine and then fire multiplexer in a separate thread as 
    then multiplexer won`t work ... To solve this i fire ugm_engine in the 
    main thread, fire multiplexer in separate PROCESS and create TcpServer
    to convey data from multiplexer to ugm_engine."""
    def __init__(self, p_ugm_engine):
        """Init server and store ugm engine."""
        self._ugm_engine = p_ugm_engine
    def run(self):
        """Do forever:
        wait for data from ugm_server (it should be UgmUpdate() message
        type by now), parse data and send it to self._ugm_engine."""
        try:
            l_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Get config form ugm_server module
            l_soc.bind((ugm_server.TCP_IP, ugm_server.TCP_PORT))
            l_soc.listen(5)
        except Exception, l_exc:
            LOGGER.error('An error occured in TcpServer: '+str(l_exc))
            raise(l_exc)
        if 1 == 1:
            while True:
                # Wait for data from ugm_server
                l_conn = l_soc.accept()[0] # Don`t need address...
                l_full_data = ''
                while True:
                    l_data = l_conn.recv(ugm_server.BUFFER_SIZE)
                    if not l_data: 
                        break
                    l_full_data = ''.join([l_full_data, l_data])
                # d should represent UgmUpdate type...
                l_msg = variables_pb2.UgmUpdate()
                l_msg.ParseFromString(l_full_data)
                #LOGGER.debug(''.join(['TcpServer got: ',
                #                      str(l_msg.type),
                #                      ' / ',
                #                      l_msg.value]))
                # Not working properly while multithreading ...
                l_time = time.time()
                self._ugm_engine.update_from_message(
                    l_msg.type, l_msg.value)
                TAGGER.send_tag(l_time, l_time, "ugm_update", 
                                {"ugm_config":str(l_msg.value)})
                l_conn.close()
            l_soc.close()




class UdpServer(object):
    """The class solves a problem with PyQt - it`s main window MUST be 
    created in the main thread. As a result I just can`t fire multiplexer
    and fire ugm_engine in a separate thread because it won`t work. I can`t
    fire ugm_engine and then fire multiplexer in a separate thread as 
    then multiplexer won`t work ... To solve this i fire ugm_engine in the 
    main thread, fire multiplexer in separate PROCESS and create TcpServer
    to convey data from multiplexer to ugm_engine."""
    def __init__(self, p_ugm_engine):
        """Init server and store ugm engine."""
        self._ugm_engine = p_ugm_engine
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind((ugm_server.TCP_IP, ugm_server.TCP_PORT))

    def run(self):
        """Do forever:
        wait for data from ugm_server (it should be UgmUpdate() message
        type by now), parse data and send it to self._ugm_engine."""
        if 1 == 1:
            while True:
                # Wait for data from ugm_server
                l_full_data = self.socket.recvfrom(1024)[0].strip()

                # d should represent UgmUpdate type...
                l_msg = variables_pb2.UgmUpdate()
                try:
                    l_msg.ParseFromString(l_full_data)
                except:
                    LOGGER.info("PARSER ERROR")
                    continue
                #LOGGER.debug(''.join(['TcpServer got: ',
                #                      str(l_msg.type),
                #                      ' / ',
                #                      l_msg.value]))
                # Not working properly while multithreading ...
                l_time = time.time()
                self._ugm_engine.update_from_message(
                    l_msg.type, l_msg.value)
                #TAGGER.send_tag(l_time, l_time, "ugm_update", 
                #                {"ugm_config":str(l_msg.value)})
            self.socket.close()




if __name__ == "__main__":
    # Create instance of ugm_engine with config manager (created from
    # default config file
    try:
        l_eng_type = sys.argv[1]
    except IndexError:
        l_eng_type = 'simple'
    if l_eng_type == 'p300_train':
        from ugm import p300_train_ugm_engine
        ENG = p300_train_ugm_engine.P300TrainUgmEngine()        
    elif l_eng_type == 'p300_test':
        from ugm import p300_test_ugm_engine
        ENG = p300_test_ugm_engine.P300TestUgmEngine()        
    else:
        from ugm import ugm_engine
        ENG = ugm_engine.UgmEngine(ugm_config_manager.UgmConfigManager('feedback_speller_config3'))
    # Start TcpServer in a separate thread with ugm engine on slot
    #thread.start_new_thread(TcpServer(ENG).run, ())
        thread.start_new_thread(UdpServer(ENG).run, ())
    ugm_engine = ENG
    #server = SocketServer.TCPServer((ugm_server.TCP_IP, ugm_server.TCP_PORT), MyTCPHandler)
    #server = SocketServer.UDPServer((ugm_server.TCP_IP, ugm_server.TCP_PORT), MyUDPHandler)
    #thread.start_new_thread(server.serve_forever, ())

    # Start multiplexer in a separate process
    path = os.path.join(settings.module_abs_path(), "ugm_server.py")
    os.system("python " + path + " &")
    #TODO - works only when running from openbci directiory...
    # fire ugm engine in MAIN thread (current thread)
    ENG.run()


