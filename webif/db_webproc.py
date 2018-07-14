from flask import Flask, Blueprint, render_template, g, request, redirect
from flask_login import login_required
from webdatabase import db_edit
from flask import current_app as app

db_webproc = Blueprint('db_webproc', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_edit', None)
    if db is None:
        db = g_db_edit = db_edit(app)
    return db
    
@db_webproc.teardown_request
def teardown_request(exception):
    db = getattr(g, '_db_edit', None)
    if db is not None:
        del db

@db_webproc.route('/database_deleted/<string:tableid>/<int:id>', methods=['POST'])
@login_required
def db_deleteditem(tableid,id):
    if request.method == "POST":
        result=request.form
        if result['Button'] == 'Yes':
            get_db().DeleteTableRow(tableid, id)
            error = app.domotionaccess.Call("Callback","process")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/database/%s'%(tableid)))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@db_webproc.route('/database_edited/<string:tableid>/<int:id>', methods=['POST'])
@login_required
def db_editeditem(tableid,id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            get_db().EditTableRow(tableid, id, result)
            error = app.domotionaccess.Call("Callback","process")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/database/%s'%(tableid)))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@db_webproc.route('/database_edit/<string:tableid>/<int:id>')
@login_required
def db_edititem(tableid,id):
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    # generate editingdata (depending on tableid)
    fmt = None
    if (tableid == "timers"):
        fmt = app.common.TimeNoSec()
    cols, data, editable = get_db().ReadTable(tableid)
    editingdata = get_db().BuildOptionsDicts(tableid)
    print data
    return render_template('db_editor.html', prefix=app.getp(), cols=cols, data=data, editable=0, tableid=tableid, editing=1, editingid=id, editingdata=editingdata, format=fmt)

@db_webproc.route('/database_delete/<string:tableid>/<int:id>')
@login_required
def db_deleteitem(tableid,id):
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    cols, data, editable = get_db().ReadTable(tableid)
    return render_template('db_editor.html', prefix=app.getp(), cols=cols, data=data, editable=0, tableid=tableid, editing=2, editingid=id, editingdata=[], format=None)

@db_webproc.route('/database_add/<string:tableid>')
@login_required
def db_additem(tableid):
    id = get_db().AddTableRow(tableid)
    return redirect(app.p('/database_edit/%s/%d'%(tableid,id)))
    
@db_webproc.route('/database/<string:tableid>')
@login_required
def db_view(tableid):
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    cols, data, editable = get_db().ReadTable(tableid)
    return render_template('db_editor.html', prefix=app.getp(), cols=cols, data=data, editable=editable, tableid=tableid, editing=0, editingid=0, editingdata=[], format=None)

@db_webproc.route('/database')
@login_required
def db_viewstart():
    return redirect(app.p('/database/sensors'))