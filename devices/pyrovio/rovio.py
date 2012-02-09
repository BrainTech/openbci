"""
A Python implementation of the Wowwee Rovio web-based API.

The Rovio mobile webcam is controlled through a web-based API.  The Rovio class
wraps http calls to a Rovio and returns the appropriate responses.  It also
provides some additional support methods for parsing the responses.

Classes:
  - Rovio: Access to an instance of a Rovio mobile webcam

Exceptions:
  - RovioError: base class for Rovio-related exceptions

Handlers:
  - NullHandler: do-nothing handler for logging

Module Attributes:
  - rovios: a map of Rovio names to Rovio objects
  - rlog: logging.Logger object for logging

Module Functions:
  - getRovio: return the rovio object with the given name

Module Constants:
  - __version__: The version of the PyRovio interface module as a string
  - API_VERSION: The version of the Rovio API as a string
  - API_DATE: Release date of the Rovio API
  - INFO: PyRovio version and API info as a string
  - AUTHORS: List of dicts of author names and emails
  - COPYRIGHT
  - LICENSE
  - USER_AGENT: For use with HTTP requests
  - response_codes: map of response codes to [name, docstring]
    
    Response Code Commands Table

    These are returned by many Rovio commands.

    #  Constant name                    Description
    ---------------------------------------------------------------------------
    0  SUCCESS                          CGI command successful
    1  FAILURE                          CGI command general failure
    2  ROBOT_BUSY                       robot is executing autonomous function
    3  FEATURE_NOT_IMPLEMENTED          CGI command not implemented
    4  UNKNOWN_CGI_ACTION               CGI nav command: unknown action
                                        requested
    5  NO_NS_SIGNAL                     no navigation signal available
    6  NO_EMPTY_PATH_AVAILABLE          path memory is full
    7  FAILED_TO_READ_PATH              failed to read Flash memory
    8  PATH_BASEADDRESS_NOT_INITIALIZED Flash error
    9  PATH_NOT_FOUND                   no path with such name
    10 PATH_NAME_NOT_SPECIFIED          path name parameter is missing
    11 NOT_RECORDING_PATH               save path command received while not in
                                        recording mode
    12 FLASH_NOT_INITIALIZED            Flash subsystem failure
    13 FAILED_TO_DELETE_PATH            Flash operation failed
    14 FAILED_TO_READ_FROM_FLASH        Flash operation failed
    15 FAILED_TO_WRITE_TO_FLASH         Flash operation failed
    16 FLASH_NOT_READY                  Flash failed
    17 NO_MEMORY_AVAILABLE              N/A
    18 NO_MCU_PORT_AVAILABLE            N/A
    19 NO_NS_PORT_AVAILABLE             N/A
    20 NS_UART_READ_ERROR               N/A
    21 PARAMETER_OUTOFRANGE             one or more CGI parameters are out of
                                        expected range
    22 NO_PARAMETER                     one or more CGI parameters are missing

Authors:
  - Jon Bona (University at Buffalo) (mailto:jpbona@buffalo.edu)
  - Mike Prentice (University at Buffalo) (mailto:mjp44@buffalo.edu)

PyRovio is developed at the University at Buffalo and distributed under the UB
Public License (UBPL) version 1.0 (see license.txt).

"""

import base64
import urllib2
import logging
import threading
import time

###############
# MODULE INFO #
###############

# Some third-party software expects __version__
__version__ = '0.1'
API_VERSION = '1.2'
API_DATE = 'October 8, 2008'
INFO = 'PyRovio v%s ; Rovio API v%s released %s' % (__version__, API_VERSION,
                                                    API_DATE)
AUTHORS = [{'name' : 'Mike Prentice', 'email' : 'mjp44@buffalo.edu'},
           {'name' : 'Jon Bona', 'email' : 'jpbona@buffalo.edu'}]
COPYRIGHT = 'Copyright (C) 2009 Jon Bona and Mike Prentice'
LICENSE = 'UBPL v1.0'

####################
# MODULE CONSTANTS #
####################

USER_AGENT = 'PyRovio/%s' % __version__

