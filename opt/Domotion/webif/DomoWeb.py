# -*- coding: utf-8 -*-
#########################################################
# SERVICE : webapp.py                                   #
#           Contianing the web application for Domotion #
#           I. Helwegen 2017                            #
#########################################################
# Make reading static, but thread prototected
####################### IMPORTS #########################
from os import path
from threading import Thread
from flask import Flask, Blueprint, request, redirect, render_template, g, session
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from db_webproc import db_webproc
from web_bwa import web_bwa
from web_status import web_status
from web_settings import web_settings
from web_utils import web_utils
from webutilities.common import common
from webutilities.domotionaccess import domotionaccess
import ssl
import logging
from base64 import b64decode
import requests
from urllib.parse import urlparse, urljoin
from sys import argv, exit
from getopt import getopt, GetoptError
#########################################################

####################### GLOBALS #########################
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
VERSION = "1.10"

#########################################################
# Class : FalskApp                                      #
#########################################################
class FlaskApp(Flask):

    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.common = common()
        self.domotionaccess = domotionaccess(port=self.common.GetSetting('DomoWeb_port'))
        duser=self.common.GetSetting('Username')
        dpass=self.common.GetSetting('Password')
        self.secret_key = self.common.GetKey()
        prefix = self.common.GetSetting('DomoWeb_prefix')
        if prefix[:1] != "/":
            prefix = "/" + prefix
        if prefix[-1:] == "/":
            prefix = prefix[:-1]
        self.prefix=prefix
        Debug = 0
        if (Debug>0):
            self.config['LOGIN_DISABLED'] = True
        elif ((len(duser)>0) and (len(dpass)>0)):
            self.config['LOGIN_DISABLED'] = False
        else:
            self.config['LOGIN_DISABLED'] = True
        #Tell the login manager where to redirect users to display the login page
        login_manager.login_view = self.p("/login/")
        #Setup the login manager.
        login_manager.setup_app(self)

    def is_safe_url(self, target):
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

    def p(self, route):
        return "%s%s"%(self.prefix,route)

    def pr(self, route):
        if __name__ == "__main__":
            return "%s%s"%(self.prefix,route)
        else:
            return route

    def getp(self):
        return self.prefix

#Flask-Login Login Manager
login_manager = LoginManager()
login_manager.session_protection = "strong"

app = FlaskApp(__name__)
if __name__ == "__main__":
    app.register_blueprint(db_webproc, url_prefix=app.getp())
    app.register_blueprint(web_bwa, url_prefix=app.getp())
    app.register_blueprint(web_status, url_prefix=app.getp())
    app.register_blueprint(web_settings, url_prefix=app.getp())
    app.register_blueprint(web_utils, url_prefix=app.getp())
else:
    app.register_blueprint(db_webproc)
    app.register_blueprint(web_bwa)
    app.register_blueprint(web_status)
    app.register_blueprint(web_settings)
    app.register_blueprint(web_utils)

#########################################################
# Class : User                                          #
#########################################################
class User(UserMixin):
    def __init__(self, userid, password):
        self.id = userid
        self.password = password

    @staticmethod
    def get(userid):
        duser = app.common.GetSetting('Username')
        dpass = app.common.GetSetting('Password')
        if (userid == duser): # Get from localaccess
            return User(duser, dpass)
        elif (userid == "internal"):
            return User("internal", app.common.GetSessionPassword())
        return None

    @staticmethod
    def check(userid, password):
        user = User.get(userid)
        if (app.common.IsPassword(password)):
            if user and password == user.password:
                return user
        else:
            if user and app.common.HashPass(password) == user.password:
                return user
        return None

#########################################################
# login_manager funtions                                #
#########################################################
@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        userdata = api_key.decode().split(":")
        user = None
        if (len(userdata) > 1):
            user = User.check(userdata[0], userdata[1])
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = b64decode(api_key)
        except TypeError:
            pass
        userdata = api_key.decode().split(":")
        user = None
        if (len(userdata) > 1):
            user = User.check(userdata[0], userdata[1])
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None

#########################################################
# app functions                                         #
#########################################################
@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html', prefix=app.getp()), 400

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html', prefix=app.getp()), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', prefix=app.getp()), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', prefix=app.getp()), 500

@app.errorhandler(503)
def page_not_found(e):
    return render_template('503.html', prefix=app.getp()), 503

@app.errorhandler(504)
def page_not_found(e):
    return render_template('504.html', prefix=app.getp()), 504

@app.route(app.pr('/'))
@login_required
def index():
    return redirect(app.p('/status'))

@app.route(app.pr("/logout/"))
def logout_page():
    logout_user()
    session['logged_in'] = False
    return redirect(app.p("/"))

@app.route(app.pr("/login/"), methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html", prefix=app.getp())
    if request.method == "POST":
        user = User.check(request.form['username'], request.form['password'])
        if user:
            login_user(user, remember=False)
            session['logged_in'] = True
            target = request.args.get("next") or app.p("/")
            if app.is_safe_url(target):
                return redirect(target)
    return render_template("401.html", prefix=app.getp()), 401

#########################################################
# main                                                  #
#########################################################
def main(argv):
    ssl = False
    port = 5000
    crt = ""
    key = ""
    try:
        opts, args = getopt(argv,"hsp:c:k:",["help","ssl","port=","crt=","key="])
    except GetoptError:
        print("Domotion Home control and automation web interface")
        print("Version: " + VERSION)
        print(" ")
        print("Enter 'DomoWeb.py -h' for help")
        exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Domotion Home control and automation web interface")
            print("Version: " + VERSION)
            print(" ")
            print("Usage:")
            print("         DomoWeb.py -s -p <portnumber> -c <certificate file> -k <key file>")
            print("         -h, --help: Print this help file")
            print("         -s, --ssl: Start server in ssl mode")
            print("         -p, --port: Enter port number for server")
            print("         -c, --crt: Location of the certificate file (required for ssl)")
            print("         -k, --key: Location of the key file (required for ssl)")
            exit()
        elif opt in ("-s", "--ssl"):
            ssl = True
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-c", "--crt"):
            crt = arg
        elif opt in ("-k", "--key"):
            key = arg

    if (ssl):
        if (crt == ""):
            ssl = False
            print ("No certificate file entered, ssl disabled")
        elif (key == ""):
            ssl = False
            print ("No key file entered, ssl disabled")
        elif (not path.isfile(crt)):
            ssl = False
            print ("Invalid or non existing certificate file, ssl disabled")
        elif (not path.isfile(key)):
            ssl = False
            print ("Invalid or non existing key file, ssl disabled")
        else:
            context.load_cert_chain(crt, key)

    try:
        if (ssl):
            app.run(host="0.0.0.0", debug=False, use_reloader=False, port=port, ssl_context=context)
        else:
            app.run(host="0.0.0.0", debug=False, use_reloader=False, port=port)
    except Exception as e:
        print(e)

#########################################################
if __name__ == "__main__":
    main(argv[1:])
