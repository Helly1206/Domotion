# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_lirc.py                                  #
#           Python lirc handling for Domotion           #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from lircif import lircif
from threading import Thread, Event, Lock
import logging
from time import sleep
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
retrytime = 10 / sleeptime # test every 10s
retries = 10

#########################################################
# Class : hw_lirc                                       #
#########################################################
class lirc(Thread):
    def __init__(self, commandqueue):
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Lirc')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        self.lircif = lircif()
        self.lircrunning = False
        
    def __del__(self):
        del self.mutex
        del self.term
        del self.lircif
        self.logger.info("finished")

    def terminate(self):
            self.term.set()

    def run(self):
        try:
            testing = False
            testcnt = retrytime 
            testretries = retries 

            self.logger.info("running")

            if (not self._TestLirc()):
                testing = True
                self.logger.warning("lircd not running, retrying")
            while (not self.term.isSet() and (testretries>0)):
                if (not testing):
                    sockerror,device,key,repeat = self.lircif.ReadKey()
                    if sockerror:
                        if (not self._TestLirc(True)):
                            testing = True
                            testcnt = retrytime 
                            testretries = retries 
                    elif (key):
                        if (not repeat and self.commandqueue):
                            self.commandqueue.put_device("lirc",device,key,1)
                    else:
                        sleep(sleeptime)
                if (testing):
                    sleep(sleeptime)
                    if (testcnt > 0):
                        testcnt -= 1
                    else:
                        testcnt = retrytime
                        if (not self._TestLirc()):
                            if (retries == testretries):
                                self.logger.warning("lircd not running, retrying")
                            elif (testretries <= 1):
                                self.logger.warning("lircd not running, terminating")
                            testretries -= 1
                        else:
                            testing = False    
                            self.logger.info("lircd connection established") 

            self.logger.info("terminating")
        except Exception, e:
            self.logger.exception(e)

    def _TestLirc(self, reset = False):
        self.mutex.acquire()
        if (not self.lircrunning or reset):
            if (self.lircif.test()):               
                self.lircif.close()
                self.lircrunning = self.lircif.init(1)
            else:
                self.lircrunning = False
        self.mutex.release()
        return self.lircrunning

    def send(self, device, key):
        if (self._TestLirc()):
            sockerror,success = self.lircif.WriteKey(device, key)
            if sockerror:
                self._TestLirc(True)
        return success
