var nIntervId = 0;
var TimerOn = 0;
var lines = 0;
var maxlines = 0;
var route = "";

function getLines() {
	loadJSON(route+'/utils/log/_getlog/', handleValues);
}

function handleValues(resp) {
	var values = JSON.parse(resp);
	var logarea = document.getElementById('logarea');
	AddtoLogArea(values.log);
}

function loadJSON(url, callback) {
	var xobj = new XMLHttpRequest();
	xobj.overrideMimeType("application/json");
	xobj.open('GET', url, true);
	xobj.onreadystatechange = function () {
		if (xobj.readyState == 4 && xobj.status == "200") {
			callback(xobj.responseText);
		} else if (xobj.status != "200") {
			location.reload();
		}
	};
	xobj.send(null);
}

function AddtoLogArea(values) {
	var i = 0;
	var added = false;
	for (i in values) {
		logline = values[i];
		if(logline.indexOf("\n")!=-1) {
			if ((maxlines > 0) && (lines>=maxlines)) {
				dlines = logarea.value.split("\n");
				dlines.splice(0, 1);
				logarea.value = dlines.join("\n");
			} else {
				lines += 1;
				added = true;
			}
			logarea.value += values[i];
		}
	}
	if ((added) && (document.getElementById('autoscroll').checked)) {
		logarea.scrollTop = logarea.scrollHeight;
	}
}

function Timer(Value) {
	if (Value == 0) {
		clearInterval(nIntervId);
		TimerOn = 0;
	} else if (Value == 1) {
		clearInterval(nIntervId);
		nIntervId = setInterval(getLines, 1000);
		TimerOn = 1;
	} else {
		clearInterval(nIntervId);
		nIntervId = setInterval(getLines, 1000);
		TimerOn = 2;
	}
}

function OnLoadWindow(_maxlines, rt, stream) {
	var logarea = document.getElementById('logarea');
	route=rt;
	if (document.getElementById('autoscroll').checked) {
		logarea.scrollTop = logarea.scrollHeight;
	}
	lines = logarea.value.split("\n").length;
	maxlines = _maxlines;
	AddtoLogArea(stream);
	Timer(1);
}

function OnUnloadWindow() {
	Timer(0);
}