# Response Code Commands
SUCCESS                          = 0
FAILURE                          = 1
ROBOT_BUSY                       = 2
"""robot is executing autonomous function"""
FEATURE_NOT_IMPLEMENTED          = 3
UNKNOWN_CGI_ACTION               = 4
NO_NS_SIGNAL                     = 5
"""no navigation signal available"""
NO_EMPTY_PATH_AVAILABLE          = 6
"""path memory is full"""
FAILED_TO_READ_PATH              = 7
"""failed to read FLASH memory"""
PATH_BASEADDRESS_NOT_INITIALIZED = 8
"""FLASH error"""
PATH_NOT_FOUND                   = 9
"""no path with such name"""
PATH_NAME_NOT_SPECIFIED          = 10
"""path name parameter is missing"""
NOT_RECORDING_PATH               = 11
"""save path command received while not in recording mode"""
FLASH_NOT_INITIALIZED            = 12
"""FLASH subsystem failure"""
FAILED_TO_DELETE_PATH            = 13
"""FLASH operation failed"""
FAILED_TO_READ_FROM_FLASH        = 14
"""FLASH operation failed"""
FAILED_TO_WRITE_TO_FLASH         = 15
"""FLASH operation failed"""
FLASH_NOT_READY                  = 16
"""FLASH failed"""
NO_MEMORY_AVAILABLE              = 17
NO_MCU_PORT_AVAILABLE            = 18
NO_NS_PORT_AVAILABLE             = 19
NS_UART_READ_ERROR               = 21
PARAMETER_OUTOFRANGE             = 22
"""one or more CGI parameters are out of expected range"""
NO_PARAMETER                     = 23
"""one or more CGI parameters are missing"""

response_codes = {
    SUCCESS : ['SUCCESS', 'CGI command successful'],
    FAILURE : ['FAILURE', 'CGI command general failure'],
    ROBOT_BUSY : ['ROBOT_BUSY', 'robot is executing autonomous function'],
    FEATURE_NOT_IMPLEMENTED : ['FEATURE_NOT_IMPLEMENTED',
                               'CGI command not implemented'],
    UNKNOWN_CGI_ACTION : ['UNKNOWN_CGI_ACTION',
                          'CGI nav command: unknown action requested'],
    NO_NS_SIGNAL : ['NO_NS_SIGNAL', 'no navigation signal available'],
    NO_EMPTY_PATH_AVAILABLE : ['NO_EMPTY_PATH_AVAILABLE',
                               'path memory is full'],
    FAILED_TO_READ_PATH : ['FAILED_TO_READ_PATH',
                           'failed to read Flash memory'],
    PATH_BASEADDRESS_NOT_INITIALIZED : ['PATH_BASEADDRESS_NOT_INITIALIZED',
                                        'Flash error'],
    PATH_NOT_FOUND : ['PATH_NOT_FOUND', 'no path with such name'],
    PATH_NAME_NOT_SPECIFIED : ['PATH_NAME_NOT_SPECIFIED',
                               'path name parameter is missing'],
    NOT_RECORDING_PATH : ['NOT_RECORDING_PATH',
                          'save path command received while not in recording '
                          'mode'],
    FLASH_NOT_INITIALIZED : ['FLASH_NOT_INITIALIZED',
                             'Flash subsystem failure'],
    FAILED_TO_DELETE_PATH : ['FAILED_TO_DELETE_PATH',
                             'Flash operation failed'],
    FAILED_TO_READ_FROM_FLASH : ['FAILED_TO_READ_FROM_FLASH',
                                 'Flash operation failed'],
    FAILED_TO_WRITE_TO_FLASH : ['FAILED_TO_WRITE_TO_FLASH',
                                'Flash operation failed'],
    FLASH_NOT_READY : ['FLASH_NOT_READY', 'Flash failed'],
    NO_MEMORY_AVAILABLE : ['NO_MEMORY_AVAILABLE', 'N/A'],
    NO_MCU_PORT_AVAILABLE : ['NO_MCU_PORT_AVAILABLE', 'N/A'],
    NO_NS_PORT_AVAILABLE : ['NO_NS_PORT_AVAILABLE', 'N/A'],
    NS_UART_READ_ERROR : ['NS_UART_READ_ERROR', 'N/A'],
    PARAMETER_OUTOFRANGE : ['PARAMETER_OUTOFRANGE',
                            'one or more CGI parameters are out of expected '
                            'range'],
    NO_PARAMETER : ['NO_PARAMETER', 'one or more CGI parameters are missing'],
    }

#####################
# MODULE ATTRIBUTES #
#####################

rovios = dict()
"""Map of Rovio names to interface objects"""
rlog = logging.getLogger('rovio')

####################
# MODULE FUNCTIONS #
####################

def getRovio(name):
    """Return the Rovio object named by name."""
    return rovios[name]

###########
# CLASSES #
###########

class NullHandler(logging.Handler):
    """Do-nothing handler for logging."""
    def emit(self, record):
        pass
# add null handler to avoid error messages
rlog.addHandler(NullHandler())

class RovioError(Exception):
    """Base class for errors in the Rovio package."""

class ConnectError(RovioError):
    """
    Exception raised for error connecting to the Rovio.

    Attributes:
      - rovio:   Rovio object
      - message: explanation of the error

    """

    def __init__(self, rovio):
        self.rovio = rovio
        self.message = ('Error connecting to %s (host: %s)' %
                        (self.rovio.name, self.rovio.host))

class ResponseError(RovioError):
    """
    Exception raised for a command response code error.

    Attributes:
      - rovio: Rovio object
      - code: command response code
      - message: explanation of the error

    """

    def __init__(self, rovio, code):
        self.rovio = rovio
        self.code = code
        self.message = ('Response error from %s: %d (%s)' %
                        (self.rovio.name,
                         response_codes[self.code][0],
                         response_codes[self.code][1]))

