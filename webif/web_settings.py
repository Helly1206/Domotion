from flask import Flask, Blueprint, render_template, g, request, redirect
from database import db_settings
from engine import localaccess
from engine import commandqueue

web_settings = Blueprint('web_settings', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_settings', None)
    if db is None:
        db = g_db_settings = db_settings(localaccess.GetDBPath())
    return db
    
@web_settings.teardown_request
def teardown_request(exception):
    db = getattr(g, '_db_settings', None)
    if db is not None:
        del db

@web_settings.route('/settings_edited/<int:id>', methods=['POST'])
def settings_edited(id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            get_db().EditSettings(id, result)
            commandqueue.callback2("settings")
            pass
        return redirect('/settings')
    else:
        return 'Bad request: Incorrect use of  this URL'

@web_settings.route('/settings_edit/<int:id>')
def settings_edit(id):
    cols, data = get_db().ReadSettings()
    editingdata = get_db().BuildFormatDict()
    return render_template('settings.html', cols=cols, data=data, editing=1, editingid=id, editingdata=editingdata)

@web_settings.route('/settings')
def settings():
    cols, data = get_db().ReadSettings()
    return render_template('settings.html', cols=cols, data=data, editing=0, editingid=0, editingdata={})