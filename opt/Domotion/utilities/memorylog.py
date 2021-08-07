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
        self.rdpos={}
        self.mutex = None
        self._initmutex()
        self._setinit(size)

    def __del__(self):
        self._setdel()
        self._delmutex()

    def _setinit(self,size):
        self._acquire()
        self.wrpos=0
        self.addinstance()
        self.size=size
        self.Memory=[]
        self._release()

    def _setdel(self):
        self._acquire()
        del self.Memory
        self.Memory=[]
        self.wrpos=0
        self.rdpos.clear()
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

    def _format(self,s):
        # As python3 formatting differs from python2, we need to do something here
        sf = ''
        if len(s)>0:
            if s.endswith("\n"):
                sf =s
            else:
                sf = s + "\n"
        return(sf)

    def write(self,s):
        sf = self._format(s)
        if sf:
            self._acquire()
            if (self.size>0):
                if (self.wrpos>=self.size):
                    self.Memory.pop(0)
                    for key in self.rdpos:
                        if (self.rdpos[key]>0):
                            self.rdpos[key]-=1
            self.Memory.append(sf)
            self.wrpos=len(self.Memory)
            self._release()

    def writelines(self,sl):
        for s in sl:
            self.write(s)

    def readline(self,instance=0):
        strbuf=""
        self._acquire()
        oldpos=self.rdpos[instance]
        if (oldpos<self.wrpos):
            self.rdpos[instance]+=1
            strbuf=self.Memory[oldpos]
        self._release()
        return (strbuf)

    def readlines(self, instance=0):
        buf=[]
        self._acquire()
        oldpos=self.rdpos[instance]
        if (oldpos<self.wrpos):
            self.rdpos[instance]=self.wrpos
            buf=self.Memory[oldpos:]
        self._release()
        return (buf)

    def read(self, instance=0):
        return self.readline(instance)

    def getvalue(self, instance=0):
        self._acquire()
        self.rdpos[instance]=self.wrpos
        buf=self.Memory
        self._release()
        return (buf)

    def tell(self, instance=0):
        self._acquire()
        pos=(self.rdpos[instance])
        self._release()
        return (pos)

    def seek(self, pos, instance=0):
        self._acquire()
        if (pos>self.wrpos):
            self.rdpos[instance]=self.wrpos
        elif (pos<0):
            self.rdpos[instance]=0
        else:
            self.rdpos[instance]=pos
        self._release()

    def close(self):
        self._setdel()

    def addinstance(self):
        instance = 0
        if len(self.rdpos)>0:
            i=0
            keys = list(self.rdpos.keys())
            while instance == 0:
                if not i in keys:
                    instance = i
                i += 1

        self.rdpos[instance]=0
        return instance

    def removeinstance(self, instance):
        try:
            del self.rdpos[instance]
        except:
            pass
