# -*- coding: utf-8 -*-
#########################################################
# SERVICE : db_settings                                 #
#           Reading and processing settings from db     #
#                                     for home control  #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from .sqlitedb import sqlitedb
from base64 import b64encode

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : db_settings                                   #
#########################################################

class db_settings(object):
    def __init__(self, app):
        self.app = app
        self.db=sqlitedb(self.app.common.GetDBPath())

    def __del__(self):
        del self.db

    def ReadSettings(self):
        return self._PrettyEditData()

    def EditSettings(self, id, result):
        value = {}
        retval=self.db.SearchValueFromColumn("settings", "format", "Id", id, False)
        if (retval):
            Format = retval[0][0]
        else:
            Format = ''
        retval=self.db.SearchValueFromColumn("settings", "restart", "Id", id, False)
        if (retval):
            Restart = retval[0][0]
        else:
            Restart = 0
        if (Format == 'BOOL'):
            if ((result['BoolValue'].lower() ==  'true') or (result['BoolValue'] == "1")):
                value['Value']="1"
            else:
                value['Value']="0"
        elif ('INT' in Format):
            value['Value']=result['IntValue']
        elif ('FLOAT' in Format):
            value['Value']=result['FloatValue']
        elif (Format == 'PSTRING'):
            if (result['PasswordValue1'] == result['PasswordValue2']):
                value['Value']=b64encode(result['PasswordValue1'].encode("utf-8")).decode("utf-8")
            else:
                value['Value']=""
        elif (Format == 'PDSTRING'):
            if (result['PasswordValue1'] == result['PasswordValue2']):
                if (len(result['PasswordValue1'])>0):
                    value['Value']=self.app.common.HashPass(result['PasswordValue1']).decode("utf-8")
                else:
                    value['Value']=""
            else:
                value['Value']=""
        else:
            value['Value']=result['StringValue']
        if (value):
            self.db.UpdateRow("settings", value, "Id", id)
        return Restart

    def BuildFormatDict(self):
        return dict(self.db.SelectColumnFromTable("settings", "Id,Format"))

    def _GetColumn(self,cols,name):
        i = 0
        retcol = -1
        for colname in cols:
            if (colname.lower() == name.lower()):
                retcol = i
            i += 1

        return retcol

    def _PrettyEditData(self):
        cols=self.db.GetColNames("settings")
        data=self.db.ReadTable("settings")

        format_col = self._GetColumn(cols,"format")
        value_col = self._GetColumn(cols,"value")
        newcols = cols[:value_col+1]
        newdata = []

        for row in data:
            if (row[format_col] == 'BOOL'):
                if (row[value_col] > 0):
                    _bool = ("True",)
                else:
                    _bool = ("False",)
                newrow = row[:value_col] + _bool
            elif (row[format_col] == 'PSTRING') or (row[format_col] == 'PDSTRING'):
                p = len(row[value_col])
                if (p>0):
                    _pwd = ("*" * 10,)
                else:
                    _pwd = ("",)
                newrow = row[:value_col] + _pwd
            else:
                newrow = row[:value_col+1]
            newdata.append(newrow)

        return newcols, newdata
