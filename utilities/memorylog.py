# -*- coding: utf-8 -*-
#########################################################
# SERVICE : memorylog.py                                #
#           Python allocate a memory stream for logging #
#           with FIFO properties                        #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Lock
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : memorylog                                     #
#########################################################

class memorylog(object):
    def __init__(self, size=0):
        self.Memory=[]
        self.size=0
        self.wrpos=0
        self.rdpos=0
        self.mutex = None
        self._initmutex()
        self._setinit(size)

    def __del__(self):
        self._setdel()
        self._delmutex()

    def _setinit(self,size):
        self._acquire()
        self.wrpos=0
        self.rdpos=0
        self.size=size
        self.Memory=[]
        self._release()

    def _setdel(self):
        self._acquire()
        del self.Memory
        self.Memory=[]
        self.wrpos=0
        self.rdpos=0
        self._release()

    def _initmutex(self):
        self.mutex = Lock()

    def _delmutex(self):
        del self.mutex

    def _acquire(self):
        if (self.mutex):
            self.mutex.acquire()
            return True
        else:
            return False

    def _release(self):
        if (self.mutex):
            self.mutex.release()
            return True
        else:
            return False

    def write(self,s):
        self._acquire()
        if (self.size>0):
            if (self.wrpos>=self.size):
                self.Memory.pop(0)
                if (self.rdpos>0):
                    self.rdpos-=1
        self.Memory.append(s)
        self.wrpos=len(self.Memory)
        self._release()

    def writelines(self,sl):
        for s in sl:
            self.write(s)

    def readline(self):
        strbuf=""
        self._acquire()
        oldpos=self.rdpos
        if (oldpos<self.wrpos):
            self.rdpos+=1
            strbuf=self.Memory[oldpos]
        self._release()
        return (strbuf)

    def readlines(self):
        buf=[]
        self._acquire()
        oldpos=self.rdpos
        if (oldpos<self.wrpos):
            self.rdpos=self.wrpos
            buf=self.Memory[oldpos:]
        self._release()
        return (buf)

    def read(self):
        return self.readline()

    def getvalue(self):
        self._acquire()
        self.rdpos=self.wrpos
        buf=''.join(self.Memory)
        self._release()
        return (buf)

    def tell(self):
        self._acquire()
        pos=(self.rdpos)
        self._release()
        return (pos)

    def seek(self, pos):
        self._acquire()
        if (pos>self.wrpos):
            self.rdpos=self.wrpos
        elif (pos<0):
            self.rdpos=0
        else:
            self.rdpos=pos
        self._release()

    def close(self): 
        self._setdel()   
