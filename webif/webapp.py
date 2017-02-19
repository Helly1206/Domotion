import os
from threading import Thread
from flask import Flask, Blueprint, redirect, render_template, g
from db_webproc import db_webproc
from web_bwa import web_bwa
from web_status import web_status 
from web_settings import web_settings
from engine import localaccess
import ssl
import logging

resourcepath=os.path.join(os.path.dirname(__file__), 'resources')
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(os.path.join(resourcepath,'domotion.crt'), os.path.join(resourcepath,'domotion.key'))

app = Flask(__name__)
app.register_blueprint(db_webproc)
app.register_blueprint(web_bwa)
app.register_blueprint(web_status)
app.register_blueprint(web_settings)

@app.route('/')
def index():
    return redirect('/status')

class webapp(Thread):
    def __init__(self):
        self.logger = logging.getLogger('Domotion.Webapp')
        # settings for future use ...
        self.port=localaccess.GetSetting('Webport')
        self.ssl=localaccess.GetSetting('SSL')
        self.username=localaccess.GetSetting('Username')
        self.password=localaccess.GetSetting('Password')
        Thread.__init__(self)

    def __del__(self):
        pass

    def run(self):
        self.logger.info("running")

        app.run(debug=True, use_reloader=False, port=self.port)  #, ssl_context=context)
