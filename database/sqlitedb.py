# -*- coding: utf-8 -*-
#########################################################
# SERVICE : sqlitedb.py                                 #
#           Accessing the sqlite db for home control    #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################

import sqlite3

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : sqlitedb                                      #
#########################################################
class sqlitedb(object):
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath, check_same_thread=False)
    def __del__(self):
        # Closing the connection to the database file
        self.conn.close()

    def GetColNames(self, table_name):
        #this works beautifully given that you know the table name
        c = self.conn.cursor()
        c.execute("SELECT * FROM {tn}".format(tn=table_name))
        return [member[0] for member in c.description]

    def ReadTable(self, table_name):
        c = self.conn.cursor()
        c.execute("SELECT * FROM {tn}".format(tn=table_name))
        return c.fetchall()        

    def SearchTable(self, table_name, field, searchdata, like=True):
        c = self.conn.cursor()
        # like makes searching slower. Set false if you require speed.
        if like:
            c.execute("SELECT * FROM {tn} WHERE {fn} LIKE '{sd}'".format(tn=table_name, fn=field, sd=searchdata))
        else:
            c.execute("SELECT * FROM {tn} WHERE {fn}='{sd}'".format(tn=table_name, fn=field, sd=searchdata))
        return c.fetchall()

    def SearchTableMultiple(self, table_name, column, searchdict, like=True):
        searchdata=""
        c = self.conn.cursor()
        for field in searchdict:
            if like:
                searchdata += field + " LIKE '" + searchdict[field] + "' AND "
            else:
                searchdata += field + "='" + searchdict[field] + "' AND "
        searchdata = searchdata[:-5]

        c.execute("SELECT {cl} FROM {tn} WHERE {sd}".format(cl=column, tn=table_name, sd=searchdata))
        return c.fetchall()

    def SelectColumnFromTable(self, table_name, column):
        c = self.conn.cursor()
        c.execute("SELECT {cl} from {tn}".format(cl=column, tn=table_name))
        return c.fetchall()

    def SearchValueFromColumn(self, table_name, column, field, searchdata, like=True):
        c = self.conn.cursor()
        # like makes searching slower. Set false if you require speed.
        if like:
            c.execute("SELECT {cl} FROM {tn} WHERE {fn} LIKE '{sd}'".format(cl=column, tn=table_name, fn=field, sd=searchdata))
        else:
            c.execute("SELECT {cl} FROM {tn} WHERE {fn}='{sd}'".format(cl=column, tn=table_name, fn=field, sd=searchdata))
        return c.fetchall()

    def ClearTable(self, table_name):
        c = self.conn.cursor()
        c.execute("DELETE FROM {tn}".format(tn=table_name))
        self.conn.commit()
        return

    def ClearDB(self):
        self.ClearTable(ACTUATORS)
        self.ClearTable(COMBINERS)
        self.ClearTable(DEPENDENCIES)
        self.ClearTable(SENSORS)
        self.ClearTable(TIMERS)
        #do not clear types, only if add types later?
        #self.ClearTable(TYPES)

    def AddRow(self, table_name, rowdict):
        names = ""
        values = ""
        c = self.conn.cursor()

        for key in rowdict:
            names += key + ", "
            values += "'" + rowdict[key] + "', "
        names = "(" + names[:-2] + ")"
        values = "(" + values[:-2] + ")"

        c.execute("INSERT INTO {tn} {nm} VALUES {vl}".format(tn=table_name,nm=names, vl=values))
        self.conn.commit()

        return (c.lastrowid)

    def DeleteRow(self, table_name, field, fieldvalue):
        c = self.conn.cursor()
        c.execute("DELETE FROM {tn} WHERE {fn}='{sd}'".format(tn=table_name, fn=field, sd=fieldvalue))
        self.conn.commit()
        return

    def UpdateRow(self, table_name, rowdict, field, fieldvalue):
        columns = ""
        c = self.conn.cursor()

        for key in rowdict:
            columns += key + " = '" + rowdict[key] + "', "
        columns = columns[:-2]

        c.execute("UPDATE {tn} SET {cl} WHERE {fn}='{sd}'".format(tn=table_name, cl=columns, fn=field, sd=fieldvalue))
        self.conn.commit()
        return

