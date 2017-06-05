from flask import Flask, Blueprint, render_template, g, request, redirect, jsonify
from flask_login import login_required
from engine import commandqueue
from engine import localaccess
from database import db_status
from utilities import localformat

web_status = Blueprint('web_status', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_status', None)
    if db is None:
        db = g_db_status = db_status(localaccess.GetDBPath())
    return db
    
@web_status.teardown_request
def teardown_request(exception):
    db = getattr(g, '_db_status', None)
    if db is not None:
        del db

@web_status.route('/status/_getvalues/<string:tableid>', methods=['GET'])
@login_required
def _getvalues(tableid):
    if request.method == "GET":
        localaccess.SetStatusBusy()
        val = None
        key=request.args.get('Id')
        ivalue=request.args.get('Value')
        if ((key != None) and (ivalue != None)):
            status = 1
            commandqueue.put_id2("None", int(key), ivalue, (tableid == "controls"))
        else:
            status = 0
            if (tableid == "devices"):
                val = localaccess.GetActuatorValues()
            elif (tableid == "controls"):
                val = localaccess.GetSensorValues()
        tm = localaccess.GetAscTime()
        st = localaccess.GetStatus(status)
        return jsonify(time=tm, status=st, values=val)
    else:
        return render_template("401.html"), 401

@web_status.route('/status/_gettimers', methods=['GET'])
@login_required
def _gettimers():
    if request.method == "GET":
        localaccess.SetStatusBusy()
        tm = localaccess.GetAscTime()
        st = localaccess.GetStatus(status)
        sr = localformat.Mod2Asc(localaccess.GetSunRiseSetMod())
        return jsonify(time=tm, riseset=sr, status=st)
    else:
        return render_template("401.html"), 401

@web_status.route('/status/_getholidays', methods=['GET'])
@login_required
def _getholidays():
    if request.method == "GET":
        localaccess.SetStatusBusy()
        tm = localaccess.GetAscTime()
        st = localaccess.GetStatus(0)
        td = get_db().GetTodayString()
        return jsonify(time=tm, status=st, today=td)
    else:
        return render_template("401.html"), 401

@web_status.route('/status/timers_edit/<string:tableid>/<int:id>')
@login_required
def timers_edit(tableid, id):
    cols, data = get_db().GetTimers()
    fmt = localformat.timenosec()
    return render_template('status.html', editing=1, tableid=tableid, cols=cols, data=data, editingdata=None, digital=None, dtype=None, editingid=id, format=fmt)

@web_status.route('/timers_edited/<int:id>', methods=['POST'])
@login_required
def timers_editeditem(id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            value = -1
            if (int(result['ValActive'])):
                value = localformat.Asc2Mod(result['Time'])
            localaccess.SetTimer(id, value)
        return redirect('/status/timers')
    else:
        return render_template("401.html"), 401

@web_status.route('/status/holidays_edit/<int:id>')
@login_required
def holidays_edit(id):
    cols, data = get_db().GetHolidays()
    fmt = localformat.date()
    edata = get_db().BuildOptionsDicts("holidays")
    return render_template('status.html', editing=1, tableid="holidays", cols=cols, data=data, editingdata=edata, digital=None, dtype=None, editingid=id, format=fmt)

@web_status.route('/status/holidays_delete/<int:id>')
@login_required
def holidays_deleteitem(id):
    cols, data = get_db().GetHolidays()
    fmt = localformat.date()
    return render_template('status.html', editing=2, tableid="holidays", cols=cols, data=data, editingdata=None, digital=None, dtype=None, editingid=id, format=fmt)


@web_status.route('/holidays_deleted/<int:id>', methods=['POST'])
@login_required
def holidays_deleteditem(id):
    if request.method == "POST":
        result=request.form
        if result['Button'] == 'Yes':
            get_db().DeleteHolidaysRow(id)
            commandqueue.callback2("timerrecalc")
        return redirect('/status/holidays')
    else:
        return render_template("401.html"), 401

@web_status.route('/holidays_edited/<int:id>', methods=['POST'])
@login_required
def holidays_editeditem(id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            get_db().EditHolidaysRow(id, result)
            commandqueue.callback2("timerrecalc")
        return redirect('/status/holidays')
    else:
        return render_template("401.html"), 401

@web_status.route('/status/holidays_add')
@login_required
def holidays_additem():
    id = get_db().AddHolidaysRow()
    return redirect('/status/holidays_edit/%d'%(id))

@web_status.route('/status/timers_recalc')
@login_required
def statusrecalc():
    commandqueue.callback2("timerrecalc")
    return redirect('/status/timers')

@web_status.route('/status/<string:tableid>')
@login_required
def status(tableid):
    fmt=None
    if (tableid == "timers"):
        cols, data = get_db().GetTimers()
        digital = None
        dtype = None
    elif (tableid == "holidays"):
        get_db().DeleteOldHolidays()
        cols, data = get_db().GetHolidays()
        digital = None
        type = None
    else:
        cols, data, digital, dtype = get_db().GetDevices(tableid)
    return render_template('status.html', editing=0, tableid=tableid, cols=cols, data=data, editingdata=None, digital=digital, dtype=dtype, editingid=0, format=fmt)

@web_status.route('/status')
@login_required
def statusstart():
    return redirect('/status/devices')