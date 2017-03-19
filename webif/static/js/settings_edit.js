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

function PWChanged() {
	pw1 = document.getElementById("PW1").value;
	pw2 = document.getElementById("PW2").value;
	if (pw1 == pw2) {
		document.getElementById("OkButton").disabled = false;
		document.getElementById("PW1").style.backgroundColor = "white";
		document.getElementById("PW2").style.backgroundColor = "white";
	} else {
		document.getElementById("OkButton").disabled = true;
		document.getElementById("PW1").style.backgroundColor = "red";
		document.getElementById("PW2").style.backgroundColor = "red";
	}
}

function OnLoadWindow(format, datum) { /* do stuff on page load */ 
	if (format == "BOOL") {
    	TFSet("TFBV",datum[3]);
	} else if (format == "PDSTRING") {
		
	} else if (format == "PSTRING") {
		
	}
}