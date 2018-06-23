# -*- coding: utf-8 -*-
#########################################################
# SERVICE : appcommon.py                                #
#           Python common API for Domotion apps         #
#           Use this API with apps for proper working   #
#           I. Helwegen 2018                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
from time import sleep
from datetime import datetime
import locale
import signal
from bdaclient import bdaclient
import xml.etree.ElementTree as ET
import sys
import os
import logging
import logging.handlers
#########################################################

####################### GLOBALS #########################
LOG_MAXSIZE = 100*1024*1024

#########################################################
# Class : appcommon                                     #
#########################################################

class appcommon(Thread):
    def __init__(self, file):
        self.file = file
        self.doUpdate = True
        self.IntervalUpdate = False
        self.Startup = True
        self.retrytime = -1
        self.common = self._readCommonfromXML()
        self.counter = 0
        self.parameters = {}
        self.newparams = {}
        self.logger = logging.getLogger(self.getBaseName())
        if self.str2bool(self.common['verbose']):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.handlers.RotatingFileHandler(self._getLogger(), maxBytes=LOG_MAXSIZE, backupCount=5)
        # create console handler with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        logging.captureWarnings(True)
        locale.setlocale(locale.LC_TIME,'')
        strformat=("{} {}".format(locale.nl_langinfo(locale.D_FMT),locale.nl_langinfo(locale.T_FMT)))
        strformat=strformat.replace("%y", "%Y")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', strformat)
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.client=bdaclient(self.getBaseName(), self._update, url=self.common['url'], port=self.common['port'], server=self.common['server'], username=self.common['username'], password=self.common['password'])
        self.client.start()
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        self.start()

    def __del__(self):
        logging.shutdown()
        del self.mutex
        del self.term

    def init(self):
        raise NotImplementedError

    def loop(self):
        raise NotImplementedError

    def exit(self):
        raise NotImplementedError

    def callback(self):
        raise NotImplementedError

    def ismain(self):
        signal.signal(signal.SIGINT, self._signal)
        signal.signal(signal.SIGTERM, self._signal)
        signal.pause()

    def terminate(self):
        self.term.set()
        self.join()

        if (self.client != None):
            self.client.terminate()
            self.client.join(5)

    def _signal(self, signum, frame):
        self.terminate()

    def update(self):
        _doUpdate = self.doUpdate
        _done = False
        self.IntervalUpdate = False
        if (self.common['interval'] > 0):
            if self.Startup:
                self.Startup = False
                self.IntervalUpdate = True
                _done = True
            elif (self.counter >= int(self.common['interval'])):
                _doUpdate = True
                _done = True
                self.IntervalUpdate = True
                self.mutex.acquire()
                self.counter = 0
                self.mutex.release()
            else:
                self.mutex.acquire()
                self.counter += 1
                self.mutex.release()
        if (not _done) and (self.common['times'] != []):
            _time = datetime.now()
            currenttime = _time.hour*60 + _time.minute
            if (currenttime in self.common['times']) or (self.retrytime == currenttime):
                if (self.doUpdate == False):
                    self.doUpdate = True
                    _doUpdate = True  
                else:
                    _doUpdate = False 
            else:
                if (self.retrytime >= 0) and (self.retrytime < currenttime):
                    self.mutex.acquire()
                    self.retrytime = -1
                    self.mutex.release()
                    _doUpdate = False
                if (currenttime-1 in self.common['times']):
                    _doUpdate = False
                self.doUpdate = False
        elif (not _done):
            self.doUpdate = False
        return _doUpdate

    def isIntervalUpdate(self):
        return self.IntervalUpdate

    def tryAgainIn1Minute(self, interval):
        self.mutex.acquire()
        if interval:
            self.counter = int(self.common['interval']) - 60
        else:
            _time = datetime.now()
            self.retrytime = _time.hour*60 + _time.minute + 1
        self.mutex.release()

    def setparameters(self, params):
        self.mutex.acquire()
        self.newparams=params
        self.mutex.release()

    def run(self):
        update = False
        wasDisconnected = False
        self.init()

        while not self.term.isSet():
            self.loop()
            self.mutex.acquire()
            # to do: test server disconnected/ connected
            if self.newparams:
                if self.newparams != self.parameters:
                    self.parameters = self.newparams
                    update = True
                self.newparams = {}
            self.mutex.release()

            if update and self.client.isConnected():
                for key in self.parameters:
                    self.client.Send(key,self.parameters[key])
                update = False
            elif wasDisconnected and self.client.isConnected():
                wasDisconnected = False
                if self.parameters:
                    for key in self.parameters:
                        self.client.Send(key,self.parameters[key])
            else:
                if not self.client.isConnected():
                    wasDisconnected = True
                sleep(1)

        self.exit()

    def _tomod(self, times):
        returntimes=[]
        for time in times:
            data=time.split(":")
            if (len(data) == 2):
                returntimes.append(int(data[0])*60+int(data[1]))
        return returntimes

    def _update(self, data): # Callback function
        tag = None
        value = None
        if data[0]:
            tag = data[0]
        if data[1]:
            value = data[1]
        if self.callback:
            rtag, rvalue = self.callback(tag, value)
        else:
            rtag = None
            rvalue = None
        return rtag, rvalue

    def _getLogger(self):
        logpath = "/var/log"
        LoggerPath = ""
        logfile=self.getBaseName()+'.log'
        # first look in log path
        if os.path.exists(logpath):
            if os.access(logpath, os.W_OK):
                LoggerPath = os.path.join(logpath,logfile)
        if (not LoggerPath):
            # then look in home folder
            if os.access(os.path.expanduser('~'), os.W_OK):
                LoggerPath = os.path.join(os.path.expanduser('~'),logfile)
            else:
                print("Error opening logger, exit")
                exit(1) 
        return (LoggerPath)

    def _getXML(self):
        etcpath = "/etc/Domotion/"
        xmlfile=self.getBaseName()+'.xml'
        if os.path.isfile(os.path.join(etcpath,xmlfile)): # first look in etc
            xmlfile = os.path.join(etcpath,xmlfile)
        elif os.path.isfile(os.path.join(os.path.expanduser('~'),xmlfile)): # then look in home folder
                xmlfile = os.path.join(os.path.expanduser('~'),xmlfile)
        #else look in local folder, test later
               
        return (xmlfile)

    def getBaseName(self):
        return os.path.splitext(os.path.basename(self.file))[0]

    def _readCommonfromXML(self):
        commonread = False
        common = {}
        try:
            xmlfile=self._getXML()
            if os.path.isfile(xmlfile):
                tree = ET.parse(xmlfile)
                root = tree.getroot()
                commontag=root.find('common')
                if commontag != None:
                    tag=commontag.find('verbose')
                    if tag != None:
                        common['verbose']=tag.text
                    else:
                        common['verbose']=""
                    tag=commontag.find('server')
                    if tag != None:
                        common['server']=tag.text
                    else:
                        common['server']=""
                    tag=commontag.find('port')
                    if tag != None:
                        common['port']=tag.text
                    else:
                        common['port']=60004
                    tag=commontag.find('url')
                    if tag != None:
                        common['url']=tag.text
                    else:
                        common['url']="na"
                    tag=commontag.find('interval')
                    if tag != None:
                        common['interval']=tag.text
                    else:
                        common['interval']=0
                    tag=commontag.find('times')
                    if tag != None:
                        times = []
                        for child in tag:
                            if 'time' in child.tag:
                                times.append(child.text)  
                        common['times']=self._tomod(times)
                    else:
                        common['times']=[]
                    tag=commontag.find('username')
                    if tag != None:
                        common['username']=tag.text
                    else:
                        common['username']=""
                    tag=commontag.find('password')
                    if tag != None:
                        common['password']=tag.text
                    else:
                        common['password']=""
    
                    commonread = True
        except:
            pass
        if not commonread:
            common['server']=""
            common['port']=60004
            common['url']="na"
            common['interval']=0
            common['times']=[]
            common['username']=""
            common['password']=""

        return common

    def ReadAppParams(self):
        app = {}
        try:
            xmlfile=self._getXML()
            if os.path.isfile(xmlfile):
                tree = ET.parse(xmlfile)
                root = tree.getroot()
                apptag=root.find('app')
                app = self._getchilds(apptag)
        except:
            pass

        return app

    def _getchilds(self, tag):
        content = {}
        for child in tag:
            if child.getchildren() == []:
                content[child.tag] = child.text
            else:
                content[child.tag] = self._getchilds(child)
        return content

    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")