var nIntervId = 0;
var TimerOn = 0;
var route = "";

var TimePicker = null;

function getTimers() {
  loadJSON(route+'/status/_gettimers', handleValues);
}

function handleValues(resp) {
  var values = JSON.parse(resp);
  document.getElementById('now').value=values.time;
  document.getElementById('status').value=values.status;
  document.getElementById('sunrise').value=values.riseset[0];
  document.getElementById('sunset').value=values.riseset[1];
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

function Timer(Value) {
  if (Value == 0) {
    clearInterval(nIntervId);
    TimerOn = 0;
  } else if (Value == 1) {
    clearInterval(nIntervId);
    nIntervId = setInterval(getTimers, 1000);
    TimerOn = 1;
  } else {
    clearInterval(nIntervId);
    nIntervId = setInterval(getTimers, 1000);
    TimerOn = 2;
  }
}

function ActiveChanged() {
  if (document.getElementById('ValActive').checked) {
    document.getElementById('ValActive').parentNode.getElementsByTagName('span')[0].innerHTML = "True";
    document.getElementById("Time").disabled = false;
  } else {
    document.getElementById('ValActive').parentNode.getElementsByTagName('span')[0].innerHTML = "False";
    document.getElementById("Time").disabled = true;
  }
}

function OnLoadWindow(rt) {
  route=rt;
  getTimers();
  Timer(1);
}

function OnUnloadWindow() {
  Timer(0);
}

function LoadPicker(datum, format) {
  if (datum[4] == 'True') {
    document.getElementById('ValActive').checked = true;
  } else {
    document.getElementById('ValActive').checked = false;
  }
  ActiveChanged();
  TimePicker = new Pikatime(
  {
    field: document.getElementById('Time'),
    format: format
  });
  TimePicker.setTimeFmt(datum[3]);
}