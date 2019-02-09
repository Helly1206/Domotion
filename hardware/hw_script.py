# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_script.py                                #
#           Python script handling for Domotion         #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import logging
import os
import subprocess
from time import sleep
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
retrytime = 10 / sleeptime # test every 10s
retries = 10

#########################################################
# Class : hw_script                                     #
#########################################################
class script(object):
    def __init__(self):
        self.logger = logging.getLogger('Domotion.Script')
        self.scripts = {}
        self.logger.info("running")
        
    def __del__(self):
        del self.scripts
        self.logger.info("finished")

    def execute(self, device, key):
        success = True

        if not self._test_running(device):
            if not self._run_script(device, key):
                self.logger.warning("Script '%s' not found"%device)
        else:
            self.logger.info("Script '%s' not started, another instance is still running"%device)

        return success

    def _test_running(self, device):
        running = False
        if device in list(self.scripts.keys()):
            # script was running
            if self.scripts[device].poll() != None:
                # script finished, so remove
                self._del_script(device)
            else:
                # script is still running
                running = True
        return running

    def _add_script(self, device, proc):
        self.scripts[device] = proc
        return

    def _del_script(self, device):
        if device in list(self.scripts.keys()):
            del self.scripts[device]

        return

    def _get_loc(self, file):
        etcpath = "/etc/Domotion/"
        scriptfolder = "scripts"
        location = ""
        # first look in etc
        fpath = os.path.join(etcpath, scriptfolder, file)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            location = fpath
        else:
            # look in local folder
            fpath = os.path.join(".", scriptfolder, file)
            if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
                location = fpath
        
        return (location)

    def _run_script(self, device, key):
        retval = False
        
        loc = self._get_loc(device)
        try:
            if loc != "":
                proc = subprocess.Popen([loc, key])
                self._add_script(device, proc)
                retval = True
        except:
            pass
        return retval
