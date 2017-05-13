# -*- coding: utf-8 -*-
#########################################################
# SERVICE : lircif.py                                   #
#           Python socket communication if for lirc     #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import os, os.path
import socket
from time import sleep
import logging

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : lircif                                        #
#########################################################
class lircif(object):
    def __init__(self):
        self.lirc_socket_path="/var/run/lirc/lircd"
        self.sock = None
        self.logger = logging.getLogger('Domotion.Lircif')
        
    def __del__(self):
        self.close()

    def test(self):
        return os.path.exists(self.lirc_socket_path)

    def init(self,timeout=None, path=None):
        sockerror = False
        if (self.sock):
            self.logger.warning("Socket already exists, init already done")
            return True
        if (not path):
            path=self.lirc_socket_path
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(path)
            self.sock.settimeout(timeout)
        except Exception, e:
            self.logger.error("Socket connection error: %s"%e)
            self.sock = None
            sockerror = True
        return (not sockerror)

    def close(self):
        if (self.sock):
            self.sock.close()
            self.sock = None
        return

    def ReadKey(self):
        sockerror = False
        device = None
        key = None
        repeat = False
        if (not self.sock):
            self.logger.warning("Socket not initialized")
            sockerror = True
            return sockerror,device,key,repeat
        try:
            buf = self.sock.recv(128)
            if (buf != None):
                device,key,repeat = self._DecodeBuf(buf)
        except socket.timeout:
            pass
        except socket.error, e:
            self.logger.error("Socket connection error: %s"%e)
            sockerror = True

        return sockerror,device,key,repeat

    def WriteKey(self,remote,key,timems=0):
        sockerror = False
        success=-2
        if (not self.sock):
            self.logger.warning("Socket not initialized")
            sockerror = True
            return sockerror,success
        if (timems<=0):
            command="SEND_ONCE %s %s\n"%(remote, key)
            success=self._lirc_send_command(command)
        else:
            command="SEND_START %s %s\n"%(remote, key)
            success=self._lirc_send_command(command)

            sleep(timems/1000)

            command="SEND_STOP %s %s\n"%(remote, key)
            success=self._lirc_send_command(command)
        sockerror = (success<-1)
        return sockerror,success

    def _DecodeBuf(self,buf):
        spbuf = buf.strip().split(' ')
        try:
            if int(spbuf[1])>0:
                repeat = True
            else:
                repeat = False
        except:
            spbuf[3]=None
            spbuf[2]=None
            repeat=False
        return spbuf[3],spbuf[2],repeat

    def _lirc_send_command(self, command):
        status = -1
        try:
            sent = self.sock.send(command)
        except socket.error, e:
            self.logger.error("Socket connection error: %s"%e)
            status = -2
            return status
    
        finished=False
        state=0
        nread=0
        while (not finished):
            buf = None
            try:
                buf = self.sock.recv(128)
            except socket.timeout:
                pass
            except socket.error, e:
                self.logger.error("Socket connection error: %s"%e)
                status = -2
                return status     
    
            if (buf != None):
                for bufl in buf.split('\n'):
                    if (state == 0): # BEGIN
                        if ("BEGIN" in bufl.upper()):
                            state = 1
                    elif (state == 1): # MESSAGE
                        if (bufl.upper().strip() == command.upper().strip()):
                            state = 2
                        else:
                            state = 0
                    elif (state == 2): # STATUS
                        if ("SUCCESS" in bufl.upper()):    
                            status = sent
                        elif ("END" in bufl.upper()):
                            status = 0
                            finished = True
                            break
                        elif ("ERROR" in bufl.upper()):
                            status = -1
                        else:
                            status = -1
                            finished = True
                            break
                        state = 3 
                    elif (state == 3): # DATA
                        if ("END" in bufl.upper()):
                            finished = True
                            break
                        elif ("DATA" in bufl.upper()):
                            state = 4
                        else:
                            status = -1
                            finished = True
                            break
                    elif (state == 4): # P_N
                        data_n=int(bufl)
                        if (bufl == None):
                            status = -1
                            finished = True
                            break
                        if (data_n == 0):
                            state = 6
                        else:
                            state = 5               
                    elif (state == 5): # P_DATA_N
                        nread+=len(bufl)
                        if (nread >= data_n):
                            state = 6
                    elif (state == 6): # END
                        if ("END" in buf.upper()):
                            finished = True
                            break
                        else:
                            status = -1
                            finished = True
                            break
                    else:
                        status = -1
                        finished = True
                        break
    
        return status   