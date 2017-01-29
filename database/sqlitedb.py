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
        self.conn = sqlite3.connect(dbpath)
        self.c = self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        # Closing the connection to the database file
        self.conn.close()

    def GetColNames(self, table_name):
        #this works beautifully given that you know the table name
        self.c.execute("SELECT * FROM {tn}".format(tn=table_name))
        return [member[0] for member in self.c.description]

    def ReadTable(self, table_name):
        self.c.execute("SELECT * FROM {tn}".format(tn=table_name))
        return self.c.fetchall()        

    def SearchTable(self, table_name, field, searchdata, like=True):
        # like makes searching slower. Set false if you require speed.
        if like:
            self.c.execute("SELECT * FROM {tn} WHERE {fn} LIKE '{sd}'".format(tn=table_name, fn=field, sd=searchdata))
        else:
            self.c.execute("SELECT * FROM {tn} WHERE {fn}='{sd}'".format(tn=table_name, fn=field, sd=searchdata))
        return self.c.fetchall()

    def SearchTableMultiple(self, table_name, column, searchdict, like=True):
        searchdata=""
        for field in searchdict:
            if like:
                searchdata += field + " LIKE '" + searchdict[field] + "' AND "
            else:
                searchdata += field + "='" + searchdict[field] + "' AND "
        searchdata = searchdata[:-5]

        self.c.execute("SELECT {cl} FROM {tn} WHERE {sd}".format(cl=column, tn=table_name, sd=searchdata))
        return self.c.fetchall()

    def SelectColumnFromTable(self, table_name, column):
        self.c.execute("SELECT {cl} from {tn}".format(cl=column, tn=table_name))
        return self.c.fetchall()

    def SearchValueFromColumn(self, table_name, column, field, searchdata, like=True):
        # like makes searching slower. Set false if you require speed.
        if like:
            self.c.execute("SELECT {cl} FROM {tn} WHERE {fn} LIKE '{sd}'".format(cl=column, tn=table_name, fn=field, sd=searchdata))
        else:
            self.c.execute("SELECT {cl} FROM {tn} WHERE {fn}='{sd}'".format(cl=column, tn=table_name, fn=field, sd=searchdata))
        return self.c.fetchall()

    def ClearTable(self, table_name):
        self.c.execute("DELETE FROM {tn}".format(tn=table_name))
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
        for key in rowdict:
            names += key + ", "
            values += "'" + rowdict[key] + "', "
        names = "(" + names[:-2] + ")"
        values = "(" + values[:-2] + ")"

        self.c.execute("INSERT INTO {tn} {nm} VALUES {vl}".format(tn=table_name,nm=names, vl=values))
        self.conn.commit()

        return (self.c.lastrowid)

    def DeleteRow(self, table_name, field, fieldvalue):
        self.c.execute("DELETE FROM {tn} WHERE {fn}='{sd}'".format(tn=table_name, fn=field, sd=fieldvalue))
        self.conn.commit()
        return

    def UpdateRow(self, table_name, rowdict, field, fieldvalue):
        columns = ""
        for key in rowdict:
            columns += key + " = '" + rowdict[key] + "', "
        columns = columns[:-2]

        self.c.execute("UPDATE {tn} SET {cl} WHERE {fn}='{sd}'".format(tn=table_name, cl=columns, fn=field, sd=fieldvalue))
        self.conn.commit()
        return