class ParamError(RovioError):
    """
    Exception raised when trying to set a parameter to an invalid value.

    Attributes:
      - rovio:   rovio object
      - param:   parameter name
      - message: explanation of the error

    """

    def __init__(self, rovio, param, value, message=None):
        self.rovio = rovio
        self.param = param
        self.message = ('Parameter error from %s: Attempting to set param %s '
                        'to %s (Details: %s)') % (self.rovio.name,
                                                  self.param,
                                                  self.message)

class OutOfRangeError(ParamError):
    """
    Exception raised when trying to set a parameter out of range.

    Attributes:
      - rovio:  Rovio object
      - param:  parameter name
      - range_: [low, high]
      - value:  attempted input value
      
    """

    def __init__(self, rovio, param, range_, value):
        super(OutOfRangeError, self).__init__(rovio, param, value,
                                              'valid range is %s' % range)
        self.range = range_
        self.value = value

class Rovio:
    
    """
    An instance of the Rovio class provides an interface to one Rovio.

    The Rovio API consists of function calls made over HTTP.  This class wraps
    the HTTP requests with Python method calls.  The Rovio API is mirrored as
    faithfully as possible; however, some convenience functions have been used.
    For example, the movement commands are implemented as separate methods
    rather than parameters to the ManualDrive method in the Rovio API.

    You can set the hostname of the Rovio to connect to using the host
    property.  You can also set the IP address or host of the Rovio webcam
    itself using the Rovio API using SetHTTP.  After using SetHTTP, you are
    required to then set the host property to the same address in order to
    continue controlling the same Rovio object.  (Note: This was an arbitrary
    design decision in making the Rovio class.)  TODO: example

    WARNING: There is not much parameter checking.  The only indicator that
    things aren't working may be that the object is not able to connect to the
    Rovio's webserver, so set parameters carefully.

    Properties:
      - host:     hostname or IP address of the Rovio
      - name:     name of this Rovio (read-only)
      - port:     HTTP port number (default 80)
      - protocol: Protocol to use (read-only, default http)
      - speed:    Default Rovio speed (1 fastest, 10 slowest, default 1)
      - username: HTTP Auth name (default None)
      - password: HTTP Auth password (default None)

    Commands:
      - abort_recording
      - change_brightness
      - change_compress_ratio
      - change_framerate
      - change_mic_volume
      - change_resolution
      - change_speaker_volume
      - clear_all_paths
      - delete_path
      - email_image
      - get_data
      - get_host
      - get_image
      - get_libNS_version
      - get_MCU_report
      - get_path_list
      - get_report:           return a status report on the Rovio
      - get_status
      - get_tuning_parameters
      - go_home
      - go_home_and_dock
      - manual_drive:         master command for wheel and camera movement
      - pause_playing
      - play_path_backward
      - play_path_forward
      - read_all_parameters
      - read_parameter
      - rename_path
      - reset_home_location
      - reset_nav_state_machine
      - save_parameter
      - set_camera
      - set_tuning_parameters
      - start_recording
      - stop_playing
      - stop_recording
      - stream_video
      - update_home_position

    Movement commands:
    
    All movement commands return a response code (SUCCESS for success, see
    Response Code Commands Table).  Non-camera movement commands have an
    optional speed parameter that defaults to the default speed of this Rovio
    object.
    
      - stop
      - forward
      - backward
      - left (straight left)
      - right (straight right)
      - rotate_left (by speed and angle)
      - rotate_right (by speed and angle)
      - forward_left
      - forward_right
      - back_left
      - back_right
      - head_up (camera)
      - head_down (camera)
      - head_middle (camera)

    Documentation taken from the API Specification for Rovio, version 1.2,
    October 8, 2008, from WowWee Group Limited.
    
    """
    
    # Class constants

    # Data attributes (instance attributes)
    
    def get_protocol(self): return self._protocol
    protocol = property(get_protocol, doc="""Protocol to use (default http)""")
    
    def get_port(self): return self._port
    def set_port(self, value):
        if 0 <= value <= 65535:
            self._port = value
            self._compile_URLs()
        else:
            raise OutOfRangeError(self, 'port', [0, 65535], value)
    port = property(get_port, set_port,
                    doc="""Rovio port (default 80)""")

    def get_speed(self): return self._speed
    def set_speed(self, value):
        if 1 <= value <= 10:
            self._speed = value
        else:
            raise OutOfRangeError(self, 'speed', [1, 10], value)
    speed = property(get_speed, set_speed,
                     doc="""
                     Rovio's default movement speed.

                     1 fastest, 10 slowest (default 1)
                     
                     """)

    def get_username(self): return self._username
    def set_username(self, value):
        if (isinstance(value, str) or value is None):
            self._username = value
            self._compile_URLs()
        else:
            raise ParamError(self, 'username', value,
                             'must be a string or None')
    username = property(get_username, set_username,
                        doc="""HTTP Auth username or None""")

    def get_password(self): return self._password
    def set_password(self, value):
        if (isinstance(value, str) or value is None):
            self._password = value
            self._compile_URLs()
        else:
            raise ParamError(self, 'password', value,
                             'must be a string or None')
    password = property(get_password, set_password,
                        doc="""HTTP Auth password or None""")
    
    def get_name(self): return self._name
    name = property(get_name, doc="""Name of the Rovio the object represents""")

    def get_host(self): return self._host
    def set_host(self, value):
        if (isinstance(value, str)):
            self._host = value
            self._compile_URLs()
        else:
            raise ParamError(self, 'host', value, 'must be a valid URL string')
    host = property(get_host, set_host,
                    doc="""Hostname or IP address of the Rovio""")
    
    def __init__(self, name, host, username=None, password=None, port=80):
        """
        Initialize a new Rovio interface.

        Parameters:
          - name:     name of this Rovio mobile webcam
          - host:     hostname or IP address
          - username: HTTP Auth name (default None)
          - password: HTTP Auth password (default None)
          - port:     HTTP port (default 80)

        """
        self._name = name
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._protocol = 'http'
        self._speed = 1
        self._compile_URLs()
        rovios[self.name] = self

    def stop(self):
        """Currently does nothing."""
        return self.manual_drive(0)

    def forward(self, speed=None):
        """Move Rovio forward."""
        return self.manual_drive(1, speed)

    def backward(self, speed=None):
        """Move Rovio backward."""
        return self.manual_drive(2, speed)

    def left(self, speed=None):
        """Move Rovio straight left."""
        return self.manual_drive(3, speed)

    def right(self, speed=None):
        """Move Rovio straight right."""
        return self.manual_drive(4, speed)

    def rotate_left(self, speed=None, angle=None):
        """
        Rotate Rovio left by speed.

        The optional angle parameter turns the Rovio a certain distance.
        Approximately: 3 is 45 degrees, 7 is 90 degrees, 11 is 135 degrees, and
        15 is 180 degrees.

        Parameters:
          - speed
          - angle (optional)

        """
        if angle is None:
            return self.manual_drive(5, speed)
        else:
            return self.manual_drive(17, speed, angle)

    def rotate_right(self, speed=None, angle=None):
        """
        Rotate Rovio right by speed.

        The optional angle parameter turns the Rovio a certain distance.
        Approximately: 3 is 45 degrees, 7 is 90 degrees, 11 is 135 degrees, and
        15 is 180 degrees.

        Parameters:
          - speed
          - angle (optional)

        """
        if angle is None:
            return self.manual_drive(6, speed)
        else:
            return self.manual_drive(18, speed, angle)

    def forward_left(self, speed=None):
        """Move Rovio forward and left."""
        return self.manual_drive(7, speed)

    def forward_right(self, speed=None):
        """Move Rovio forward and right."""
        return self.manual_drive(8, speed)

    def back_left(self, speed=None):
        """Move Rovio backward and left."""
        return self.manual_drive(9, speed)

    def back_right(self, speed=None):
        """Move Rovio backward and right."""
        return self.manual_drive(10, speed)

    def head_up(self):
        """Move camera head looking up."""
        return self.manual_drive(11)

    def head_down(self):
        """Move camera head down, looking ahead."""
        return self.manual_drive(12)

    def head_middle(self):
        """Move camera head to middle position, looking ahead."""
        return self.manual_drive(13)

    def get_report(self):
        """
        Get Rovio's current status.

        Generate a report from libNS module that provides Rovio's current
        status.  Return a dictionary (keys are strings).

        Key                Description
        -----------------------------------------------------------------------
        responses          error checking (0: no error)
        x, y, theta        average location of Rovio in relation to the
                           strongest room beacon
                           x,y: -32767--32768
                           theta: -PI--PI
        room               room ID (0: home base, 1--9: mutable room projector)
        ss                 navigation signal strength
                           0--65535 (16 bit)
                           Strong signal > 47000
                           No signal < 5000
        beacon             signal strength for docking beacon when available
                           0--65535 (16 bit)
        beacon_x           horizontal position of beacon as seen by navigation
                           system (-32767--32768)
        next_room          the next strongest room beacon ID seen
                           -1: no room found
                           1--9: mutable room ID
        next_room_ss       the signal strength of the next strongest room
                           beacon
                           0--65535 (16 bit)
                           Strong signal > 47000
                           No signal < 5000
        state              0: idle
                           1: driving home
                           2: docking
                           3: executing path
                           4: recording path
        resistance         status of robot resistant to drive into navigation
                           system-deprived areas (NOT IN USE)
        sm                 currect status of the navigation state machine (for
                           debugging purposes)
        pp                 current way point when using path (1--10)
        flags              1: home position
                           2: obstacle detected
                           3: IR detector activated
        brightness         the current brightness (1 dimmest, 6 brightest)
        raw_resolution     0: [176x144]
                           1: [320x240]
                           2: [352x240]
                           3: [640x480]
        resolution         size of camera image as a list of [horz, vert]
        video_compression  0: low, 1: medium, 2: high
        frame_rate         video frame rate (1--30 fps)
        privilege          show current user privilege status
                           0: administrator
                           1: guest user
        user_check         whether need login and password (0 no, 1 yes)
        speaker_volume     0 (lowest) -- 31 (highest)
        mic_volume         0 (lowest) -- 31 (highest)
        wifi_ss            Wifi signal strength (0--254)
        show_time          whether to show time in the image (0 no, 1 yes)
        ddns_state         DDNS update status
                           0: no update
                           1: updating
                           2: update successful
                           3: update failed
        email_state        current status of email client (NOT IN USE)
        battery            < 100: turn self off
                           100--106: try to go home
                           106--127: normal
        charging           0--79: not charging
                           80: charging
        raw_head_position  204: position low
                           135--140: position mid-way
                           65: position high
        head_position      'low', 'mid', or 'high'
        raw_ac_freq        projector's frequency
                           0: not detected
                           1: 50 Hz
                           2: 60 Hz
        ac_freq            projector's frequency in Hz, or 0 if none

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (1,)
        r = self._get_request_response(page)
        d = self._parse_response(r)
        if d['responses'] == SUCCESS:
            d['raw_resolution'] = d['resolution']
            if d['raw_resolution'] == 0:
                d['resolution'] = [176,144]
            elif d['raw_resolution'] == 1:
                d['resolution'] = [320,240]
            elif d['raw_resolution'] == 2:
                d['resolution'] = [352,240]
            elif d['raw_resolution'] == 3:
                d['resolution'] = [640,480]
            d['raw_head_position'] = d['head_position']
            if d['raw_head_position'] < 135:
                d['head_position'] = 'high'
            elif d['raw_head_position'] > 140:
                d['head_position'] = 'low'
            else:
                d['head_position'] = 'mid'
            d['raw_ac_freq'] = d['ac_freq']
            if d['raw_ac_freq'] == 1:
                d['ac_freq'] = 50
            elif d['raw_ac_freq'] == 2:
                d['ac_freq'] = 60
        return d

    def start_recording(self):
        """
        Start recording a path.

        Rovio will resist going outside NorthStar (navigation system) coverage
        area while recording path.

        Rovio will stop recording if coverage is lost.

        Rovio will stop recording if user connection is lost.

        Return a command response code.

        """
        return self._simple_rev_cmd(2)

    def abort_recording(self):
        """
        Terminate recording of path.

        Does not store to flash memory.

        Return a command response code.

        """
        return self._simple_rev_cmd(3)

    def stop_recording(self, path_name='newpath'):
        """
        Stop recording and save path to flash memory.

        Path name should contain only alphanumeric characters (no whitespace or
        punctuation).

        Parameters:
          - path_name: name for saving path (default 'newpath')

        Return a command response code.

        """
        return self._simple_rev_cmd(4, path_name)

    def delete_path(self, path_name):
        """
        Delete the specified path.

        Parameters:
          - path_name: the path to delete

        Return a command response code.

        """
        return self._simple_rev_cmd(5, path_name)

    def get_path_list(self):
        """
        Return a list of paths stored in the Rovio.

        Return a command response code on error.

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (6,)
        r = self._get_request_response(page).strip()
        if r.startswith('Cmd = nav\nresponses = 0'):
            p = r[24:]
            paths = p.split('|')
            if paths[0] == '':
                paths = []
        else:
            paths = self._parse_response(r)['responses']
        return paths

    def play_path_forward(self, path_name):
        """
        Replays a stored path from closest point to the end.

        If navigation signal is lost, it stops.

        Parameters:
          - path_name: name of path to play

        Return a command response code.

        """
        return self._simple_rev_cmd(7, path_name)
        
    def play_path_backward(self, path_name):
        """
        Replays a stored path from closest point to the beginning.

        If navigation signal is lost, it stops.

        Parameters:
          - path_name: name of path to play

        Return a command response code.

        """
        return self._simple_rev_cmd(8, path_name)

    def stop_playing(self):
        """Stop playing a path."""
        return self._simple_rev_cmd(9)

    def pause_playing(self):
        """Pause the robot and wait for a new pause or stop command."""
        return self._simple_rev_cmd(10)

    def rename_path(self, old_path_name, new_path_name):
        """
        Rename the old path.

        Parameters:
          - old_path_name: old name of the path
          - new_path_name: new name of the path

        Return a command response code.

        """
        page = ('rev.cgi?Cmd=nav&action=%d&name=%s&newname=%s' %
                (11, old_path_name, new_path_name))
        r = self._get_request_response(page)
        return self._parse_response(r)['responses']

    def go_home(self):
        """Drive to home location in front of charging station."""
        return self._simple_rev_cmd(12)

    def go_home_and_dock(self):
        """Drive to home location and dock at charging station."""
        return self._simple_rev_cmd(13)

    def update_home_position(self):
        """Define current position as home location."""
        return self._simple_rev_cmd(14)

    def set_tuning_parameters(self):
        """
        Change homing, docking, and driving parameters.

        Speed for driving commands.

        Return a command response code.

        """
        return self._simple_rev_cmd(15)

    def get_tuning_parameters(self):
        """Return home, docking, and driving parameters."""
        page = 'rev.cgi?Cmd=nav&action=%d' % (16,)
        r = self._get_request_response(page)
        return self._parse_response(r)

    def reset_nav_state_machine(self):
        """Stops whatever it was doing and resets to idle state."""
        return self._simple_rev_cmd(17)

    def get_MCU_report(self):
        """
        Return MCU report (motor controller unit?).

        Including wheel encoders and IR obstacle avoidance.

        Return a firmware-dependent byte sequence.

        WARNING: The following table is OUT OF DATE with version 5 of the
        firmware!

        Offset Length Description
        -----------------------------------------------------------------------
        0      1B     Length of the packet
        1      1B     NOT IN USE
        2      1B     Direction of rotation of left wheel since last read
                      (bit 2)
        3      2B     Number of left wheel encoder ticks since last read
        5      1B     Direction of rotation of right wheel since last read
                      (bit 2)
        6      2B     Number of right wheel encoder ticks since last read
        8      1B     Direction of rotation of rear wheel since last read
                      (bit 2)
        9      2B     Number of rear wheel encoder ticks since last read
        11     1B     NOT IN USE
        12     1B     Head position
        13     1B     0x7F: battery full (0x7f or higher for new battery)
                      0x??: orange light in Rovio head (to be defined)
                      0x6A: very low battery (hungry, danger, very low battery
                            level), libNS needs to take control to go home and
                            charge
                      0x64: shutdown level (MCU will cut off power for
                            protecting the battery)
        14     1B     bit 0: light LED (head) status, 0 off, 1 on
                      bit 1: IR-Radar power status, 0 off, 1 on
                      bit 2: IR-Radar detector status
                             0: fine
                             1: barrier detected
                      bit 3--5: charger status
                                0x00: nothing happening
                                0x01: charging completed
                                0x02: in charging
                                0x04: something wrong, error occurred
                      bit 6,7: undefined, not used

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (20,)
        r = self._get_request_response(page)
        d = self._parse_response(r)
        return d['responses']

    def clear_all_paths(self):
        """Delete all paths in flash memory."""
        return self._simple_rev_cmd(21)

    def get_status(self):
        """
        Report navigation state.

        Return a dictionary:
        {'responses': response code,
         'raw_state': 0 (idle)
                      1 (driving home)
                      2 (docking)
                      3 (executing path)
                      4 (recording path)
         'state': 'idle', 'driving home', 'docking', 'executing path', or
                  'recording path'}

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (22,)
        r = self._get_request_response(page)
        d = self._parse_response(r)
        if d['responses'] == SUCCESS:
            d['raw_state'] = d['state']
            if d['raw_state'] == 0:
                d['state'] = 'idle'
            elif d['raw_state'] == 1:
                d['state'] = 'driving home'
            elif d['raw_state'] == 2:
                d['state'] = 'docking'
            elif d['raw_state'] == 3:
                d['state'] = 'executing path'
            elif d['raw_state'] == 4:
                d['state'] = 'recording path'
        return d

    def save_parameter(self, index, value):
        """
        Stores parameter in the robot's flash.

        Parameters:
          - index: 0--19
          - value: 32-bit signed integer

        Return response code NO_MEMORY_AVAILABLE or
        PARAMETER_OUTOFRANGE on error.

        """
        page = ('rev.cgi?Cmd=nav&action=%d&index=%d&value=%d' %
                (23, index, value))
        r = self._get_request_response(page)
        return self._parse_response(r)

    def read_parameter(self, index):
        """
        Read parameter from the robot's flash.

        Parameters:
          - index: 0--19

        Return a dict with response code and parameter value.

        """
        page = ('rev.cgi?Cmd=nav&action=%d&index=%d' % (24,
                                                        index))
        r = self._get_request_response(page)
        return self._parse_response(r)

    def read_all_parameters(self):
        """
        Read all parameters from the robot's flash.

        Return a dict with parameter indices and values.

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % 24
        r = self._get_request_response(page)
        return self._parse_response(r)

    def get_libNS_version(self):
        """Return string version of libNS and NS sensor."""
        page = 'rev.cgi?Cmd=nav&action=%d' % (25,)
        r = self._get_request_response(page)
        return self._parse_response(r)['version']

    def email_image(self, email):
        """
        Emails current image or if in path recording mode sets an action.

        Parameters:
          - email: email address

        """
        page = ('rev.cgi?Cmd=nav&action=%d&email=%d' % (26,
                                                        email))
        r = self._get_request_response(page)
        return self._parse_response(r)

    def reset_home_location(self):
        """Clear home location in flash memory."""
        return self._simple_rev_cmd(27)

    def get_data(self):
        """
        Do nothing.
        
        Rovio API documentation on this command is not very good.  Does nothing
        at the moment.

        """
        return None

    def get_image(self, imgID = None):
        """
        Acquire an image from the Rovio webcam.

        Parameters:
          - imgID: optional integer value for image tagging (default None)

        Return a JPEG image.

        """
        if imgID is None:
            return self._get_request_response('Jpeg/CamImg.jpg')
        else:
            return self._get_request_response('Jpeg/CamImg%d.jpg' % imgID)

    def stream_video(self):
        """Streaming video not yet supported."""
        return None

    def change_resolution(self, ResType=2, RedirectURL=None):
        """
        Change the resolution of the camera's images.

        Parameters:
          - ResType: Camera supports 4 resolutions.
                     0: 176x144
                     1: 352x288
                     2: 320x240 (default)
                     3: 640x480
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeResolution.cgi?ResType=%d' % (ResType,)
        else:
            page = ('ChangeResolution.cgi?ResType=%d&RedirectURL=%s' %
                    (ResType, RedirectURL))
        return self._get_request_response(page)
        
    def change_compress_ratio(self, Ratio=1, RedirectURL=None):
        """
        Change the quality setting of camera's images (MPEG only).

        Parameters:
          - Ratio: 0 low, 1 medium, 2 high quality (default 1)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeCompressRatio.cgi?Ratio=%d' % (Ratio,)
        else:
            page = ('ChangeCompressRatio.cgi?Ratio=%d&RedirectURL=%s' %
                    (Ratio, RedirectURL))
        return self._get_request_response(page)
        
    def change_framerate(self, Framerate=30, RedirectURL=None):
        """
        Change the frame rate of camera's images.

        Parameters:
          - Framerate: 2--32 frames per second (default 30)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeFramerate.cgi?Framerate=%d' % (Framerate,)
        else:
            page = ('ChangeFramerate.cgi?Framerate=%d&RedirectURL=%s' %
                    (Framerate, RedirectURL))
        return self._get_request_response(page)
        
    def change_brightness(self, Brightness=6, RedirectURL=None):
        """
        Change the brightness of camera's images.

        Parameters:
          - Brightness: 0--6, lower is dimmer (default 6)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeBrightness.cgi?Brightness=%d' % (Brightness,)
        else:
            page = ('ChangeBrightness.cgi?Brightness=%d&RedirectURL=%s' %
                    (Brightness, RedirectURL))
        return self._get_request_response(page)
        
    def change_speaker_volume(self, SpeakerVolume=15, RedirectURL=None):
        """
        Change the speaker volume of the Rovio.

        Parameters:
          - SpeakerVolume: 0--31, lower is quieter (default 15)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = ('ChangeSpeakerVolume.cgi?SpeakerVolume=%d' %
                    (SpeakerVolume,))
        else:
            page = ('ChangeSpeakerVolume.cgi?SpeakerVolume=%d&RedirectURL=%s' %
                    (SpeakerVolume, RedirectURL))
        return self._get_request_response(page)
        
    def change_mic_volume(self, MicVolume=15, RedirectURL=None):
        """
        Change the microphone volume of the Rovio.

        Parameters:
          - MicVolume: 0--31, lower is quieter (default 15)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeMicVolume.cgi?MicVolume=%d' % (MicVolume,)
        else:
            page = ('ChangeMicVolume.cgi?MicVolume=%d&RedirectURL=%s' %
                    (MicVolume, RedirectURL))
        return self._get_request_response(page)
        
    def set_camera(self, Frequency=0, RedirectURL=None):
        """
        Change camera sensor's settings.

        Parameters:
          - Frequency: 0: auto-detect (default), 50: 50Hz, 60: 60Hz
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'SetCamera.cgi?Frequency=%d' % (Frequency,)
        else:
            page = ('SetCamera.cgi?Frequency=%d&RedirectURL=%s' %
                    (Frequency, RedirectURL))
        return self._get_request_response(page)
        
    def manual_drive(self, command, speed=None, angle=None):
        """
        Send a movement command to the Rovio.

        In general, this command should not be called directly.

        Parameters:
          - command: the movement command ID (integer)
                     0   stop
                     1   forward
                     2   backward
                     3   straight left
                     4   straight right
                     5   rotate left by speed
                     6   rotate right by speed
                     7   diagonal forward left
                     8   diagonal forward right
                     9   diagonal back left
                     10  diagonal back right
                     11  head up (camera)
                     12  head down (camera)
                     13  head middle (camera)
                     17  rotate left 20 degrees
                     18  rotate right 20 degrees
          - speed: speed to move (default is self.speed)

        Return the response code (0 for success).

        """
        if speed is None:
            speed = self.speed
        # camera commands
        if 11 <= command <= 13:
            page = 'rev.cgi?Cmd=nav&action=%d&drive=%d' % (18, command)
        # rotate commands
        elif command == 17 or command == 18:
            page = ('rev.cgi?Cmd=nav&action=%d&drive=%d&angle=%d&speed=%d' %
                    (18, command, angle, speed))
        # all other movement commands
        else:
            page = ('rev.cgi?Cmd=nav&action=%d&drive=%d&speed=%d' %
                    (18, command, speed))
        r = self._get_request_response(page)
        return self._parse_response(r)['responses']

    def _get_request_response(self, page):
        """
        Send a command to the Rovio and return its response.

        In general, this command should not be called directly.

        Parameters:
          - page: the Rovio API command to request

        Return the raw response.

        """
        url = self._base_url + page
        req = urllib2.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        if self._base64string is not None:
            req.add_header("Authorization", "Basic %s" % self._base64string)
        f = urllib2.urlopen(req)
        data = f.read()
        return data;

    def _parse_response(self, response):
        """
        Parse the response of some Rovio CGI commands.

        In general, this command should not be called directly.

        Responses are of the form (for example):
        'Cmd = nav\nresponses = 0\n|x=-5644|...'
        For this example, return:
        {'Cmd' : 'nav', 'responses' : '0', 'x' : '-5644', ...}

        Return a dictionary of response key/value pairs.

        """
        reply = dict()
        # split on | (bar)
        rlst = response.split('|')
        # handle Cmd=... first line specially
        rlst[0:1] = rlst[0].splitlines()
        # split key=val into key,val pairs
        for pair in rlst:
            try:
                (key,val) = pair.split('=')
            except ValueError:
                key = pair
                val = None
            key = key.strip()
            if val is not None:
                val = val.strip()
            # try to convert to int
            if key != 'flags':
                try:
                    val = int(val)
                except ValueError:
                    pass
                except TypeError:
                    pass
            reply[key] = val
        return reply

    def _compile_URLs(self):
        """Compile all URLs for use in _get_request_response."""
        if self._username is not None and self._password is not None:
            self._base64string = base64.encodestring('%s:%s' %
                                                     (self._username,
                                                      self._password))[:-1]
        else:
            self._base64string = None
        self._base_url = '%s://%s:%d/' % (self._protocol, self._host,
                                          self._port)

    def _simple_rev_cmd(self, commandID, name=None):
        """Make simple rev.cgi calls (for path ops, not manual_drive)"""
        if name is None:
            page = 'rev.cgi?Cmd=nav&action=%d' % (commandID,)
        else:
            page = 'rev.cgi?Cmd=nav&action=%d&name=%s' % (commandID, name)
        r = self._get_request_response(page)
        return self._parse_response(r)['responses']

