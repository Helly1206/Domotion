# -*- coding: utf-8 -*-
#########################################################
# SERVICE : timer.py                                    #
#           Python timer handling Domotion              #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
from localaccess import localaccess
from commandqueue import commandqueue
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
maxcnt = (1000/sleeptime)
updatecnt = (1/sleeptime)

#########################################################
# Class : timer                                         #
#########################################################
class timer(Thread):
    def __init__(self, commandqueue):
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Timer')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        
    def __del__(self):
        del self.mutex
        del self.term
        self.logger.info("finished")

    def terminate(self):
            self.term.set()

    def run(self):
        counter = 0
        self.logger.info("running")

        while (not self.term.isSet()):
            if (counter % updatecnt == 0):
                self.mutex.acquire()
                pass
                self.mutex.release()
            sleep(sleeptime)
            if (counter < maxcnt):
                counter += 1
            else:
                counter = 0

        self.logger.info("terminating")