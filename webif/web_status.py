from flask import Flask, Blueprint, render_template, g, request
#from frontend import basicwebaccess

web_status = Blueprint('web_status', __name__, template_folder='templates')

@web_status.route('/status')
def index():
    return render_template('index.html', editing=0)