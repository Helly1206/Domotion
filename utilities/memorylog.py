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
    Memory=[]
    size=0
    wrpos=0
    rdpos=0
    mutex = None

    def __init__(self, size=0):
        self._initmutex()
        self._setinit(size)

    def __del__(self):
        self._setdel()
        self._delmutex()

    @classmethod
    def _setinit(cls,size):
        cls._acquire()
        cls.wrpos=0
        cls.rdpos=0
        cls.size=size
        cls.Memory=[]
        cls._release()

    @classmethod
    def _setdel(cls):
        cls._acquire()
        del cls.Memory
        cls.Memory=[]
        cls.wrpos=0
        cls.rdpos=0
        cls._release()

    @classmethod
    def _initmutex(cls):
        cls.mutex = Lock()

    @classmethod
    def _delmutex(cls):
        del cls.mutex

    @classmethod
    def _acquire(cls):
        if (cls.mutex):
            cls.mutex.acquire()
            return True
        else:
            return False

    @classmethod
    def _release(cls):
        if (cls.mutex):
            cls.mutex.release()
            return True
        else:
            return False

    @classmethod
    def write(cls,s):
        cls._acquire()
        if (cls.size>0):
            if (cls.wrpos>=cls.size):
                cls.Memory.pop(0)
                if (cls.rdpos>0):
                    cls.rdpos-=1
        cls.Memory.append(s)
        cls.wrpos=len(cls.Memory)
        cls._release()

    @classmethod
    def writelines(cls,sl):
        for s in sl:
            cls.write(s)

    @classmethod
    def readline(cls):
        strbuf=""
        cls._acquire()
        oldpos=cls.rdpos
        if (oldpos<cls.wrpos):
            cls.rdpos+=1
            strbuf=cls.Memory[oldpos]
        cls._release()
        return (strbuf)

    @classmethod
    def readlines(cls):
        buf=[]
        cls._acquire()
        oldpos=cls.rdpos
        if (oldpos<cls.wrpos):
            cls.rdpos=cls.wrpos
            buf=cls.Memory[oldpos:]
        cls._release()
        return (buf)

    @classmethod
    def read(cls):
        return cls.readline()

    @classmethod
    def getvalue(cls):
        cls._acquire()
        cls.rdpos=cls.wrpos
        buf=''.join(cls.Memory)
        cls._release()
        return (buf)

    @classmethod
    def tell(cls):
        cls._acquire()
        pos=(cls.rdpos)
        cls._release()
        return (pos)

    @classmethod
    def seek(cls, pos):
        cls._acquire()
        if (pos>cls.wrpos):
            cls.rdpos=cls.wrpos
        elif (pos<0):
            cls.rdpos=0
        else:
            cls.rdpos=pos
        cls._release()

    @classmethod
    def close(cls): 
        cls._setdel()   
