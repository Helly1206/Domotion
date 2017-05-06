var nIntervId = 0;
var TimerOn = 0;
var lines = 0;
var maxlines = 0;

function getLines() {
	loadJSON('/utils/log/_getlog/', handleValues);
}

function handleValues(resp) {
	var values = JSON.parse(resp);
	var logarea = document.getElementById('logarea');
	var i = 0;
	var added = false;

	for (i in values.log) {
		if ((maxlines > 0) && (lines>=maxlines)) {
			dlines = logarea.value.split("\n");
			dlines.splice(0, 1);
			logarea.value = dlines.join("\n");	
		} else {
			lines += 1;
			added = true;
		}
	    logarea.value += values.log[i];
	}
	if ((added) && (document.getElementById('autoscroll').checked)) {
		logarea.scrollTop = logarea.scrollHeight;
	}
}

function loadJSON(url, callback) {   
	var xobj = new XMLHttpRequest();
	xobj.overrideMimeType("application/json");
	xobj.open('GET', url, true);
	xobj.onreadystatechange = function () {
		if (xobj.readyState == 4 && xobj.status == "200") {
    		callback(xobj.responseText);
		}
	};
	xobj.send(null);  
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

function OnLoadWindow(_maxlines) {
	var logarea = document.getElementById('logarea');
	if (document.getElementById('autoscroll').checked) {
		logarea.scrollTop = logarea.scrollHeight;  
	}
	lines = logarea.value.split("\n").length;
	maxlines = _maxlines;
	Timer(1);
}

function OnUnloadWindow() {
	Timer(0);
}