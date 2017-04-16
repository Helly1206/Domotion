function TFChanged(id) {
	if (document.getElementById(id).checked) {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "True";
	} else {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "False";
	}
}

function TFSet(id,check) {
	if (check.toLowerCase() == "true") {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "True";
		document.getElementById(id).checked = true;
	} else {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "False";
		document.getElementById(id).checked = false;
	}
}

function OOChanged(id) {
	if (document.getElementById(id).checked) {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "On";
	} else {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "Off";
	}
}

function OOSet(id,check) {
	if (check.toLowerCase() == "true") {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "On";
		document.getElementById(id).checked = true;
	} else {
		document.getElementById(id).parentNode.getElementsByTagName('span')[0].innerHTML = "Off";
		document.getElementById(id).checked = false;
	}
}

function SensorTypeChanged() {
	var e = document.getElementById("SensorType");
	var val = e.options[e.selectedIndex].text;
	SensorDisableByType(val);
	SensorDefaultToggleByType(val);
}

function dSensorTypeChanged() {
	var e = document.getElementById("dSensorType");
	var val = e.options[e.selectedIndex].text;
	SensorDisableBydType(val);
}

function SensorDisableBydType(val) {
	if (val.toLowerCase() == "key") {
		document.getElementById("TF3").disabled = false;
	} else {
		document.getElementById("TF3").disabled = true;
	}
}

function SensorDisableByType(val) {
	if ((val.toLowerCase().includes("domoticz")) || (val.toLowerCase().includes("gpio"))) {
		document.getElementById("sSysCode").disabled = true;
		document.getElementById("sGroupCode").disabled = true;
		document.getElementById("sDeviceCode").disabled = false;
		document.getElementById("sURL").disabled = true;
		document.getElementById("sTag").disabled = true;
	} else if ((val.toLowerCase().includes("rf")) || (val == '-')) {
		document.getElementById("sSysCode").disabled = false;
		document.getElementById("sGroupCode").disabled = false;
		document.getElementById("sDeviceCode").disabled = false;
		document.getElementById("sURL").disabled = true;
		document.getElementById("sTag").disabled = true;
	} else {
		document.getElementById("sSysCode").disabled = true;
		document.getElementById("sGroupCode").disabled = true;
		document.getElementById("sDeviceCode").disabled = true;
		document.getElementById("sURL").disabled = false;
		document.getElementById("sTag").disabled = false;
	}
}

function SensorDefaultToggleByType(val) {
	if (val.toLowerCase().includes("ir")) {
		TFSet("TF3", "true")
	} else {
		TFSet("TF3", "false")
	}
}

function ActuatorTypeChanged() {
	var e = document.getElementById("ActuatorType");
	var val = e.options[e.selectedIndex].text;
	ActuatorDisableByType(val);
}

function ActuatorDisableByType(val) {
	if (val.toLowerCase() == "buffer output") {
		document.getElementById("SysCode").disabled = true;
		document.getElementById("GroupCode").disabled = true;
		document.getElementById("DeviceCode").disabled = true;
		document.getElementById("URL").disabled = true;
		document.getElementById("Tag").disabled = true;
	} else if ((val.toLowerCase() == "timer output") || (val.toLowerCase().includes("domoticz")) || (val.toLowerCase().includes("gpio"))) {
		document.getElementById("SysCode").disabled = true;
		document.getElementById("GroupCode").disabled = true;
		document.getElementById("DeviceCode").disabled = false;
		document.getElementById("URL").disabled = true;
		document.getElementById("Tag").disabled = true;
	} else if ((val.toLowerCase().includes("rf")) || (val == '-')) {
		document.getElementById("SysCode").disabled = false;
		document.getElementById("GroupCode").disabled = false;
		document.getElementById("DeviceCode").disabled = false;
		document.getElementById("URL").disabled = true;
		document.getElementById("Tag").disabled = true;
	} else {
		document.getElementById("SysCode").disabled = true;
		document.getElementById("GroupCode").disabled = true;
		document.getElementById("DeviceCode").disabled = true;
		document.getElementById("URL").disabled = false;
		document.getElementById("Tag").disabled = false;
	}
}

