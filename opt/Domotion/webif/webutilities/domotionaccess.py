# -*- coding: utf-8 -*-
#########################################################
# SERVICE : domotionaccess.py                           #
#           Python communication functions for web app  #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import socket
from json import dumps, loads
from struct import pack, unpack
from threading import Timer

TIMEOUT=300.0

class domotionaccess(object):
    _functions = {"None": 0, "SetStatusBusy": 1, "Callback": 2, "BWAset": 3, "BWAget": 4, "Reboot": 5,
                  "Shutdown": 6, "RestartApp": 7, "RestartAll": 8, "LogReadLines": 9, "LogGetLog": 10,
                  "PutValue": 11, "GetActuatorValues": 12, "GetSensorValues": 13, "GetTimerValues": 14,
                  "GetSunRiseSetMod": 15, "SetTimer": 16, "GetToday": 17, "BWAgetall": 18, "BWAgetinfo": 19,
                  "ScriptsList": 20, "GetScript": 21, "SetScript": 22}

    def __init__(self, port=10000):
        self.Timer = None
        self.bufsize = 1024
        self.server_address = ('localhost', port)
        self.connected = False
        self.initsock()

    def __del__(self):
        if (self.sock):
            self.sock.close()
            self.connected = False

    def initsock(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO, pack('ll', 5, 0))
            self.sock.connect(self.server_address)
            # Check communication with Domotion server
            data = loads(self.receive(self.sock))
            if data:
                if (data != "Domotion"):
                    if (self.sock):
                        self.sock.close()
                        self.connected = False
                    print("# Error: Incorrect socket")
                else:
                    print("# Connected to Domotion server on %s, port %d" % (self.server_address[0], self.server_address[1]))
                    self.connected = True
            else:
                if (self.sock):
                    self.sock.close()
                    self.connected = False
                print("# Error: Socket doesn't introduce itself")
        except:
            if (self.sock):
                self.sock.close()
                self.connected = False
                print("# Error: Trying to connect to socket")

        return self.connected

    def closesock(self):
        if (self.sock):
            self.sock.close()
            self.connected = False
            print("# Closing connection to Domotion server on %s, port %d" % (self.server_address[0], self.server_address[1]))

        return self.connected

    def Call(self, function, *arguments):
        error = 0
        argout = []

        self.FireTimer()
        if (not self.connected):
            if (not self.initsock()):
                argout = self.getdummyargout(function)
                error = 503 # Service unavailable
                if (argout):
                    return error, argout
                else:
                    return error

        message = dumps((self._functions[function],arguments))
        self.flush(self.sock)
        success = self.send(self.sock, message)
        if (success):
            data = self.receive(self.sock)
            if data:
                returndata = loads(data)
                #print returndata
                if (len(returndata)>=1):
                    if returndata[0]:
                        argout = self.getdummyargout(function)
                        error=500 # Internal server error
                if (len(returndata)>=2):
                    if (returndata[1] != self._functions[function]):
                        argout = self.getdummyargout(function)
                        error=500 # Internal server error
                if (len(returndata)>=3):
                    argout=returndata[2]
            else:
                argout = self.getdummyargout(function)
                error = 504 # Timeout
                self.closesock()
        else:
            argout = self.getdummyargout(function)
            error = 503 # Service unavailable
            self.closesock()

        if (argout != None) and (argout != []):
            return error, argout
        else:
            return error

    def getdummyargout(self, function):
        argout = []
        fn = self._functions[function]

        if (fn == 3): #"set"): #basicwebaccess
            argout = "!!!"
        elif (fn == 4): #"get"): #basicwebaccess
            argout = "!!!"
        elif (fn == 9): #"readlines"): #memorylog
            argout = "!!!"
        elif (fn == 10): #"getvalue"): #memorylog
            argout = "!!!"
        elif (fn == 11): # put_id2: commandqueue
            #commandqueue.put_id2("None", int(key), ivalue, (tableid == "controls"))
            argout = 1
        elif (fn == 12): #"GetActuatorValues"): #localaccess
            argout = {0, 0, 0, 0, 0}
        elif (fn == 13): #"GetSensorValues"): #localaccess
            argout = {0, 0, 0, 0, 0}
        elif (fn == 14): #"GettimerValues"): #localaccess
            argout = {0, 0, 0, 0, 0}
        elif (fn == 15): #"GetSunRiseSetMod"): #localaccess
            argout = (0, 0)
        elif (fn == 16): #"SetTimer"): #localaccess
            argout = 1
        elif (fn == 17): #"GetToday"): #localaccess
            argout = 1
        elif (fn == 18): #"getall"): #basicwebaccess
            argout = "!!!"
        elif (fn == 19): #"getinfo"): #basicwebaccess
            argout = "!!!"
        elif (fn == 20): #ScriptsList #scripts
            argout = []
        elif (fn == 21): #GetScript #scripts
            argout = "!!!"
        elif (fn == 22): #SetScript #scripts
            argout = 1

        return argout

    def flush(self, sock):
        try:
            sock.setblocking(0)
        except:
            pass
        try:
            while len(sock.recv(self.bufsize)):
                pass
        except:
            pass
        try:
            sock.setblocking(1)
        except:
            pass

    def receive(self, sock):
        try:
            raw_msglen = self.receivevalue(sock, 4)
            if not raw_msglen:
                return None
            msglen = unpack('>I', raw_msglen)[0]
            # Read the message data
            return self.receivevalue(sock, msglen).decode("utf-8")
        except:
            return None

    def receivevalue(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            if (n- len(data) > self.bufsize):
                packet = sock.recv(self.bufsize)
            else:
                packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send(self, sock, arg):
        try:
            msg = pack('>I', len(arg)) + bytes(arg,"utf-8")
            sock.sendall(msg)
            return True
        except:
            return False

    def FireTimer(self):
        self.CancelTimer()
        self.Timer = Timer(TIMEOUT, self.OnTimer)
        self.Timer.start()

    def CancelTimer(self):
        if (self.Timer != None):
            self.Timer.cancel()
            del self.Timer
            self.Timer = None

    def OnTimer(self):
        self.CancelTimer()
        self.closesock()
