# -*- coding: utf-8 -*-
#########################################################
# SERVICE : scripts.py                                  #
#           Inferface for scripts handling for Domotion #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import logging
import glob
import os
import importlib
from .commandqueue import commandqueue
from .localaccess import localaccess
from frontend.domotion_scripts import domotion_scripts
#########################################################

####################### GLOBALS #########################
etcpath = "/etc/Domotion/"
scriptsfolder = "process"
scriptsext = "*.py"
classfunctions = ["getSensor", "setSensor", "getActuator", "setActuator", "log", "currentValue", "posEdge", "negEdge", "eitherEdge"]

#########################################################
# Class : scripts                                       #
#########################################################
class scripts(object):
    def __init__(self, commandqueue, localaccess):
        self.commandqueue = commandqueue
        self.localaccess = localaccess
        self.scriptspath = os.path.join(etcpath, scriptsfolder)
        self.logger = logging.getLogger('Domotion.process_scripts')
        self.logger.info("running")
        self.loadedScripts = {}

    def __del__(self):
        self.logger.info("finished")

    def run(self, filename):
        if filename:
            scriptclass = self._loadScript(filename)
            if scriptclass:
                self._runScript(filename, scriptclass)

    def update(self):
        for filename, scriptclass in self.loadedScripts.items():
            if scriptclass:
                del scriptclass
        self.loadedScripts = {}

    def set(self, filename, contents):
        retval = False
        if not contents:
            retval = self.delete(filename)
        else:
            full = self.dressScript(contents)
            if full:
                try:
                    pathExists = os.path.exists(self.scriptspath)
                    if not pathExists:
                        pathExists = self.addFolder()
                    if pathExists:
                        with open(os.path.join(self.scriptspath,self.addExt(filename)), "w") as f:
                            f.write(full)
                        retval = True
                except:
                    self.logger.error("Unable to write script: {}".format(filename))
            else:
                self.logger.error("Unable to build script: {}".format(filename))
        return retval

    def get(self, filename):
        contents = ""
        if self.exists(filename):
            full = ""
            try:
                with open(os.path.join(self.scriptspath,self.addExt(filename))) as f:
                    full = f.read()
            except:
                self.logger.error("Unable to read script: {}".format(filename))
            if full:
                contents = self.stripScript(full)
            if not contents:
                self.logger.error("Unable to parse script: {}".format(filename))
        else:
            contents = self.default()

        return contents

    def list(self):
        scriptslist = []
        if os.path.exists(self.scriptspath):
            files = glob.glob(os.path.join(self.scriptspath, scriptsext))
            for file in files:
                folder, name = os.path.split(file)
                if name:
                    scriptslist.append(self.removeExt(name))
        return scriptslist

    def exists(self, filename):
        return os.path.exists(os.path.join(self.scriptspath, self.addExt(filename)))

    def delete(self, filename):
        retval = False
        if self.exists(filename):
            try:
                os.remove(os.path.join(self.scriptspath, self.addExt(filename)))
                retval = True
            except:
                self.logger.error("Unable to delete script: {}".format(filename))
        return retval

    def addFolder(self):
        retval = False
        try:
            os.mkdir(self.scriptspath)
            os.chmod(self.scriptspath, 0o777)
            retval = True
        except:
            self.logger.error("Unable add scripts folder at /etc/Domotion/process")
        return retval

    def default(self):
        return """# Enter your scripts code here. Scripts here python3 based (only built-in code)
# Functions: getSensor(name, edge = currentValue), setSensor(name, value)
#            getActuator(name, edge = currentValue), setActuator(name, value)
#            log(logString)
# Edges:     currentValue, posEdge, negEdge, eitherEdge
if True:
    pass
"""

    def head(self):
        return """class procscript(object):
    def run(self):
        # Only modify your code below this point!!!
"""

    def removeExt(self, filename):
        return filename.replace(".py", "")

    def addExt(self, filename):
        return filename + ".py"

    def stripScript(self, full):
        lines = full.split("\n")
        headlines = self.head().split("\n")

        contentlines = []
        for line in lines:
            if not line in headlines:
                if line.startswith(" " * 8):
                    line = line[8:]
                line = self._removeSelfies(line)
                contentlines.append(line)

        return "\n".join(contentlines)

    def dressScript(self, contents):
        lines = contents.split("\n")
        headlines = self.head().split("\n")

        fulllines = headlines
        for line in lines:
            line = self._addSelfies(line)
            line = " " * 8 + line
            fulllines.append(line)

        full = "\n".join(fulllines)
        if not full.endswith("\n"):
            full = full + "\n"

        return full

    def _removeSelfies(self, line):
        for classfunction in classfunctions:
            # Do it twice to remove self.self. if coincidently typed
            line = line.replace("self." + classfunction, classfunction)
            line = line.replace("self." + classfunction, classfunction)
        return line

    def _addSelfies(self, line):
        for classfunction in classfunctions:
            # Remove self.self. if coincidently typed
            line = line.replace(classfunction, "self." + classfunction)
            line = line.replace("self.self.", "self.")
        return line

    def _loadScript(self, filename):
        scriptclass = None
        if filename in self.loadedScripts:
            scriptclass = self.loadedScripts[filename]
        else:
            if self.exists(filename):
                try:
                    spec = importlib.util.spec_from_file_location(filename, os.path.join(self.scriptspath, self.addExt(filename)))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    scriptclass = module.procscript()
                    Inheritclass = type('procscript', (domotion_scripts, object), module.procscript.__dict__.copy())
                    scriptclass.__class__ = Inheritclass
                    scriptclass.init(self.commandqueue, self.localaccess, filename)
                except Exception as e:
                    self.logger.error("Error in loading script: {}".format(filename))
                    self.logger.exception(e)
                    scriptclass = None #prevent running
                self.loadedScripts[filename] = scriptclass

        return scriptclass

    def _runScript(self, filename, scriptclass):
        try:
            if scriptclass:
                scriptclass.run()
                #self.logger.info("runned script: {}".format(filename))
        except Exception as e:
            self.logger.error("Error in running script: {}".format(filename))
            self.logger.exception(e)
            self.loadedScripts[filename] = None #prevent running
