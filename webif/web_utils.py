from flask import Flask, Blueprint, render_template, g, request, session, redirect
from flask_login import login_required
from engine import AppKiller
#from frontend import basicwebaccess

web_utils = Blueprint('web_utils', __name__, template_folder='templates')

@web_utils.route('/utils')
@login_required
def utils():
    loggedin = session.get('logged_in')
    return render_template('utils.html', editing=0, loggedin=loggedin)

@web_utils.route('/restart_dialog', methods=['POST'])
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

@web_utils.route('/restart')
@login_required
def restart():
    return render_template('restart.html')