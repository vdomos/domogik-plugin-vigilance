#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Vigilance

Implements
==========

- VigilanceManager

@author: domos  (domos dt vesta at gmail dt com)
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.common.plugin import Plugin
from domogikmq.message import MQMessage
from domogikmq.reqrep.client import MQSyncReq

from domogik_packages.plugin_vigilance.lib.vigilance import Vigilance, VigilanceException
import threading
import traceback
import re
import json
import time

class VigilanceManager(Plugin):
    """ Get weather vigilance informations
    """

    def __init__(self):
        """ Init plugin
        """
        Plugin.__init__(self, name='vigilance')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        #if not self.check_configured():
        #    return

        # get the devices list
        self.devices = self.get_device_list(quit_if_no_device = True)

        # get the sensors id per device : 
        self.sensors = self.get_sensors(self.devices)

        # create a Vigilance thread for each device
        vigilancethreads = {}
        vigilance_list = {}
        for a_device in self.devices:
            try:
                # global device parameters
                departement = self.get_parameter(a_device, "departement")
                device_id = a_device["id"]                
                vigilance_list[departement] = Vigilance(self.log, self.send_data, self.get_stop(), device_id, departement)

                # start the vigilance thread
                self.log.info(u"Start to check vigilance forecast for departement '%s'" % departement)
                thr_name = "{0}".format(departement)
                vigilancethreads[thr_name] = threading.Thread(None,
                                              vigilance_list[departement].check,
                                              thr_name,
                                              (),
                                              {})
                vigilancethreads[thr_name].start()
                self.register_thread(vigilancethreads[thr_name])

            except:
                self.log.error(u"{0}".format(traceback.format_exc()))   # we don't quit plugin if an error occured, a vigilance device can be KO and the others be ok

        self.ready()



    def send_data(self, device_id, dep, vigilanceColors, vigilanceRisk, vigilanceInfo):
        """ Send the vigilance sensors values over MQ
        """
        data = {}
        data[self.sensors[device_id]["vigilanceDep"]] = dep
        data[self.sensors[device_id]["vigilanceColor"]] = vigilanceColors[0] 
        data[self.sensors[device_id]["vigilanceColorWind"]] = vigilanceColors[1]  
        data[self.sensors[device_id]["vigilanceColorRain"]] = vigilanceColors[2]   
        data[self.sensors[device_id]["vigilanceColorThunderstorms"]] = vigilanceColors[3]   
        data[self.sensors[device_id]["vigilanceColorFlood"]] = vigilanceColors[4]  
        data[self.sensors[device_id]["vigilanceColorSnow"]] = vigilanceColors[5]  
        data[self.sensors[device_id]["vigilanceColorHeat"]] = vigilanceColors[6]   
        data[self.sensors[device_id]["vigilanceColorCold"]] = vigilanceColors[7]   
        data[self.sensors[device_id]["vigilanceColorAvalanches"]] = vigilanceColors[8]   
        data[self.sensors[device_id]["vigilanceColorSubmersion"]] = vigilanceColors[9]  
        
        data[self.sensors[device_id]["vigilanceRisk"]] = vigilanceRisk
        data[self.sensors[device_id]["vigilanceInfo"]] = vigilanceInfo 
        
        self.log.info("==> 0MQ PUB sended = %s" % format(data))

        try:
            self._pub.send_event('client.sensor', data)
        except:
            self.log.debug(u"Bad MQ message to send : {0}".format(data))
            pass


        
if __name__ == "__main__":
    vigilance = VigilanceManager()
