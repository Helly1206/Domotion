# -*- coding: utf-8 -*-
#########################################################
# SERVICE : Domotion.py                                 #
#           The main class for runnnig Domotion         #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import os
import logging
import logging.handlers
import signal
import sys
import time
from webif import webapp
from engine import commandqueue
from engine import engine
from engine import localaccess
from hardware import lirc
from hardware import pi433MHz
from hardware import domoticz_if
from hardware import url
from frontend import domoticz_frontend
from utilities import domoticz_api

####################### GLOBALS #########################
LOG_FILENAME = 'Domotion.log'
LOG_MAXSIZE = 100*1024*1024

#########################################################
# Class : AppKiller                                     #
#########################################################
class AppKiller(object):
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_app)
        signal.signal(signal.SIGTERM, self.exit_app)

    def exit_app(self,signum, frame):
        self.kill_now = True 

#########################################################
# Class : Domotion                                      #
#########################################################
class Domotion(object):
    def __init__(self):
        self.logger = logging.getLogger('Domotion')
        self.logger.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_MAXSIZE, backupCount=5)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        logging.captureWarnings(True)
        self.logger.info("Starting Domotion")
        self.killer = AppKiller()

        #start queue and engine
        self.commandqueue=commandqueue()
        self.engine = engine(self.commandqueue,"./Domotion.db")

        #start domoticz api (even when no domoticz connection is made)
        self.domoticz_api = domoticz_api()

        #start hardware
        if (localaccess.GetSetting('Pi433MHz')):
            self.pi433MHz = pi433MHz(self.commandqueue)
            self.pi433MHz.start()
        else:
            self.logger.info("Pi433MHz hardware disabled")
            self.pi433MHz = None
    
        if (localaccess.GetSetting('LIRC')):
            self.lirc = lirc(self.commandqueue)
            self.lirc.start()
        else:
            self.logger.info("LIRC interface disabled")
            self.lirc = None
    
        if (localaccess.GetSetting('Domoticz')):
            self.domoticz_if = domoticz_if(self.commandqueue)
            self.domoticz_if.start()
        else:
            self.logger.info("Domoticz interface disabled")
            self.domoticz_if = None
    
        if (localaccess.GetSetting('URL')):
            self.url = url(self.commandqueue)
            self.url.start()
        else:
            self.logger.info("URL interface disabled")
            self.url = None
    
        #start frontend
        if (localaccess.GetSetting('Domoticz_frontend')):
            self.domoticz_frontend = domoticz_frontend(self.commandqueue)
            self.domoticz_frontend.start()
        else:
            self.logger.info("Domoticz frontend disabled")
            self.domoticz_frontend = None
    
        #start webapp
        self.webapp = webapp()
        self.webapp.setDaemon(True)
        self.webapp.start()

        self.engine.instances(self.domoticz_api, self.domoticz_frontend, self.url, self.domoticz_if, self.lirc, self.pi433MHz)
        self.engine.DomoticzMessenger("Domotion Running")

    def __del__(self):
        self.engine.DomoticzMessenger("Domotion Finished")

        #stop webapp
        del self.webapp
    
        #stop frontend
        if (self.domoticz_frontend != None):
            self.domoticz_frontend.terminate()
            self.domoticz_frontend.join()
            del self.domoticz_frontend
    
        #stop hardware
        if (self.url != None):
            self.url.terminate()
            self.url.join()
            del self.url

        if (self.domoticz_if != None):
            self.domoticz_if.terminate()
            self.domoticz_if.join()
            del self.domoticz_if

        if (self.lirc != None):
            self.lirc.terminate()
            self.lirc.join()
            del self.lirc
    
        if (self.pi433MHz != None):
            self.pi433MHz.terminate()
            self.pi433MHz.join()
            del self.pi433MHz
    
        # stop domoticz_api, queue and engine
        del self.domoticz_api
        del self.engine
        del self.commandqueue
        self.logger.info("Domotion Ready")
        logging.shutdown()

    def run(self):
        while(True):
            if (not self.engine.loop()):
                time.sleep(0.1)
            if self.killer.kill_now:
                break   

#########################################################
# Main function                                         #
#########################################################
if __name__ == '__main__':
    Domotion().run()