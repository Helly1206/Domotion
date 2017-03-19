var nIntervId = 0;
var TimerOn = 0;
var TableId = "None";
var EditId = 0;
var LoadEdit = false;

function getTimers() {
  loadJSON('/status/_gettimers/'+TableId, handleValues);
}

function setTimer(id,value) {
  Timer(0);
  var uri='/status/_gettimers/'+TableId+BuildGetRequest(id,value);
  loadJSON(uri, handleValues);
}

function handleValues(resp) {
  var values = JSON.parse(resp);
  document.getElementById('time').value=values.time;
  document.getElementById('status').value=values.status;
  document.getElementById('sunrise').value=values.riseset[0];
  document.getElementById('sunset').value=values.riseset[1];

  for (key in values.values) {
    if (values.values[key] >=0) {
      TimeSet(key,values.values[key]);
      ActiveSet(key, true);
    } else {
      ActiveSet(key, false);
    }
  }
  if (TimerOn < 2) {
    Timer(TimerOn+1);
  }
  if (LoadEdit) {
    LoadEdit = false;
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
    nIntervId = setInterval(getTimers, 1000);
    TimerOn = 1;
  } else {
    clearInterval(nIntervId);
    nIntervId = setInterval(getTimers, 1000);
    TimerOn = 2;
  }
}

function TimeSet(id, value) {
  var iid='Time'+id;
  h=~~(value/60);
  if (h<10) {
    h="0"+h;
  }
  m=value%60;
  if (m<10) {
    m="0"+m;
  }
  if (id==EditId) {
    if (LoadEdit) {
      document.getElementById("Hour").value = h;
      document.getElementById("Minute").value = m;
    }
  } else {
    document.getElementById(iid).innerHTML=h+':'+m;
  }
}

function TimeSetEdit(time) {
  res = time.split(":");
  document.getElementById("Hour").value = res[0];
  document.getElementById("Minute").value = res[1];
}

function ActiveSet(id, value) {
  var iid='Active'+id;

  if (id==EditId) {
    if (LoadEdit) {
      if (value) {
        document.getElementById('ValActive').parentNode.getElementsByTagName('span')[0].innerHTML = "True";
        document.getElementById('ValActive').checked = true;
        document.getElementById("Hour").disabled = false;
        document.getElementById("Minute").disabled = false;
      } else {
        document.getElementById('ValActive').parentNode.getElementsByTagName('span')[0].innerHTML = "False";
        document.getElementById('ValActive').checked = false;
        document.getElementById("Hour").disabled = true;
        document.getElementById("Minute").disabled = true;
      }
    }
  } else {
    if (value) {
      document.getElementById(iid).innerHTML='True';
    } else {
      document.getElementById(iid).innerHTML='False';
    }
  }
}

function ActiveChanged() {
  if (document.getElementById('ValActive').checked) {
    document.getElementById('ValActive').parentNode.getElementsByTagName('span')[0].innerHTML = "True";
    document.getElementById("Hour").disabled = false;
    document.getElementById("Minute").disabled = false;
  } else {
    document.getElementById('ValActive').parentNode.getElementsByTagName('span')[0].innerHTML = "False";
    document.getElementById("Hour").disabled = true;
    document.getElementById("Minute").disabled = true;
  }
}

function OkClicked() {
  if (document.getElementById('ValActive').checked) {
    h = document.getElementById("Hour").value;
    m = document.getElementById("Minute").value;
    value = (60*parseInt(h)+parseInt(m));
  } else {
    value = -1;
  }
  if (EditId > 0) {
    setTimer(EditId,value)
  }
  CancelClicked();
}

function CancelClicked() {
  window.location.replace("/status/"+TableId);
}

/*function SNChanged(id) {
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

function SButtonClicked(id) {
  var iid='SButtond'+id;
  var value = 0;
  var curval = document.getElementById(iid).innerHTML;
  if (curval== "Off") {
    document.getElementById(iid).innerHTML="On";
    var value = 1;
  } else {
    document.getElementById(iid).innerHTML="Off";
    var value = 0;
  }
  
  setValue(id, value);
}

function SButtonSet(id, value) {
  var iid='SButtond'+id;
  if (value) {
    document.getElementById(iid).innerHTML="On";
  } else {
    document.getElementById(iid).innerHTML="Off";
  }
} */     

function OnLoadWindow(tid, id) {
  Timer(2);
  TableId=tid;
  if (id>0) {
    EditId=id;
    LoadEdit = true;
  } else {
    EditId=0;
    LoadEdit = false;
  }
}

function OnUnloadWindow() {
  Timer(0);
  TableId="None";
  EditId=0;
  LoadEdit = false;
}