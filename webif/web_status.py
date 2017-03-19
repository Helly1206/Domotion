from flask import Flask, Blueprint, render_template, g, request, redirect, jsonify
from flask_login import login_required
from engine import commandqueue
from engine import localaccess
from database import db_status
#from frontend import basicwebaccess

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
            else:
                val = localaccess.GetSensorValues()
        tm = localaccess.GetAscTime()
        st = localaccess.GetStatus(status)
        return jsonify(time=tm, status=st, values=val)
    else:
        return render_template("401.html"), 401

@web_status.route('/status/_gettimers/<string:tableid>', methods=['GET'])
@login_required
def _gettimers(tableid):
    if request.method == "GET":
        val = None
        key=request.args.get('Id')
        ivalue=request.args.get('Value')
        if ((key != None) and (ivalue != None)):
            status = 1
            localaccess.SetTimer(int(key), int(ivalue))
        else:
            status = 0
            val = localaccess.GetTimerValues()
        tm = localaccess.GetAscTime()
        st = localaccess.GetStatus(status)
        sr = localaccess.Mod2Asc(localaccess.GetSunRiseSetMod())
        return jsonify(time=tm, riseset=sr, status=st, values=val)
    else:
        return render_template("401.html"), 401

@web_status.route('/status/timers_edit/<string:tableid>/<int:id>')
@login_required
def status_edit(tableid, id):
    if (tableid != "timers"):
        cols, data, digital = get_db().GetDevices(tableid)
    else:
        cols, data = get_db().GetTimers()
        digital = None
    return render_template('status.html', editing=1, tableid=tableid, cols=cols, data=data, digital=digital, editingid=id)

@web_status.route('/status/recalc/<string:tableid>')
@login_required
def statusrecalc(tableid):
    commandqueue.callback2("timerrecalc")
    return redirect('/status/'+tableid)

@web_status.route('/status/<string:tableid>')
@login_required
def status(tableid):
    if (tableid != "timers"):
        cols, data, digital = get_db().GetDevices(tableid)
    else:
        cols, data = get_db().GetTimers()
        digital = None
    return render_template('status.html', editing=0, tableid=tableid, cols=cols, data=data, digital=digital, editingid=0)

@web_status.route('/status')
@login_required
def statusstart():
    return redirect('/status/devices')