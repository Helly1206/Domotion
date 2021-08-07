# -*- coding: utf-8 -*-
#########################################################
# SERVICE : db_webread                                  #
#           Reading and processing db for web app       #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from .sqlitedb import sqlitedb

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : db_webread                                    #
#########################################################

class db_webread(object):
    def __init__(self, dbpath):
        self.db=sqlitedb(dbpath)

    def __del__(self):
        del self.db

    def GetSetting(self, Setting):
        vals=self.db.SearchTable("settings", "Parameter", Setting, False)
        if vals:
            return vals[0][3],vals[0][4]
        else:
            return None,None

    