class RovioController(threading.Thread):

    """
    Controls the Rovio robot.

    A higher-level wrapper for the API.

    Attributes:
      - rovio: the Rovio being controlled (read-only)
      - wait: the amount of time to sleep before checking the Rovio event queue

    """

    def getRovio(self): return self._rovio
    rovio = property(getRovio, doc="""Rovio being controlled (read-only)""")

    def __init__(self, rovio):
        """
        Initialize a RovioController.

        Parameters:
          - rovio: rovio object to be controlled

        """
        threading.Thread.__init__(self)
        self._rovio = rovio
        self._running = True
        self._queue = []
        self.wait = 0.1

    def enqueue(self, millis, command, params=[]):
        self._queue.append([None, millis, command, params])

    def enqueue_all(self, commands):
        self._queue.extend(commands)

    def interrupt(self, millis, command, params=[]):
        self._queue = [[None, millis, command, params]]

    def clear(self):
        self._queue = []

    def _dispatch(self):
        if len(self._queue) > 0:
            cmd = self._queue[0][2]
            parms = self._queue[0][3]
            if isinstance(parms, list) or isinstance(parms, tuple):
                cmd(*parms)
            elif isinstance(parms, dict):
                cmd(**parms)

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            if len(self._queue) > 0:
                if self._queue[0][0] is None:
                    # start executing
                    self._queue[0][0] = time.time()
                    self._dispatch()
                else:
                    # continue executing, check for time
                    now = time.time()
                    elapsed = (now - self._queue[0][0]) * 1000
                    millis = self._queue[0][1]
                    if elapsed > millis:
                        self._queue = self._queue[1:]
                    else:
                        self._dispatch()
            time.sleep(self.wait)

#######################
# TESTING AND SCRIPTS #
#######################

if __name__ == "__main__":
    pass
