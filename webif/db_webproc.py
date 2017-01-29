from flask import Flask, Blueprint, render_template, g, request, redirect
from database import db_edit

db_webproc = Blueprint('db_webproc', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_edit', None)
    if db is None:
        db = g_db_edit = db_edit("../Domotion.db")
    return db

@db_webproc.teardown_request
def teardown_request(exception):
    db = getattr(g, '_db_edit', None)
    if db is not None:
        del db

@db_webproc.route('/database_deleted/<string:tableid>/<int:id>', methods=['POST'])
def db_deleteditem(tableid,id):
    if request.method == "POST":
        result=request.form
        print result
        if result['Button'] == 'Yes':
            get_db().DeleteTableRow(tableid, id)
        return redirect('/database/%s'%(tableid))
    else:
        return 'Bad request: Incorrect use of  this URL'

@db_webproc.route('/database_edited/<string:tableid>/<int:id>', methods=['POST'])
def db_editeditem(tableid,id):
    if request.method == "POST":
        result=request.form
        print result
        # add results to db
        if result['Button'] == 'Ok':
            get_db().EditTableRow(tableid, id, result)
        return redirect('/database/%s'%(tableid))
    else:
        return 'Bad request: Incorrect use of  this URL'

@db_webproc.route('/database_edit/<string:tableid>/<int:id>')
def db_edititem(tableid,id):
    # generate editingdata (depending on tableid)
    cols, data, editable = get_db().ReadTable(tableid)
    editingdata = get_db().BuildOptionsDicts(tableid)
    return render_template('db_editor.html', cols=cols, data=data, editable=0, tableid=tableid, editing=1, editingid=id, editingdata=editingdata)

@db_webproc.route('/database_delete/<string:tableid>/<int:id>')
def db_deleteitem(tableid,id):
    cols, data, editable = get_db().ReadTable(tableid)
    return render_template('db_editor.html', cols=cols, data=data, editable=0, tableid=tableid, editing=2, editingid=id, editingdata=[])

@db_webproc.route('/database_add/<string:tableid>')
def db_additem(tableid):
    id = get_db().AddTableRow(tableid)
    return redirect('/database_edit/%s/%d'%(tableid,id))
    
@db_webproc.route('/database/<string:tableid>')
def db_view(tableid):
    cols, data, editable = get_db().ReadTable(tableid)
    return render_template('db_editor.html', cols=cols, data=data, editable=editable, tableid=tableid, editing=0, editingid=0, editingdata=[])