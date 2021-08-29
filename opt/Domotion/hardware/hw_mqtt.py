# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_mqtt.py                                  #
#           Python mqtt handling for Domotion           #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
from threading import Lock
import logging
from base64 import b64decode
from uuid import getnode
from engine.localaccess import localaccess
from engine.commandqueue import commandqueue
try:
    import paho.mqtt.client as mqttclient
    ifinstalled = True
except ImportError:
    ifinstalled = False
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : mqtt                                          #
#########################################################

class mqtt(object):
    def __init__(self, commandqueue, localaccess):
        self.commandqueue=commandqueue
        self.localaccess=localaccess
        self.logger = logging.getLogger('Domotion.MQTT')
        self.mutex = Lock()
        self.connected = False
        self.SubscribeList = {}
        self.rcConnect = 0
        self.rcDisconnect = 0
        if ifinstalled:
            self.client = mqttclient.Client("Domotion_" + format(getnode(),'X')[-6:])  #create new instance
            self.client.on_message=self._onmessage #attach function to callback
            self.client.on_connect=self._onconnect  #bind call back function
            self.client.on_disconnect=self._ondisconnect  #bind call back function
            self.client.on_log=self._onlog
        else:
            self.client = None

    def __del__(self):
        del self.mutex
        if self.client:
            del self.client
        self.logger.info("finished")

    def UpdateDevices(self, sensors, actuators):
        # subscribe and publish to devices
        self.mutex.acquire()
        self._SubscribeSensors(sensors)
        self._SubscribeActuators(actuators)
        self.mutex.release()

    def terminate(self):
        self.logger.info("terminating")
        if self.client:
            #self.client.wait_for_publish() # wait for all messages published
            self.client.loop_stop()    #Stop loop
            self.client.disconnect() # disconnect

    def start(self):
        try:
            self.logger.info("running")

            if (not self.client):
                self.logger.warning("mqtt not installed, terminating")
                self.terminate()
            else:
                if self.localaccess.GetSetting('MQTT_username'):
                    if self.localaccess.GetSetting('MQTT_password'):
                        self.client.username_pw_set(self.localaccess.GetSetting('MQTT_username'), password=b64decode(self.localaccess.GetSetting('MQTT_password')))
                    else:
                        self.client.username_pw_set(self.localaccess.GetSetting('MQTT_username'), password=None)
                try:
                    self.client.connect(self.localaccess.GetSetting('MQTT_brokeraddress'), port=int(self.localaccess.GetSetting('MQTT_port'))) #connect to broker
                    self.client.loop_start() #start the loop
                except:
                    self.logger.error("Invalid connection, check server address")
        except Exception as e:
            self.logger.exception(e)

    def SetActuator(self, mainTopic, subTopic, value):
        res = False
        self.mutex.acquire()
        if self.client:
            self.client.publish(self._buildTopic(mainTopic, subTopic), value, int(self.localaccess.GetSetting('MQTT_QOS')), self.localaccess.GetSetting('MQTT_retain'))
            res = True
        self.mutex.release()
        return res

    def _onlog(self, client, userdata, level, buf):
        self.logger.debug(buf)

    def _onmessage(self, client, userdata, message):
        self.mutex.acquire()
        if message.topic in self.SubscribeList.keys():
            if self.SubscribeList[message.topic]: # isSensor
                self.commandqueue.put_device("MQTT", self._mainTopic(message.topic), self._subTopic(message.topic), message.payload.decode('utf-8'), True)
            else: # actuator: don't set hardware, only update value
                self.commandqueue.put_device("None", self._mainTopic(message.topic), self._subTopic(message.topic), message.payload.decode('utf-8'), False)
        self.mutex.release()

    def _onconnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected OK, Returned code = " + str(rc))
            self.connected = True
            self.rcDisconnect = 0
        else:
            if self.rcConnect != rc:
                self.logger.info("Bad connection, Returned code = " + str(rc))
            self.connected = False
        self.rcConnect = rc

    def _ondisconnect(self, client, userdata, rc):
        if rc == 0 or self.rcDisconnect != rc:
            self.logger.info("Disconnected, Returned code = " + str(rc))
            self.rcConnect = 0
        self.connected = False
        self.rcDisconnect = rc

    def _SubscribeSensors(self, sensors):
        topicList = []
        if (self.client):
            for sensor in sensors:
                prop = self.localaccess.GetSensorProperties(sensor)
                topicList.append(self._buildTopic(prop['DeviceURL'], prop['KeyTag']))
            for key in list(self.SubscribeList):
                if not key in topicList and self.SubscribeList[key]:
                    del self.SubscribeList[key]
                    self.client.unsubscribe(key)
            for topic in topicList:
                if not topic in self.SubscribeList.keys():
                    self.SubscribeList[topic] = True #isSensor
                    self.client.subscribe(topic, int(self.localaccess.GetSetting('MQTT_QOS')))

    def _SubscribeActuators(self, actuators):
        topicList = []
        if (self.client):
            for actuator in actuators:
                prop = self.localaccess.GetActuatorProperties(actuator)
                topicList.append(self._buildTopic(prop['DeviceURL'], prop['KeyTag']))
            for key in list(self.SubscribeList):
                if not key in topicList and not self.SubscribeList[key]:
                    del self.SubscribeList[key]
                    self.client.unsubscribe(key)
            for topic in topicList:
                if not topic in self.SubscribeList.keys():
                    self.SubscribeList[topic] = False #not isSensor
                    self.client.subscribe(topic, int(self.localaccess.GetSetting('MQTT_QOS')))

    def _buildTopic(self, maintopic, subtopic):
        topic = ""
        if maintopic:
            if maintopic.startswith("/"):
                topic = maintopic[1:]
            else:
                topic = maintopic
            if topic.endswith("/"):
                topic = topic[0:-1]
        if subtopic:
            if not subtopic.startswith("/"):
                topic += "/"
            topic += subtopic
            if topic.endswith("/"):
                topic = topic[0:-1]
        return topic

    def _mainTopic(self, topic):
        maintopic = ""
        if topic:
            if topic.count("/") > 0:
                maintopic = topic.rsplit("/",1)[0]
        return maintopic

    def _subTopic(self, topic):
        subtopic = ""
        if topic:
            if topic.count("/") > 0:
                subtopic = topic.rsplit("/",1)[1]
            else:
                subtopic = topic
        return subtopic
