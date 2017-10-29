#!/bin/bash
INSTALL="/usr/bin/install -c"
INSTALL_DATA="$INSTALL -m 644"
INSTALL_PROGRAM="$INSTALL"
INSTALL_FOLDER="cp -r *"
NAME="Domotion"
WEBNAME="DomoWeb"
WEBSTARTER="$WEBNAME""Starter"
RETMOVE="RetainerMove"
ETCDIR="/etc"
ETCLOC="$ETCDIR/$NAME"
SCRIPTS="scripts"
ETCSCRIPTS="$ETCLOC/$SCRIPTS"
INSTALL_SCRIPTS="cp -r $scripts/* $ETCSCRIPTS"
DB_NAME="$NAME.db"
EMPTY_DB_NAME="$NAME.empty.db"
XML_NAME="$WEBNAME.xml"
OPTDIR="/opt"
OPTLOC="$OPTDIR/$NAME"
SYSTEMDDIR="./systemd"
SERVICEDIR="$ETCDIR/systemd/system"
SERVICESCRIPT="$NAME.service"
WEBSERVICESCRIPT="$WEBNAME.service"
WEB_ROOT="/var/www"
DOMOWEB_ROOT="$WEB_ROOT/$NAME"
WEBLOC="./webif"
INSTALL_WEB="cp -r $WEBLOC/*"
A2CONFIG="Apache2Config"

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

	echo "Uninstalling daemon $WEBNAME"
	systemctl stop "$WEBSERVICESCRIPT"
	systemctl disable "$WEBSERVICESCRIPT"
	if [ -e "$SERVICEDIR/$WEBSERVICESCRIPT" ]; then rm -f "$SERVICEDIR/$WEBSERVICESCRIPT"; fi
	
	echo "Uninstalling $NAME"
	if [ -d "$OPTLOC" ]; then rm -rf "$OPTLOC"; fi
elif [ "$1" == "-h" ] || [ "$1" == "-H" ]
then
	echo "Usage:"
	echo "  <no argument>: install Domotion"
	echo "  -u/ -U       : uninstall Domotion"
	echo "  -h/ -H       : this help file"
	echo "  -a/ -A       : install Apache2 WSGI web deployment"
	echo "  -b/ -B       : uninstall Apache2 WSGI web deployment" 
	echo "  -c/ -C       : Cleanup compiled files in install folder"
elif [ "$1" == "-c" ] || [ "$1" == "-C" ]
then
	echo "$NAME Deleting compiled files in install folder"
	find . -name "*.pyc" -type f -delete
elif [ "$1" == "-a" ] || [ "$1" == "-A" ]
then
	echo "$NAME Apache2 install script"
	echo "Take care that you open the required ports when runnning ufw or another firewall"

	echo "Check required packages"
	
	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' apache2|grep "install ok installed")
	echo Checking for apache2: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
		echo "No apache2. Setting up apache2."
		sudo apt-get --force-yes --yes install apache2
	fi

	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' libapache2-mod-wsgi|grep "install ok installed")
	echo Checking for libapache2-mod-wsgi: $PKG_OK
	if [ "" == "$PKG_OK" ]; then
		echo "No libapache2-mod-wsgi. Setting up libapache2-mod-wsgi."
		sudo apt-get --force-yes --yes install libapache2-mod-wsgi
	fi

	echo "Enabling wsgi and ssl modules"
	a2enmod wsgi &> /dev/null
	a2enmod ssl &> /dev/null

	echo "Installing $NAME on $WEB_ROOT"
	if [ ! -d "$DOMOWEB_ROOT" ]; then 
		mkdir "$DOMOWEB_ROOT" 
	fi

	$INSTALL_WEB "$DOMOWEB_ROOT"

	echo "Configuring apache2"
	./$A2CONFIG

elif [ "$1" == "-b" ] || [ "$1" == "-B" ]
then
	echo "$NAME Apache2 uninstall script"
	echo "WARNING: Apache2 itself is not uninstalled, evenso conf files are not removed"
	echo "         If you want to do so, remove all externaldeployment entries"
	echo "         in /etc/Domotion/DomoWeb.xml and then run sudo ./install.sh -a"
	echo "         This uninstaller only removes Domotion files from apache's www folder"
	read -p "Do you want to continue (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
		echo "Skipping Apache2 uninstall script"
	else
		echo "Running Apache2 uninstall script"
		echo "Uninstalling $NAME from $WEB_ROOT"

		if [ -d "$DOMOWEB_ROOT" ]; then rm -rf "$DOMOWEB_ROOT"; fi
	fi
else
	echo "$NAME install script"

	echo "Stop running services"
	systemctl stop $SERVICESCRIPT
	systemctl disable $SERVICESCRIPT
	systemctl stop $WEBSERVICESCRIPT
	systemctl disable $WEBSERVICESCRIPT

	echo "Installing $NAME"

	find . -name "*.pyc" -type f -delete

	if [ ! -d "$OPTLOC" ]; then 
		mkdir "$OPTLOC"
		chmod 755 "$OPTLOC"
	fi

	$INSTALL_FOLDER $OPTLOC
	$INSTALL_PROGRAM "./$NAME" $OPTLOC
	$INSTALL_PROGRAM "./$WEBSTARTER" $OPTLOC
	$INSTALL_PROGRAM "./$RETMOVE" $OPTLOC
	$INSTALL_PROGRAM "./$A2CONFIG" $OPTLOC
	$INSTALL_PROGRAM "./${0##*/}" $OPTLOC

	echo "Installing $DB_NAME"
	if [ ! -d "$ETCLOC" ]; then 
		mkdir "$ETCLOC" 
		chmod 755 "$ETCLOC"
	fi
	if [ ! -e "$ETCLOC/$DB_NAME" ]; then 
		$INSTALL_DATA "./$EMPTY_DB_NAME" "$ETCLOC/$DB_NAME"
	fi

	echo "Installing $XML_NAME"
	if [ ! -e "$ETCLOC/$XML_NAME" ]; then 
		$INSTALL_DATA "./$XML_NAME" "$ETCLOC/$XML_NAME"
	fi

	if [ ! -d "$ETCSCRIPTS" ]; then
		mkdir "$ETCSCRIPTS"
		chmod 755 "$ETCSCRIPTS"
		#INSTALL_SCRIPTS
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

	echo "Installing daemon $WEBNAME"
	read -p "Do you want to install an automatic startup service for $WEBNAME (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
		echo "Skipping install automatic startup service for $WEBNAME"
	else
		echo "Install automatic startup service for $WEBNAME"
		$INSTALL_DATA "$SYSTEMDDIR/$WEBSERVICESCRIPT" "$SERVICEDIR/$WEBSERVICESCRIPT"

		systemctl enable $WEBSERVICESCRIPT
		systemctl start $WEBSERVICESCRIPT
	fi
fi
