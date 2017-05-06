from flask import Flask, Blueprint, render_template, g, request, redirect
from flask_login import login_required
from database import db_edit
from engine import localaccess
from engine import commandqueue
from utilities import localformat

db_webproc = Blueprint('db_webproc', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_edit', None)
    if db is None:
        db = g_db_edit = db_edit(localaccess.GetDBPath())
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
            commandqueue.callback2("process")
        return redirect('/database/%s'%(tableid))
    else:
        return render_template("401.html"), 401

@db_webproc.route('/database_edited/<string:tableid>/<int:id>', methods=['POST'])
@login_required
def db_editeditem(tableid,id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            get_db().EditTableRow(tableid, id, result)
            commandqueue.callback2("process")
        return redirect('/database/%s'%(tableid))
    else:
        return render_template("401.html"), 401

@db_webproc.route('/database_edit/<string:tableid>/<int:id>')
@login_required
def db_edititem(tableid,id):
    # generate editingdata (depending on tableid)
    fmt = None
    if (tableid == "timers"):
        fmt = localformat.timenosec()
    cols, data, editable = get_db().ReadTable(tableid)
    editingdata = get_db().BuildOptionsDicts(tableid)
    return render_template('db_editor.html', cols=cols, data=data, editable=0, tableid=tableid, editing=1, editingid=id, editingdata=editingdata, format=fmt)

@db_webproc.route('/database_delete/<string:tableid>/<int:id>')
@login_required
def db_deleteitem(tableid,id):
    cols, data, editable = get_db().ReadTable(tableid)
    return render_template('db_editor.html', cols=cols, data=data, editable=0, tableid=tableid, editing=2, editingid=id, editingdata=[], format=None)

@db_webproc.route('/database_add/<string:tableid>')
@login_required
def db_additem(tableid):
    id = get_db().AddTableRow(tableid)
    return redirect('/database_edit/%s/%d'%(tableid,id))
    
@db_webproc.route('/database/<string:tableid>')
@login_required
def db_view(tableid):
    cols, data, editable = get_db().ReadTable(tableid)
    return render_template('db_editor.html', cols=cols, data=data, editable=editable, tableid=tableid, editing=0, editingid=0, editingdata=[], format=None)

@db_webproc.route('/database')
@login_required
def db_viewstart():
    return redirect('/database/sensors');