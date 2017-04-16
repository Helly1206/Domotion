var nIntervId = 0;
var TimerOn = 0;
var TableId = "None";

function getValues() {
  loadJSON('/status/_getvalues/'+TableId, handleValues);
}

function setValue(id,value) {
  Timer(0);
  var uri='/status/_getvalues/'+TableId+BuildGetRequest(id,value);
  loadJSON(uri, handleValues);
}

function handleValues(resp) {
  var values = JSON.parse(resp);
  document.getElementById('time').value=values.time;
  document.getElementById('status').value=values.status;

  for (key in values.values) {
    if (!SNHidden(key)) {
      SNSet(key,values.values[key]);
    } else {
      if (TableId == "devices") {
        SOOSet(key,values.values[key]);
      } else {
        SButtonSet(key,values.values[key]);
      }
    }
  }
  if (TimerOn < 2) {
    Timer(TimerOn+1);
  }
}

function BuildGetRequest(id, value) {
  return ("?Id="+id+"&Value="+value);
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
    nIntervId = setInterval(getValues, 2000);
    TimerOn = 1;
  } else {
    clearInterval(nIntervId);
    nIntervId = setInterval(getValues, 1000);
    TimerOn = 2;
  }
}

function SNChanged(id) {
  var iid='StatVal'+id;
  var value = document.getElementById(iid).value;

  setValue(id, value);
}

function SNSet(id, value) {
  var iid='StatVal'+id;
  if (document.getElementById(iid) !== document.activeElement) {
    document.getElementById(iid).value=value
  }
}

function SNHidden(id) {
  var iid='StatVal'+id;
  return document.getElementById(iid).hidden;
}

function SOOChanged(id) {
  var iid='SOOd'+id;
  var value = 0;
  if (document.getElementById(iid).checked) {
    document.getElementById(iid).parentNode.getElementsByTagName('span')[0].innerHTML = "On";
    value = 1;
  } else {
    document.getElementById(iid).parentNode.getElementsByTagName('span')[0].innerHTML = "Off";
    value = 0;
  }
  
  setValue(id, value);
}

function SOOSet(id, value) {
  var iid='SOOd'+id;
  if (value) {
    document.getElementById(iid).parentNode.getElementsByTagName('span')[0].innerHTML = "On";
    document.getElementById(iid).checked = true;
  } else {
    document.getElementById(iid).parentNode.getElementsByTagName('span')[0].innerHTML = "Off";
    document.getElementById(iid).checked = false;
  }
}

function SButtonClicked(id, value) {
  SButtonSet(id, value);
  setValue(id, value);
}

function SButtonSet(id, value) {
  var iid='SButtond'+id;
  if (value) {
    document.getElementById(iid).getElementsByTagName('span')[0].innerHTML="On";
  } else {
    document.getElementById(iid).getElementsByTagName('span')[0].innerHTML="Off";
  }
}      

function OnLoadWindow(tid) {
  Timer(2);
  TableId=tid;
}

function OnUnloadWindow() {
  Timer(0);
  TableId="None";
}