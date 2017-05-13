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
from engine import localaccess
import ssl
import logging
from base64 import b64decode
import requests
from urlparse import urlparse, urljoin
#########################################################

####################### GLOBALS #########################
resourcepath=path.join(path.dirname(__file__), 'resources')
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(path.join(resourcepath,'domotion.crt'), path.join(resourcepath,'domotion.key'))

app = Flask(__name__)
app.register_blueprint(db_webproc)
app.register_blueprint(web_bwa)
app.register_blueprint(web_status)
app.register_blueprint(web_settings)
app.register_blueprint(web_utils)

#Flask-Login Login Manager
login_manager = LoginManager()
login_manager.session_protection = "strong"

#########################################################
# Class : User                                          #
#########################################################
class User(UserMixin):
    def __init__(self, userid, password):
        self.id = userid
        self.password = password
 
    @staticmethod
    def get(userid):
        duser = localaccess.GetSetting('Username')
        dpass = localaccess.GetSetting('Password')
        if (userid == duser): # Get from localaccess
            return User(duser, dpass)
        elif (userid == "internal"):
            return User("internal", localaccess.GetSessionPassword())
        return None

    @staticmethod
    def check(userid, password):
        user = User.get(userid)
        if (localaccess.ispassword(password)):
            if user and password == user.password:
                return user
        else:
            if user and localaccess.hash_pass(password) == user.password:
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
        userdata = api_key.split(":")
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
        userdata = api_key.split(":")
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
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html'), 400

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route('/shutdown')
@login_required
def shutdown():
    if ((urlparse(request.host_url).hostname == "localhost") and (current_user.get_id() == "internal")):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Server')
        func()
        return "Server shutdown ..."
    else:
        return render_template("401.html"), 401

@app.route('/')
@login_required
def index():
    return redirect('/status')

@app.route("/logout/")
def logout_page():
    logout_user()
    session['logged_in'] = False
    return redirect("/")
 
@app.route("/login/", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")    
    if request.method == "POST":
        user = User.check(request.form['username'], request.form['password'])
        if user:
            login_user(user, remember=False)
            session['logged_in'] = True
            target = request.args.get("next") or "/"
            if is_safe_url(target):
                return redirect(target)
    return render_template("401.html"), 401

#########################################################
# Class : webapp                                        #
#########################################################
class webapp(Thread):
    def __init__(self, Debug):
        #self.server = None
        self.logger = logging.getLogger('Domotion.Webapp')
        # settings for future use ...
        self.port=localaccess.GetSetting('Webport')
        self.ssl=localaccess.GetSetting('SSL')
        duser=localaccess.GetSetting('Username')
        dpass=localaccess.GetSetting('Password')
        app.secret_key = localaccess.get_key()
        if (Debug>0):
            app.config['LOGIN_DISABLED'] = True
        elif ((len(duser)>0) and (len(dpass)>0)):
            app.config['LOGIN_DISABLED'] = False
        else:
            app.config['LOGIN_DISABLED'] = True
        if (Debug>1):
            self.port=5000
        #Tell the login manager where to redirect users to display the login page
        login_manager.login_view = "/login/"
        #Setup the login manager. 
        login_manager.setup_app(app) 

        Thread.__init__(self)

    def __del__(self):
        self.logger.info("finished")

    def terminate(self):
        self.logger.info("terminating")
        success = False
        #shutdown server via call ... (ugly way of doing this, but the only method I can come up with)
        try:
            auth = ("internal", localaccess.GetSessionPassword())
            if (self.ssl):
                result = requests.get("https://localhost:%d/shutdown"%self.port, auth=auth, verify=False)
            else:
                result = requests.get("http://localhost:%d/shutdown"%self.port, auth=auth, verify=False)
            success = True
        except:
            pass
        return success

    def run(self):
        try:
            self.logger.info("running")
            if (self.ssl):
                app.run(host="0.0.0.0", debug=False, use_reloader=False, port=self.port, ssl_context=context)
            else:
                app.run(host="0.0.0.0", debug=False, use_reloader=False, port=self.port)
        except Exception, e:
            self.logger.exception(e)
            