#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from drivers import drivers_logging as logger
from configs import settings
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from launcher.launcher_tools import obci_root
import json

LOGGER = logger.get_logger("DriverDiscovery", "info")

class DriverDiscovery(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(DriverDiscovery, self).__init__(addresses=addresses, type=peers.DRIVER_DISCOVERY)

        self._mx_addresses = addresses

        self.drivers = []

        self.find_drivers()
        self.serialize_drivers_info(self.drivers)

        self.ready()


    def find_drivers(self):
        pass

    def _add_driver(self, driver_desc):
        desc = json.loads(driver_desc)
        self.drivers.append(desc)

    def serialize_drivers_info(self, driver_list):
        dl = [

                {    
                    "name":"Porti7-24e4b4at",
                   "physical_channels": 34,
                   "sampling_rates":[128,256,512,1024,2048],
                   "channels": [        
                                        {"name": "ExG1", 
                                            "gain": 1.0167751312255859e+00, 
                                            "offset": -1.3535621337890625e+03,
                                            "a": 7.1500003337860107e-02, 
                                            "b": 0.0000000000000000e+00, 
                                            "idle": -2147483648, 
                                            "type": "EXG ", 
                                            "unit": "Volt -6"}
                                   ]
                },
                
                    {   "name":"Dummy Amplifier",
                    "physical_channels": 0,
                    "sampling_rates":[128,256,2048],
                    "channels": [       {"name": "Sinus[128]84Volt-3", "gain": 1.9116473575122654e+00, "offset": -2.5649296506250000e+08,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Cos[128]36Volt-3", "gain": 5.5396995553746819e-01, "offset": -3.0497500610351562e+02,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Modulo[128]63Volt-3", "gain": 1.9522297247312963e+00, "offset": -1.3094891909375000e+08,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Random[128]27Volt-3", "gain": 1.6069688759744167e+00, "offset": -1.6850019960937500e+06,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Sinus[256]12Volt-3", "gain": 1.5667908918112516e-01, "offset": 1.1994865939605713e+07,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Cos[256]31Volt-3", "gain": 1.2182569052092731e+00, "offset": -2.5851867830000000e+09,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Modulo[256]30Volt-3", "gain": 6.3755226740613580e-01, "offset": -6.6849200634765625e+05,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Random[256]68Volt-3", "gain": 1.7713576974347234e+00, "offset": -3.9635079223632812e+05,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Sinus[512]30Volt-3", "gain": 2.2833147458732128e+00, "offset": -7.6615299375000000e+07,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Cos[512]38Volt-3", "gain": 2.9493270749226213e+00, "offset": -3.1288158330000000e+09,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Modulo[512]14Volt-3", "gain": 2.8902326021343470e+00, "offset": -2.4231028328125000e+07,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Random[512]74Volt-3", "gain": 1.0630958382971585e+00, "offset": 2.6568459687500000e+06,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Sinus[1024]6Volt-3", "gain": 2.6666574925184250e-01, "offset": -4.3630516357421875e+03,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Cos[1024]6Volt-3", "gain": 1.6677237604744732e+00, "offset": -1.3983880878906250e+07,
                 "idle": 1, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Modulo[1024]25Volt-3", "gain": 9.3080979492515326e-01, "offset": -9.9944938200000000e+08,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Random[1024]68Volt-3", "gain": 3.5404867958277464e-01, "offset": 6.7998549816608429e+07,
                 "idle": 256, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Sinus[1024]88Volt-3", "gain": 2.8292010929435492e+00, "offset": -4.6265630706787109e+04,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Cos[1024]85Volt-3", "gain": 2.6866699079982936e+00, "offset": -5.7695796100000000e+09,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Modulo[1024]33Volt-3", "gain": 4.3955991929396987e-01, "offset": -4.7197383650000000e+08,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Random[1024]13Volt-3", "gain": 9.1097203036770225e-01, "offset": -9.7813576950000000e+08,
                 "idle": 262144, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Sinus[2048]96Volt-3", "gain": 1.1476600146852434e+00, "offset": -2.0485218688964844e+05,
                 "idle": 4096, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Cos[2048]2Volt-3", "gain": 2.8105941228568554e-01, "offset": -7.3446311500000000e+07,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Modulo[2048]53Volt-3", "gain": 2.1875331094488502e+00, "offset": -4.6446915820000000e+09,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -9",
                 "other_params": []},
                        {"name": "Random[2048]42Volt-3", "gain": 1.9068039334379137e+00, "offset": -4.0948302250000000e+09,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Sinus[4096]41Volt-3", "gain": 1.9847516645677388e+00, "offset": -6.6597173765625000e+07,
                 "idle": 32, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Cos[4096]72Volt-3", "gain": 3.6866354150697589e-01, "offset": -3.0925019335937500e+06,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -3",
                 "other_params": []},
                        {"name": "Modulo[4096]68Volt-3", "gain": 1.5238979179412127e-01, "offset": -2.5158455664062500e+05,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "Random[4096]66Volt-3", "gain": 2.7450713887810707e+00, "offset": 4.3512375183105469e+04,
                 "idle": 2147483648, "type": "UNKNOWN", "unit": "Volt -6",
                 "other_params": []},
                        {"name": "temp2", "gain": 1.0000000000000000e+00, "offset": 0.0000000000000000e+00,
                 "idle": -2147483648, "type": "UNKNOWN", "unit": "Unknown",
                 "other_params": []},
                        {"name": "Driver_Saw", "gain": 1.0000000000000000e+00, "offset": 0.0000000000000000e+00,
                 "idle": 2147483648, "type": "ZAAG", "unit": "Integer",
                 "other_params": []},
                        {"name": "Trigger", "gain": 1.0000000000000000e+00, "offset": 0.0000000000000000e+00,
                 "idle": 1, "type": "Boolean", "unit": "Bit",
                 "other_params": []}
                 ]
                 

                }

        ]
        self.set_param('available_drivers', dl)


if __name__ == '__main__':
    DriverDiscovery(settings.MULTIPLEXER_ADDRESSES).loop()