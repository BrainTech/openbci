#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2



class TasksRandomizer(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(TasksRandomizer, self).__init__(addresses=addresses,
                                                type=peers.CLIENT)
        self.actions_list = self.config.get_param('actions_list').split(';')
        self.tasks_to_random = self.config.get_param('tasks_to_random').split(';')

        if len(self.tasks_to_random)>=2:
            self._update_action_list()
        self.ready()
            
    def _update_action_list(self):
        tasks_indexes = [ind for ind, value in enumerate(self.actions_list) if value in self.tasks_to_random]
        random.shuffle(self.tasks_to_random)
        for ind, task in zip(tasks_indexes, self.tasks_to_random):
            self.actions_list[ind] = task
        self.config.set_param('actions_list', ';'.join(self.actions_list))
    
if __name__ == "__main__":
    TasksRandomizer(settings.MULTIPLEXER_ADDRESSES).loop()