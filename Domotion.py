# -*- coding: utf-8 -*-
#########################################################
# SERVICE : Domotion.py                                 #
#           The main class for runnnig Domotion         #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import logging
import logging.handlers
from time import sleep
from webif import webapp
from engine import commandqueue
from engine import engine
from engine import localaccess
from engine import AppKiller
from hardware import lirc
from hardware import pi433MHz
from hardware import domoticz_if
from hardware import url
from hardware import gpio
from frontend import domoticz_frontend
from frontend import domoticz_api

import sys
import os
import psutil

####################### GLOBALS #########################
LOG_FILENAME = 'Domotion.log'
LOG_MAXSIZE = 100*1024*1024
DB_FILENAME = "Domotion.db"
VERSION = "0.01"
LoopTime = 0.1

#########################################################
# Class : Domotion                                      #
#########################################################
class Domotion(object):
    def __init__(self, Debug):
        self.logger = logging.getLogger('Domotion')
        self.logger.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.handlers.RotatingFileHandler(self.GetLogger(), maxBytes=LOG_MAXSIZE, backupCount=5)
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
        self.engine = engine(self.commandqueue, self.GetDB(), LoopTime)

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
    
        if (localaccess.GetSetting('GPIO')):
            self.gpio = gpio(self.commandqueue)
            self.gpio.start()
        else:
            self.logger.info("PiGPIO interface disabled")
            self.gpio = None

        #start frontend
        if (localaccess.GetSetting('Domoticz_frontend')):
            self.domoticz_frontend = domoticz_frontend(self.commandqueue)
            self.domoticz_frontend.start()
        else:
            self.logger.info("Domoticz frontend disabled")
            self.domoticz_frontend = None
    
        #start webapp
        self.webapp = webapp(Debug)
        self.webapp.setDaemon(True)
        self.webapp.start()

        self.engine.instances(self.domoticz_api, self.domoticz_frontend, self.gpio, self.url, self.domoticz_if, self.lirc, self.pi433MHz)
        self.engine.DomoticzMessenger("Domotion Running")

    def __del__(self):
        self.engine.DomoticzMessenger("Domotion Finished")

        #stop webapp
        if (self.webapp != None):
            self.webapp.terminate()
            self.webapp.join(5)
            del self.webapp
    
        #stop frontend
        if (self.domoticz_frontend != None):
            self.domoticz_frontend.terminate()
            self.domoticz_frontend.join(5)
            del self.domoticz_frontend
    
        #stop hardware
        if (self.gpio != None):
            self.gpio.terminate()
            self.gpio.join(5)
            del self.gpio

        if (self.url != None):
            self.url.terminate()
            self.url.join(5)
            del self.url

        if (self.domoticz_if != None):
            self.domoticz_if.terminate()
            self.domoticz_if.join(5)
            del self.domoticz_if

        if (self.lirc != None):
            self.lirc.terminate()
            self.lirc.join(5)
            del self.lirc
    
        if (self.pi433MHz != None):
            self.pi433MHz.terminate()
            self.pi433MHz.join(5)
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
                sleep(LoopTime)
            if self.killer.kill_now:
                break   
        return self.killer.restart

    def GetLogger(self):
        logpath = "/var/log"
        LoggerPath = ""
        # first look in log path
        if os.path.exists(logpath):
            if os.access(logpath, os.W_OK):
                LoggerPath = os.path.join(logpath,LOG_FILENAME)
        if (not LoggerPath):
            # then look in home folder
            if os.access(os.path.expanduser('~'), os.W_OK):
                LoggerPath = os.path.join(os.path.expanduser('~'),LOG_FILENAME)
            else:
                print("Error opening logger, exit")
                exit(1) 
        return (LoggerPath)

    def GetDB(self):
        etcpath = "/etc/Domotion/"
        DBpath = ""
        # first look in etc
        if os.path.isfile(os.path.join(etcpath,DB_FILENAME)):
            DBpath = os.path.join(etcpath,DB_FILENAME)
        else:
            # then look in home folder
            if os.path.isfile(os.path.join(os.path.expanduser('~'),DB_FILENAME)):
                DBpath = os.path.join(os.path.expanduser('~'),DB_FILENAME)
            else:
                # look in local folder, hope we may write
                if os.path.isfile(os.path.join(".",DB_FILENAME)):
                    if os.access(os.path.join(".",DB_FILENAME), os.W_OK):
                        DBpath = os.path.join(".",DB_FILENAME)
                    else: 
                        self.logger.critical("No write access to DB file, exit")
                        exit(1)
                else:
                    self.logger.critical("No DB file found, exit")
                    exit(1)
        return (DBpath)

#########################################################
# Main function                                         #
#########################################################
if __name__ == '__main__':
    Debug = 0
    if (len(sys.argv)>1):
        if ("-h" in sys.argv):
            print "Domotion Home control and automation"
            print "Version: " + VERSION
            print ""
            print "Usage:"
            print "         Domotion <args>"
            print "         -h: help: this help file"
            print "         -d: default: run on port 5000 with no login (for debugging)"
            print "         -n: no-login: run with no login (for forgotten password)"
            print "         -v: version: print version information"
            exit(1)
        elif ('-v' in sys.argv):
            print "Version: " + VERSION
            exit(1)
        else:
            if  ('-n' in sys.argv):
                print "Option: no-login detected, running with no login"
                Debug = 1
            if  ('-d' in sys.argv):
                print "Option: default detected, running on port 5000 with no login"
                Debug = 2
    while (Domotion(Debug).run()):
        try:
            p = psutil.Process(os.getpid())
            for handler in p.get_open_files() + p.connections():
                os.close(handler.fd)
        except Exception, e:
            pass
        python = sys.executable
        os.execl(python, python, *sys.argv)
    