function TimerMethodChanged() {
	var e = document.getElementById("TimerMethod");
	var val = e.options[e.selectedIndex].text;
	TimerDisableByMethod(val);
}

function TimerDisableByMethod(val) {
	if (val.toLowerCase() == "fixed") {
		document.getElementById("Hour").disabled = false;
		document.getElementById("Minute").disabled = false;
		document.getElementById("MinutesOffset").disabled = true;
	} else {
		document.getElementById("Hour").disabled = true;
		document.getElementById("Minute").disabled = true;
		document.getElementById("MinutesOffset").disabled = false;
	}
}

function TimerSetTime(time) {
	res = time.split(":");
	document.getElementById("Hour").value = res[0];
	document.getElementById("Minute").value = res[1];
}

function ProcSensorChanged(sensors, digi) {
	var e = document.getElementById("ProcSensor");
	var val = e.options[e.selectedIndex].text;				
	var IsDigital = false;

	for (key in sensors) {
		if (sensors[key][1].toLowerCase() == val.toLowerCase()) {
			IsDigital=digi[key][1];
		}
	}

	if (IsDigital) {
		document.getElementById("ProcOp").hidden = true;
		document.getElementById("ProcEq").hidden = false;
		document.getElementById("ProcVal").hidden = true;
		document.getElementById("ProcValTF").hidden = false;
	} else {
		document.getElementById("ProcOp").hidden = false;
		document.getElementById("ProcEq").hidden = true;
		document.getElementById("ProcVal").hidden = false;
		document.getElementById("ProcValTF").hidden = true;
	}
}

function DepActuatorChanged(index, actuators, digi) {
	var e = document.getElementById("DepActuator"+index);
	var val = e.options[e.selectedIndex].text;				
	var IsDigital = false;

	for (key in actuators) {
		if (actuators[key][1].toLowerCase() == val.toLowerCase()) {
			IsDigital=digi[key][1];
		}
	}

	if (IsDigital) {
		document.getElementById("DepOp"+index).hidden = true;
		document.getElementById("DepEq"+index).hidden = false;
		document.getElementById("DepVal"+index).hidden = true;
		document.getElementById("DepValTF"+index).hidden = false;
	} else {
		document.getElementById("DepOp"+index).hidden = false;
		document.getElementById("DepEq"+index).hidden = true;
		document.getElementById("DepVal"+index).hidden = false;
		document.getElementById("DepValTF"+index).hidden = true;
	}
}

function CombActuatorChanged(index, actuators, digi) {
	var e = document.getElementById("CombActuator"+index);
	var val = e.options[e.selectedIndex].text;
	var IsDigital = false;

	for (key in actuators) {
		if (actuators[key][1].toLowerCase() == val.toLowerCase()) {
			IsDigital=digi[key][1];
		}
	}

	if (IsDigital) {
		document.getElementById("CombVal"+index).hidden = true;
		document.getElementById("CombValOO"+index).hidden = false;
	} else {
		document.getElementById("CombVal"+index).hidden = false;
		document.getElementById("CombValOO"+index).hidden = true;
	}
}

function OnLoadWindow(id,datum) { /* do stuff on page load */ 
	if (id == "sensors") {
		SensorDisableByType(datum[3]);
		SensorDisableBydType(datum[9]);
		TFSet("TF2",datum[10]);
		TFSet("TF3",datum[11]);
	} else if (id == "actuators") {
		ActuatorDisableByType(datum[3]);
		TFSet("TF4",datum[9]);
		TFSet("TF5",datum[10]);
		TFSet("TF6",datum[12]);
	} else if (id == "timers") {
		TimerDisableByMethod(datum[3]);
		TimerSetTime(datum[4]);
	} else if (id == "combiners") {
		TFSet("TF7",datum[4]);
	}
}