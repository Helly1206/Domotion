var nIntervId = 0;
var TimerOn = 0;
var route = "";

var StartPicker = null;
var EndPicker = null;

function getHolidays() {
  loadJSON(route+'/status/_getholidays', handleValues);
}

function handleValues(resp) {
  var values = JSON.parse(resp);
  document.getElementById('now').value=values.time;
  document.getElementById('status').value=values.status;
  document.getElementById('today').value=values.today;
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
    nIntervId = setInterval(getHolidays, 1000);
    TimerOn = 1;
  } else {
    clearInterval(nIntervId);
    nIntervId = setInterval(getHolidays, 1000);
    TimerOn = 2;
  }
}

function DateChanged() {
  var start;
  var end;
  if (StartPicker) {
    start = StartPicker.getDate().valueOf();  
  } else {
    start = new Date().valueOf();
  }
  if (EndPicker) {
    end = EndPicker.getDate().valueOf();
  } else {
    end = new Date().valueOf();
  } 
  if (start > end) {
    EndPicker.setDate(StartPicker.getDate());
  }
}

function OnLoadWindow(rt) {
  route=rt;
  getHolidays();
  Timer(1);
}

function OnUnloadWindow() {
  Timer(0);
}

function LoadPicker(datum, format) {
  StartPicker = new Pikaday(
  {
    field: document.getElementById('Start'),
    format: format
  });
  StartPicker.setDateFmt(datum[2]);
  EndPicker = new Pikaday(
  {
    field: document.getElementById('End'),
    format: format
  });
  EndPicker.setDateFmt(datum[3]);
}