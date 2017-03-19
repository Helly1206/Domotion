import sys
import os
import shutil

runpath = "/run"
runpath2 = "/run/user"
filename = "DomotionRetainer.dat"
etcpath = "/etc/Domotion/"

def FindNVLocRead():
    NVpath = ""
    # first look in etc
    if os.path.isfile(os.path.join(etcpath,filename)):
        NVpath = os.path.join(etcpath,filename)
    else:
        # then look in home folder
        if os.path.isfile(os.path.join(os.path.expanduser('~'),filename)):
            NVpath = os.path.join(os.path.expanduser('~'),filename)
        else:
            # look in local folder, hope we may write
            if os.path.isfile(os.path.join(".",filename)):
                NVpath = os.path.join(".",filename)
            else:
                print("No NON volatile file found, exit")
                exit(1)
    return (NVpath)

def FindNVLocWrite():
    NVpath = ""
    # first look in etc
    if os.access(etcpath, os.W_OK):
        NVpath = os.path.join(etcpath,filename)
    else:
        # then look in home folder
        if os.access(os.path.expanduser('~'), os.W_OK):
            NVpath = os.path.join(os.path.expanduser('~'),filename)
        else:
            # look in local folder, hope we may write
            if os.access(".", os.W_OK):
                NVpath = os.path.join(".",filename)
            else:
                print("No valid path for NON volatile file found, exit")
                exit(1)
    return (NVpath)

def FindVLocWrite():
    Vpath = ""

    userid = os.getuid()
    if (userid == 0):
        destpath = runpath
    else:
        destpath = os.path.join(runpath2, str(userid))

    if os.path.exists(destpath):
        if os.access(destpath, os.W_OK):
            Vpath = os.path.join(destpath, filename)
        else:
            print("No valid path for volatile file found, exit")
            exit(1)
    return (Vpath)        

def FindVLocRead():
    Vpath = ""

    userid = os.getuid()
    if (userid == 0):
        destpath = runpath
    else:
        destpath = os.path.join(runpath2, str(userid))

    if os.path.exists(destpath):
        if os.access(destpath, os.W_OK):
            retainerpath = os.path.join(destpath, filename)
            if os.path.isfile(retainerpath):
                Vpath = retainerpath
            else:
                print("No volatile file found, exit")
                exit(1)
    return (Vpath)                  

def MoveBack():
    print ("Move from '" + FindNVLocRead() + "' to '" + FindVLocWrite() + "'")
    shutil.move(FindNVLocRead(), FindVLocWrite())

def MoveForward():
    print ("Move from '" + FindVLocRead() + "' to '" + FindNVLocWrite() + "'")
    shutil.move(FindVLocRead(), FindNVLocWrite())

if __name__ == '__main__':
    if (len(sys.argv)>1):
        if (('-b' in sys.argv) or ('--back' in sys.argv)):
            MoveBack()
            exit(0)
        if (('-f' in sys.argv) or ('--forward' in sys.argv)):
            MoveForward()
            exit(0)
    print "Domotion Home control and automation, Retainer move tool"
    print ""
    print "Usage:"
    print "         RetainerMove <args>"
    print "         -b: move back to it's desired volatile location (when starting)"
    print "         -f: move forward to non volatile location (when shutting down)"
    exit(1)
