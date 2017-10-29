from flask import Flask, Blueprint, g, request
from flask_login import login_required
from flask import current_app as app

web_bwa = Blueprint('web_bwa', __name__, template_folder='templates')

@web_bwa.route('/get', methods=['GET'])
@login_required
def bwa_get():
    if request.method == "GET":
        tag=request.args.get('tag')
        error, retval = app.domotionaccess.Call("BWAget",tag)
        if error:
            return 'Error: during server call, HTML error: %d' % error
        else:
            return retval
    else:
        return 'Bad request: Incorrect use of this URL'

@web_bwa.route('/set', methods=['GET'])
@login_required
def bwa_set():
    if request.method == "GET":
        tag=request.args.get('tag')
        value=request.args.get('value')
        error, retval = app.domotionaccess.Call("BWAset",tag,value)
        if error:
            return 'Error: during server call, HTML error: %d' % error
        else:
            return retval
    else:
        return 'Bad request: Incorrect use of this URL'