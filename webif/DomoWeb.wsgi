#!/usr/bin/python3
from sys import path
from os import environ

path.insert(0,"/var/www/Domotion")

def application(req_environ, start_response):
    try:
        environ['LC_TIME'] = req_environ['LC_TIME']
    except:
        environ['LC_TIME'] = ''

    from DomoWeb import app as _application
    return _application(req_environ, start_response)