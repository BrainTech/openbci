#MULTIPLEXER_ADDRESSES = [("217.115.150.135", 1234)]
MULTIPLEXER_ADDRESSES = [("127.0.0.1", 31889)]

MULTIPLEXER_PASSWORD = ""

import os.path, sys

"""MAIN DIR is a path to openbci main directory."""
MAIN_DIR = ''.join([os.path.split(
    os.path.realpath(os.path.dirname(__file__)))[0], '/'])

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
