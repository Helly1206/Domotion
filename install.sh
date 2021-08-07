#!/bin/bash
INSTALL="/usr/bin/install -c"
INSTALL_DATA="$INSTALL -m 644"
INSTALL_PROGRAM="$INSTALL"
INSTALL_FOLDER="cp -r"
NAME="Domotion"
WEBNAME="DomoWeb"
APPSNAME="DomoApps"
WEBSTARTER="$WEBNAME""Starter"
APPSSTARTER="$APPSNAME""Starter"
RETMOVE="RetainerMove"
ETCDIR="/etc"
ETCLOC="$ETCDIR/$NAME"
SCRIPTS="scripts"
ETCSCRIPTS="$ETCLOC/$SCRIPTS"
INSTALL_SCRIPTS="cp -r .$ETCSCRIPTS/* $ETCSCRIPTS"
DB_NAME="$NAME.db"
EMPTY_DB_NAME="$NAME.empty.db"
XML_NAME="$WEBNAME.xml"
OPTDIR="/opt"
OPTLOC="$OPTDIR/$NAME"
SYSTEMDDIR="./systemd"
SERVICEDIR="$ETCDIR/systemd/system"
SERVICESCRIPT="$NAME.service"
WEBSERVICESCRIPT="$WEBNAME.service"
APPSSERVICESCRIPT="$APPSNAME.service"
PIP_INSTALL="$OPTLOC/pip_install.sh"
DEBFOLDER="debian"
SCRIPTSCACHE="$ETCDIR/$NAME/process/__pycache__"

if [ "$EUID" -ne 0 ]
then
	echo "Please execute as root ('sudo install.sh')"
	exit
fi

if [ "$1" == "-u" ] || [ "$1" == "-U" ]
then
	echo "$NAME uninstall script"

	echo "Uninstalling service $NAME"
	systemctl stop "$SERVICESCRIPT"
	systemctl disable "$SERVICESCRIPT"
	if [ -e "$SERVICEDIR/$SERVICESCRIPT" ]; then rm -f "$SERVICEDIR/$SERVICESCRIPT"; fi

	echo "Uninstalling service $WEBNAME"
	systemctl stop "$WEBSERVICESCRIPT"
	systemctl disable "$WEBSERVICESCRIPT"
	if [ -e "$SERVICEDIR/$WEBSERVICESCRIPT" ]; then rm -f "$SERVICEDIR/$WEBSERVICESCRIPT"; fi

	echo "Uninstalling service $APPSNAME"
	systemctl stop "$APPSSERVICESCRIPT"
	systemctl disable "$APPSSERVICESCRIPT"
	if [ -e "$SERVICEDIR/$APPSSERVICESCRIPT" ]; then rm -f "$SERVICEDIR/$APPSSERVICESCRIPT"; fi

	echo "Uninstalling $NAME"
	if [ -d "$OPTLOC" ]; then rm -rf "$OPTLOC"; fi

    py3clean "$OPTLOC"
    if [ -d "$SCRIPTSCACHE" ]; then
        rm -rf "$SCRIPTSCACHE"
    fi
elif [ "$1" == "-h" ] || [ "$1" == "-H" ]
then
	echo "Usage:"
	echo "  <no argument>: install Domotion"
	echo "  -u/ -U       : uninstall Domotion"
	echo "  -h/ -H       : this help file"
    echo "  -d/ -D       : build debian package"
	echo "  -c/ -C       : Cleanup compiled files in install folder"
    echo ""
    echo "Apache2 install is removed from this install script"
    echo "To install apach2 web deployment, run /opt/Domotion/apach2_install.sh"
