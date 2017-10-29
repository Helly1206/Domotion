from flask import Flask, Blueprint, render_template, g, request, session, redirect, jsonify
from flask_login import login_required
from flask import current_app as app

maxlines = 100

web_utils = Blueprint('web_utils', __name__, template_folder='templates')

@web_utils.route('/utils/log/_getlog/', methods=['GET'])
@login_required
def _getlog():
    if request.method == "GET":
        error = app.domotionaccess.Call("SetStatusBusy")
        if error:
            return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        error, ll = app.domotionaccess.Call("LogReadLines")
        if error:
            return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return jsonify(log=ll)
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_utils.route('/utils')
@login_required
def utils():
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    loggedin = session.get('logged_in')
    return render_template('utils.html', prefix=app.getp(), editing=0, loggedin=loggedin, log=0, lines=maxlines, stream="")

@web_utils.route('/utils/log')
@login_required
def utils_log():
    loggedin = session.get('logged_in')
    error, log = app.domotionaccess.Call("LogGetLog")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    return render_template('utils.html', prefix=app.getp(), editing=0, loggedin=loggedin, log=1, lines=maxlines, stream=log)

@web_utils.route('/utils/reboot_dialog', methods=['POST'])
@login_required
def reboot_dialog():
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            error = app.domotionaccess.Call("Reboot")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/logout'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_utils.route('/utils/shutdown_dialog', methods=['POST'])
@login_required
def shutdown_dialog():
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            error = app.domotionaccess.Call("Shutdown")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/logout'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_utils.route('/utils/restart_dialog', methods=['POST'])
@login_required
def restart_dialog():
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            if result['All'] == '1':
                error = app.domotionaccess.Call("RestartAll")
            else:
                error = app.domotionaccess.Call("RestartApp")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/logout'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_utils.route('/utils/restart')
@login_required
def restart():
    return render_template('restart.html', all=1, prefix=app.getp())

@web_utils.route('/utils/restart2')
@login_required
def restart2():
    return render_template('restart.html', all=0, prefix=app.getp())

@web_utils.route('/utils/shutdown')
@login_required
def shutdown():
    return render_template('shutdown.html', prefix=app.getp())

@web_utils.route('/utils/reboot')
@login_required
def reboot():
    return render_template('reboot.html', prefix=app.getp())