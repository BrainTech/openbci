#!/usr/bin/python

# MSG_TYPE RECEIVER SENDER [MESSAGE]

# SET_CONFIG amplifier1 launcher {json....}

# GET_CONFIG amplifier1 launcher

# SET_PARAMS amplifier launcher {param:value, param1.value1, ...}

# GET_PARAMS amplifier launcher [param1, param2]

# PARAM_VALUES launcher amplifier {param:value, ....}


# .. MSG_TYPE SENDER MSG

# CONFIG_UPDATE ALL amplifier sampling_rate old_val new_val


# MESSAGE_TYPE:RECEIVER:SENDER:MESSAGE


MSG_PARTS = 4
MSG_DELIMITERS_N = MSG_PARTS - 1
TYPE = 0
RECEIVER = 1
SENDER = 2
MESSAGE = 3

DM = ':'


class ConfigMessage(object):

	def __init__(self):
		self.type = ''
		self.receiver = ''
		self.sender = ''
		self.message = ''

	def __repr__(self):
		st = ' '.join(["type:", self.type, "receiver", self.receiver, "sender:", self.sender, "message", self.message])
		return st

	def unpack(self, p_msg):
		msg = p_msg.split(DM, MSG_DELIMITERS_N)
		if len(msg) != MSG_PARTS:
			raise ConfigMessageError

		self.type = msg[TYPE]
		self.receiver = msg[RECEIVER]
		self.sender = msg[SENDER]
		self.message = msg[MESSAGE]

	def pack(self):
		return DM.join([self.type, self.receiver, self.sender, self.message])


class ConfigMessageError(Exception):
	pass