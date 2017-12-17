from flask import Flask, Blueprint, render_template, g, request, redirect, jsonify
from flask_login import login_required
from webdatabase import db_status
from flask import current_app as app

web_status = Blueprint('web_status', __name__, template_folder='templates')

def get_db():
    db = getattr(g, '_db_status', None)
    if db is None:
        db = g_db_status = db_status(app)
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
        error = app.domotionaccess.Call("SetStatusBusy")
        if error:
            return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        val = None
        key=request.args.get('Id')
        ivalue=request.args.get('Value')
        if ((key != None) and (ivalue != None)):
            status = 1
            error = app.domotionaccess.Call("PutValue", int(key), ivalue, (tableid == "controls"))
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        else:
            status = 0
            if (tableid == "devices"):
                error, val = app.domotionaccess.Call("GetActuatorValues")
                if error:
                    return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
            elif (tableid == "controls"):
                error, val = app.domotionaccess.Call("GetSensorValues")
                if error:
                    return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        tm = app.common.GetAscTime()
        st = app.common.GetStatus(status)
        return jsonify(time=tm, status=st, values=val)
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_status.route('/status/_gettimers', methods=['GET'])
@login_required
def _gettimers():
    if request.method == "GET":
        error = app.domotionaccess.Call("SetStatusBusy")
        if error:
            return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        tm = app.common.GetAscTime()
        st = app.common.GetStatus(0)
        error, riseset = app.domotionaccess.Call("GetSunRiseSetMod")
        if error:
            return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        sr = app.common.Mod2Asc(riseset)
        return jsonify(time=tm, riseset=sr, status=st)
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_status.route('/status/_getholidays', methods=['GET'])
@login_required
def _getholidays():
    if request.method == "GET":
        error = app.domotionaccess.Call("SetStatusBusy")
        if error:
            return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        tm = app.common.GetAscTime()
        st = app.common.GetStatus(0)
        td = get_db().GetTodayString()
        return jsonify(time=tm, status=st, today=td)
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_status.route('/status/timers_edit/<string:tableid>/<int:id>')
@login_required
def timers_edit(tableid, id):
    cols, data = get_db().GetTimers()
    fmt = app.common.TimeNoSec()
    return render_template('status.html', prefix=app.getp(), editing=1, tableid=tableid, cols=cols, data=data, editingdata=None, digital=None, dtype=None, editingid=id, format=fmt)

@web_status.route('/timers_edited/<int:id>', methods=['POST'])
@login_required
def timers_editeditem(id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            value = -1
            if (int(result['ValActive'])):
                value = app.common.Asc2Mod(result['Time'])
            error, dummy = app.domotionaccess.Call("SetTimer", id, value)
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/status/timers'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_status.route('/status/holidays_edit/<int:id>')
@login_required
def holidays_edit(id):
    cols, data = get_db().GetHolidays()
    fmt = app.common.date()
    edata = get_db().BuildOptionsDicts("holidays")
    return render_template('status.html', prefix=app.getp(), editing=1, tableid="holidays", cols=cols, data=data, editingdata=edata, digital=None, dtype=None, editingid=id, format=fmt)

@web_status.route('/status/holidays_delete/<int:id>')
@login_required
def holidays_deleteitem(id):
    cols, data = get_db().GetHolidays()
    fmt = app.common.date()
    return render_template('status.html', prefix=app.getp(), editing=2, tableid="holidays", cols=cols, data=data, editingdata=None, digital=None, dtype=None, editingid=id, format=fmt)


@web_status.route('/holidays_deleted/<int:id>', methods=['POST'])
@login_required
def holidays_deleteditem(id):
    if request.method == "POST":
        result=request.form
        if result['Button'] == 'Yes':
            get_db().DeleteHolidaysRow(id)
            error = app.domotionaccess.Call("Callback","timerrecalc")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/status/holidays'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_status.route('/holidays_edited/<int:id>', methods=['POST'])
@login_required
def holidays_editeditem(id):
    if request.method == "POST":
        result=request.form
        # add results to db
        if result['Button'] == 'Ok':
            get_db().EditHolidaysRow(id, result)
            error = app.domotionaccess.Call("Callback","timerrecalc")
            if error:
                return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
        return redirect(app.p('/status/holidays'))
    else:
        return render_template("401.html", prefix=app.getp()), 401

@web_status.route('/status/holidays_add')
@login_required
def holidays_additem():
    id = get_db().AddHolidaysRow()
    return redirect(app.p('/status/holidays_edit/%d'%(id)))

@web_status.route('/status/timers_recalc')
@login_required
def statusrecalc():
    error = app.domotionaccess.Call("Callback","timerrecalc")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    return redirect(app.p('/status/timers'))

@web_status.route('/status/<string:tableid>')
@login_required
def status(tableid):
    error = app.domotionaccess.Call("SetStatusBusy")
    if error:
        return render_template(app.common.ErrorHtml(error), prefix=app.getp()), error
    fmt=None
    if (tableid == "timers"):
        cols, data = get_db().GetTimers()
        digital = None
        dtype = None
    elif (tableid == "holidays"):
        cols, data = get_db().GetHolidays()
        digital = None
        dtype = None
    else:
        cols, data, digital, dtype = get_db().GetDevices(tableid)
    return render_template('status.html', prefix=app.getp(), editing=0, tableid=tableid, cols=cols, data=data, editingdata=None, digital=digital, dtype=dtype, editingid=0, format=fmt)

@web_status.route('/status')
@login_required
def statusstart():
    return redirect(app.p('/status/devices'))