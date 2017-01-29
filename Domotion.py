import os
import thread
from webif import webapp

if __name__ == '__main__':
    try:
        thread.start_new_thread(webapp, ( ))
    except:
        print "ERROR Creating thread"

    while(1):
        pass
    