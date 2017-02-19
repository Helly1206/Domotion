# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_test.py                                  #
#           Python test handling for Domotion           #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event
import logging
from time import sleep

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : hw_lirc                                       #
#########################################################
class test(Thread):
    def __init__(self, commandqueue):
    	self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Test')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        
    def __del__(self):
        self.logger.info("finished")

    def terminate(self):
    		self.term.set()

    def run(self):
        self.logger.info("running")
        while (not self.term.isSet()):
        	sleep (2)
        	if (self.commandqueue):
        		self.commandqueue.put_device("test","MyDevice","KEY_1",0)
        self.logger.info("terminating")

#sock=init(lirc_socket_path,0.1)

#print WriteKey(sock,'/etc/lirc/lircd.conf','KEY_9')
    
#while (True):
#    buf,repeat = ReadKey(sock)
#    if (buf != None):
#        if (not repeat):
#            print(buf)

#close(sock)