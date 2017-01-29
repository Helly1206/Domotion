import os
from flask import Flask, Blueprint, render_template
from db_webproc import db_webproc
import ssl

resourcepath=os.path.join(os.path.dirname(__file__), 'resources')
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(os.path.join(resourcepath,'domotion.crt'), os.path.join(resourcepath,'domotion.key'))

app = Flask(__name__)
app.register_blueprint(db_webproc)

@app.route('/')
def index():
    return render_template('index.html', editing=0)


def webapp():
    app.run(debug=True, use_reloader=False, port=8090)  #, ssl_context=context)
    # reloader can't work from a thread