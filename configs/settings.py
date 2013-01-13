import os

addrs = os.environ.get('MULTIPLEXER_ADDRESSES', '').split(',')
addr_tuples = []
if addrs:
    for addr in addrs:
        addr = addr.split(':')
        if len(addr) == 2:
            addr_tuples.append((addr[0], int(addr[1])))

MULTIPLEXER_ADDRESSES = addr_tuples if addr_tuples else [("0.0.0.0", 31889)]
MULTIPLEXER_PASSWORD = os.environ.get('MULTIPLEXER_PASSWORD', "")

import os.path, sys

"""MAIN DIR is a path to openbci main directory."""
MAIN_DIR = ''.join([os.path.split(
    os.path.realpath(os.path.dirname(__file__)))[0], '/'])


def current_appliance():
    """Return string defining current bci-ssvep appliance.
    Correct values: dummy, appliance1, appliance2
    app = 'dummy'"""
    try:
        app = x #read appliance name from global config
    except:
        app = 'dummy'

    return app
      
        

def module_abs_path():
    """This method returns absolute path to directory containing a module
    that imported and fired the method.
    Eg. having module /x/y/z/ugm/ugm.py with:
    ugm.py:
    import settings
    print(settings.module_abs_path())
    
    firing python z/ugm/ugm.py while being in y dir, will print out 
    /x/y/z/ugm/ path.
    """
    return ''.join([
            os.path.realpath(os.path.dirname(sys.argv[0])), 
                    os.path.sep
            ])
def executable_abs_path():
    """This method returns absolute path to directory containing a script
    that excecuted python interpreter.
    Eg. having module /x/y/z/ugm/ugm.py with:
    ugm.py:
    import settings
    print(settings.executable_abs_path())
    
    firing python z/ugm/ugm.py while being in y dir, will print out /x/y/ path.
    """
    return ''.join([os.getcwd(), os.path.sep])