elif [ "$1" == "-c" ] || [ "$1" == "-C" ]
then
	echo "$NAME Deleting compiled files in install folder"
	py3clean .
    rm -f ./*.deb
	rm -rf "$DEBFOLDER"/${NAME,,}
	rm -rf "$DEBFOLDER"/.debhelper
	rm -f "$DEBFOLDER"/files
	rm -f "$DEBFOLDER"/files.new
	rm -f "$DEBFOLDER"/${NAME,,}.*
elif [ "$1" == "-d" ] || [ "$1" == "-D" ]
then
	echo "$NAME build debian package"
	py3clean .
	fakeroot debian/rules clean binary
	mv ../*.deb .
else
	echo "$NAME install script"

	echo "Stop running services"
	systemctl stop $SERVICESCRIPT
	systemctl disable $SERVICESCRIPT
	systemctl stop $WEBSERVICESCRIPT
	systemctl disable $WEBSERVICESCRIPT
	systemctl stop $APPSSERVICESCRIPT
	systemctl disable $APPSSERVICESCRIPT

	echo "Installing $NAME"

	py3clean .

	if [ -d "$OPTLOC" ]; then rm -rf "$OPTLOC"; fi
	if [ ! -d "$OPTLOC" ]; then
		mkdir "$OPTLOC"
		chmod 755 "$OPTLOC"
	fi

	$INSTALL_FOLDER ".$OPTLOC/*" $OPTLOC
	$INSTALL_PROGRAM ".$OPTLOC/$NAME" $OPTLOC
	$INSTALL_PROGRAM ".$OPTLOC/$WEBSTARTER" $OPTLOC
	$INSTALL_PROGRAM ".$OPTLOC/$APPSSTARTER" $OPTLOC
	$INSTALL_PROGRAM ".$OPTLOC/$RETMOVE" $OPTLOC
	$INSTALL_PROGRAM ".$OPTLOC/$A2CONFIG" $OPTLOC
	$INSTALL_PROGRAM ".$OPTLOC/${0##*/}" $OPTLOC

	echo "Installing $DB_NAME"
	if [ ! -d "$ETCLOC" ]; then
		mkdir "$ETCLOC"
		chmod 755 "$ETCLOC"
	fi
	if [ ! -e "$ETCLOC/$DB_NAME" ]; then
		$INSTALL_DATA ".$ETCLOC/$DB_NAME" "$ETCLOC/$DB_NAME"
	fi

	echo "Installing $XML_NAME"
	if [ ! -e "$ETCLOC/$XML_NAME" ]; then
		$INSTALL_DATA ".$ETCLOC/$XML_NAME" "$ETCLOC/$XML_NAME"
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

    py3clean "$OPTLOC"
    if [ -d "$SCRIPTSCACHE" ]; then
        rm -rf "$SCRIPTSCACHE"
    fi

    source "$PIP_INSTALL"

	echo "Installing service $NAME"
	read -p "Do you want to install an automatic startup service for $NAME (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
		echo "Skipping install automatic startup service for $NAME"
	else
		echo "Install automatic startup service for $NAME"
		$INSTALL_DATA ".$SERVICEDIR/$SERVICESCRIPT" "$SERVICEDIR/$SERVICESCRIPT"

		systemctl enable $SERVICESCRIPT
		systemctl start $SERVICESCRIPT
	fi

	echo "Installing service $WEBNAME"
	read -p "Do you want to install an automatic startup service for $WEBNAME (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
		echo "Skipping install automatic startup service for $WEBNAME"
	else
		echo "Install automatic startup service for $WEBNAME"
		$INSTALL_DATA ".$SERVICEDIR/$WEBSERVICESCRIPT" "$SERVICEDIR/$WEBSERVICESCRIPT"

		systemctl enable $WEBSERVICESCRIPT
		systemctl start $WEBSERVICESCRIPT
	fi

	echo "Installing service $APPSNAME"
	read -p "Do you want to install an automatic startup service for $APPSNAME (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
		echo "Skipping install automatic startup service for $APPSNAME"
	else
		echo "Install automatic startup service for $APPSNAME"
		$INSTALL_DATA ".$SERVICEDIR/$APPSSERVICESCRIPT" "$SERVICEDIR/$APPSSERVICESCRIPT"

		systemctl enable $APPSSERVICESCRIPT
		systemctl start $APPSSERVICESCRIPT
	fi
fi
