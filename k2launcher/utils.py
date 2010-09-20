import hashlib
import random
from google.protobuf.message import Message

def pb2_construct(what, **kwargs):
    w = what()
    for k in kwargs:
        v = kwargs[k]
        if type(v) == list:
            p = w.__getattribute__(k)
            for l in v:
                p.append(l)
        elif isinstance(v, Message):
            w.__getattribute__(k).CopyFrom(v)
        else:
            w.__setattr__(k, v)
    return w

def convert_host_port(s):
    s = s.strip(" ")
    host = s[:s.index(":")]
    port = int(s[s.index(":")+1:])
    return (host, port)

def convert_host_ports(s):
    return map(convert_host_port, s.split(","))

def random_string(length=8):
    return hashlib.sha1(str(random.random())).hexdigest()[:length]

def make_screen_name(screen_name):
    return screen_name + '_' + random_string(4)

def set_env(task, env):
    for k in env:
        kv = task.env.add()
        kv.key = k
        kv.value = env[k]
    return task

def get_env(task, env={}):
    for kv in task.env:
        env[kv.key] = kv.value
    return env
