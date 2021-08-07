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
from engine.commandqueue import commandqueue
from engine.engine import engine
from engine.localaccess import localaccess
from engine.localaccess import AppKiller
from engine.scripts import scripts
from utilities.memorylog import memorylog
from hardware.hw_lirc import lirc
from hardware.hw_pi433MHz import pi433MHz
from hardware.hw_domoticz import domoticz_if
from hardware.hw_url import url
from hardware.hw_pigpio import gpio
from hardware.hw_mqtt import mqtt
from hardware.hw_script import script
from frontend.domoticz_frontend import domoticz_frontend
from frontend.domoticz_api import domoticz_api
from frontend.webserveraccess import webserveraccess
import sys
from getopt import getopt, GetoptError
import os
import psutil

####################### GLOBALS #########################
LOG_FILENAME = 'Domotion.log'
LOG_MAXSIZE = 100*1024*1024
DB_FILENAME = "Domotion.db"
VERSION = "1.31"
LoopTime = 0.1
RestartSleepTime = 2
LogMemory = 100

#########################################################
# Class : Domotion                                      #
#########################################################
class Domotion(object):
    def __init__(self):
        try:
            self.logger = logging.getLogger('Domotion')
            self.logger.setLevel(logging.INFO)
            # create file handler which logs even debug messages
            fh = logging.handlers.RotatingFileHandler(self.GetLogger(), maxBytes=LOG_MAXSIZE, backupCount=5)
            # create console handler with a higher log level
            ch = logging.StreamHandler(sys.stdout)
            # create memory handler for printing in web interfaceset to 10 kB > 1000 lines
            self.memorylog=memorylog(LogMemory)
            mh = logging.StreamHandler(self.memorylog)
            # create formatter and add it to the handlers
            # add the handlers to the logger
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
            self.logger.addHandler(mh)
            logging.captureWarnings(True)
            self.localaccess = localaccess(self.GetDB())
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', self.localaccess.datetime())
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            mh.setFormatter(formatter)
            self.logger.info("Starting Domotion")
            self.killer = AppKiller()

            #test DB and update if required
            result = self.localaccess.UpdateDB(VERSION)
            if (result != ""):
                self.logger.info("Database updated to latest version: %s" % result)

            #start queue, load scripts and engine
            self.commandqueue=commandqueue()
            self.scripts = scripts(self.commandqueue, self.localaccess)
            self.engine = engine(self.commandqueue, self.localaccess, self.scripts, LoopTime)

            #start domoticz api (even when no domoticz connection is made)
            self.domoticz_api = domoticz_api(self.localaccess)

            #start hardware
            if (self.localaccess.GetSetting('Pi433MHz')):
                self.pi433MHz = pi433MHz(self.commandqueue)
                self.pi433MHz.start()
            else:
                self.logger.info("Pi433MHz hardware disabled")
                self.pi433MHz = None

            if (self.localaccess.GetSetting('LIRC')):
                self.lirc = lirc(self.commandqueue)
                self.lirc.start()
            else:
                self.logger.info("LIRC interface disabled")
                self.lirc = None

            if (self.localaccess.GetSetting('Domoticz')):
                self.domoticz_if = domoticz_if(self.commandqueue, self.localaccess, self.domoticz_api)
                self.domoticz_if.start()
            else:
                self.logger.info("Domoticz interface disabled")
                self.domoticz_if = None

            if (self.localaccess.GetSetting('URL')):
                self.url = url(self.commandqueue, self.localaccess, self.memorylog)
                self.url.start()
            else:
                self.logger.info("URL interface disabled")
                self.url = None

            if (self.localaccess.GetSetting('GPIO')):
                self.gpio = gpio(self.commandqueue)
                self.gpio.start()
            else:
                self.logger.info("PiGPIO interface disabled")
                self.gpio = None

            if (self.localaccess.GetSetting('MQTT')):
                self.mqtt = mqtt(self.commandqueue, self.localaccess)
                self.mqtt.start()
            else:
                self.logger.info("MQTT interface disabled")
                self.mqtt = None

            self.script = script()

            #start frontend
            if (self.localaccess.GetSetting('Domoticz_frontend')):
                self.domoticz_frontend = domoticz_frontend(self.commandqueue, self.localaccess, self.domoticz_api)
                self.domoticz_frontend.start()
            else:
                self.logger.info("Domoticz frontend disabled")
                self.domoticz_frontend = None

            #start webapp
            self.webserveraccess = webserveraccess(self.commandqueue, self.localaccess, self.killer, self.memorylog, self.scripts, port=self.localaccess.GetSetting('DomoWeb_port'))
            self.webserveraccess.start()

            self.engine.instances(self.domoticz_api, self.domoticz_frontend, self.gpio, self.url, self.domoticz_if, self.lirc, self.pi433MHz, self.script, self.mqtt)
            self.engine.DomoticzMessenger(1)
        except Exception as e:
            if (self.logger):
                self.logger.exception(e)
            else:
                print(e)

    def __del__(self):
        try:
            self.engine.DomoticzMessenger(0)

            #stop webappserveraccess
            if (self.webserveraccess != None):
                self.webserveraccess.terminate()
                self.webserveraccess.join(5)
                del self.webserveraccess

            #stop frontend
            if (self.domoticz_frontend != None):
                self.domoticz_frontend.terminate()
                self.domoticz_frontend.join(5)
                del self.domoticz_frontend

            #stop hardware

            del self.script

            if (self.mqtt != None):
                self.mqtt.terminate()
                del self.mqtt

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
            del self.localaccess
        except Exception as e:
            if (self.logger):
                self.logger.exception(e)
            else:
                print(e)

    def run(self):
        try:
            while(True):
                if (not self.engine.loop()):
                    sleep(LoopTime)
                if self.killer.kill_now:
                    break
        except Exception as e:
            self.logger.exception(e)

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
                try:
                    sFile = os.path.abspath(sys.modules['__main__'].__file__)
                except:
                    sFile = "."
                if os.path.isfile(os.path.join(os.path.dirname(sFile),DB_FILENAME)):
                    if os.access(os.path.join(os.path.dirname(sFile),DB_FILENAME), os.W_OK):
                        DBpath = os.path.join(os.path.dirname(sFile),DB_FILENAME)
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
def DomotionMain(argv):
    try:
        opts, args = getopt(argv,"hv",["help","version"])
    except GetoptError:
        print("Domotion Home control and automation")
        print("Version: " + VERSION)
        print(" ")
        print("Enter 'Domotion -h' for help")
        exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Domotion Home control and automation")
            print("Version: " + VERSION)
            print(" ")
            print("Usage:")
            print("         Domotion <args>")
            print("         -h, --help: this help file")
            print("         -v, --version: print version information")
            exit()
        elif opt in ("-v", "--version"):
            print("Version: " + VERSION)
            exit()

    while (Domotion().run()):
        try:
            p = psutil.Process(os.getpid())
            for handler in p.get_open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            pass
        sleep(RestartSleepTime)
        python = sys.executable
        os.execl(python, python, *sys.argv)

#########################################################
if __name__ == "__main__":
    DomotionMain(sys.argv[1:])
