from flask import Flask, Blueprint, render_template, g, request, redirect
from flask_login import login_required
from webdatabase import db_settings
from flask import current_app as app

web_settings = Blueprint('web_settings', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_settings', None)
    if db is None:
        db = g_db_settings = db_settings(app)
    return db
    
@web_settings.teardown_request
def teardown_request(exception):
    db = getattr(g, '_db_settings', None)
    if db is not None:
        del db

@web_settings.route('/settings_edited/<int:id>', methods=['POST'])
@login_required
def settings_edited(id):
    if request.method == "POST":
        restart = False
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            restart=get_db().EditSettings(id, result)
            error = app.domotionaccess.Call("Callback","process")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        if (restart==2): # Also restart webserver
            return redirect(app.p('/utils/restart'))
        elif (restart==1): # Restart Domotion only
            return redirect(app.p('/utils/restart2'))
        else:
            return redirect(app.p('/settings'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_settings.route('/settings_edit/<int:id>')
@login_required
def settings_edit(id):
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    cols, data = get_db().ReadSettings()
    editingdata = get_db().BuildFormatDict()
    return render_template('settings.html', prefix=app.getp(), cols=cols, data=data, editing=1, editingid=id, editingdata=editingdata)

@web_settings.route('/settings')
@login_required
def settings():
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    cols, data = get_db().ReadSettings()
    return render_template('settings.html', prefix=app.getp(), cols=cols, data=data, editing=0, editingid=0, editingdata={})