from flask import Flask, Blueprint, render_template, g, request, session, redirect, jsonify
from flask_login import login_required
from engine import AppKiller
from engine import localaccess
from utilities import memorylog

maxlines = 100

web_utils = Blueprint('web_utils', __name__, template_folder='templates')

@web_utils.route('/utils/log/_getlog/', methods=['GET'])
@login_required
def _getlog():
    if request.method == "GET":
        localaccess.SetStatusBusy()
        ll = memorylog.readlines()
        return jsonify(log=ll)
    else:
        return render_template("401.html"), 401

@web_utils.route('/utils')
@login_required
def utils():
    localaccess.SetStatusBusy()
    loggedin = session.get('logged_in')
    return render_template('utils.html', editing=0, loggedin=loggedin, log=0, lines=maxlines, stream="")

@web_utils.route('/utils/log')
@login_required
def utils_log():
    loggedin = session.get('logged_in')
    return render_template('utils.html', editing=0, loggedin=loggedin, log=1, lines=maxlines, stream=memorylog.getvalue())

@web_utils.route('/utils/reboot_dialog', methods=['POST'])
@login_required
def reboot_dialog():
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            AppKiller.reboot()
            pass
        return redirect('/logout')
    else:
        return render_template("401.html"), 401

@web_utils.route('/utils/shutdown_dialog', methods=['POST'])
@login_required
def shutdown_dialog():
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            AppKiller.shutdown()
            pass
        return redirect('/logout')
    else:
        return render_template("401.html"), 401

@web_utils.route('/utils/restart_dialog', methods=['POST'])
@login_required
def restart_dialog():
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            AppKiller.restart_app()
            pass
        return redirect('/logout')
    else:
        return render_template("401.html"), 401

@web_utils.route('/utils/restart')
@login_required
def restart():
    return render_template('restart.html')

@web_utils.route('/utils/shutdown')
@login_required
def shutdown():
    return render_template('shutdown.html')

@web_utils.route('/utils/reboot')
@login_required
def reboot():
    return render_template('reboot.html')