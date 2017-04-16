#!/bin/bash
INSTALL="/usr/bin/install -c"
INSTALL_DATA="$INSTALL -m 666"
INSTALL_PROGRAM="cp -r *"
NAME="Domotion"
ETCDIR="/etc"
ETCLOC="$ETCDIR/$NAME"
DB_NAME="$NAME.db"
EMPTY_DB_NAME="$NAME.empty.db"
OPTDIR="/opt"
OPTLOC="$OPTDIR/$NAME"
SYSTEMDDIR="./systemd"
SERVICEDIR="$ETCDIR/systemd/system"
SERVICESCRIPT="$NAME.service"
DAEMON="$NAME"

if [ "$EUID" -ne 0 ]
then 
	echo "Please execute as root ('sudo install.sh')"
	exit
fi

if [ "$1" == "-u" ] || [ "$1" == "-U" ]
then
	echo "$NAME uninstall script"

	echo "Uninstalling daemon $NAME"
	systemctl stop "$SERVICESCRIPT"
	systemctl disable "$SERVICESCRIPT"
	if [ -e "$SERVICEDIR/$SERVICESCRIPT" ]; then rm -f "$SERVICEDIR/$SERVICESCRIPT"; fi
	if [ -e "$BINDIR/$DAEMON" ]; then rm -f "$BINDIR/$DAEMON"; fi
	
	echo "Uninstalling $NAME"
	if [ -d "$OPTLOC" ]; then rm -rf "$OPTLOC"; fi
	
else
	echo "$NAME install script"

	echo "Stop running services"
	systemctl stop $SERVICESCRIPT
    systemctl disable $SERVICESCRIPT

	echo "Installing $NAME"

	if [ ! -d "$OPTLOC" ]; then 
		mkdir "$OPTLOC"
		chmod 777 "$OPTLOC"
	fi
	$INSTALL_PROGRAM $OPTLOC

	echo "Installing $DB_NAME"
	if [ ! -d "$ETCLOC" ]; then 
		mkdir "$ETCLOC" 
		chmod 777 "$ETCLOC"
	fi
	if [ ! -e "$ETCLOC/$DB_NAME" ]; then 
		$INSTALL_DATA "./$EMPTY_DB_NAME" "$ETCLOC/$DB_NAME"
	fi

	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' sqlite3|grep "install ok installed")
	echo Checking for sqlite3: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
  		echo "No sqlite3. Setting up sqlite3."
  		sudo apt-get --force-yes --yes install sqlite3
	fi

	echo "Installing required python packages"
	PKG_OK=$(sudo -H pip freeze| grep -i "Enum==")
	echo Checking for Enum: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
  		echo "No Enum. Setting up Enum."
		sudo -H pip install enum
	fi
	PKG_OK=$(sudo -H pip freeze| grep -i "Flask==")
	echo Checking for Flask: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
  		echo "No Flask. Setting up Flask."
		sudo -H pip install flask
	fi
	PKG_OK=$(sudo -H pip freeze| grep -i "Flask-Login==")
	echo Checking for Flask-Login: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
  		echo "No Flask-Login. Setting up Flask-Login."
		sudo -H pip install flask-login
	fi
	PKG_OK=$(sudo -H pip freeze| grep -i "psutil==")
	echo Checking for psutil: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
  		echo "No psutil. Setting up psutil."
		sudo -H pip install psutil
	fi

	echo "Installing daemon $NAME"

	read -p "Do you want to install an automatic startup service for $NAME (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
    	echo "Skipping install automatic startup service for $NAME"
    else
    	echo "Install automatic startup service for $NAME"
		$INSTALL_DATA "$SYSTEMDDIR/$SERVICESCRIPT" "$SERVICEDIR/$SERVICESCRIPT"

		systemctl enable $SERVICESCRIPT
		systemctl start $SERVICESCRIPT
	fi
fi




