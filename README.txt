Domotion v1.1.2

Domotion Home Control and Automation
======== ==== ======= === ==========

Domotion is a domotics framework, designed for the Raspberry PI running Linux (Raspbian), but can also be used on other Linux platforms that have python installed.

Domotion is especially designed for people who are designing their own hardware or are using cheap hardware (like 433MHz senders and rceivers from Ebay, GPIO, Lirc for remote control etc.)

Flows (called processes in domotion) can be desgined without programming. So you can e.g. switch on a light 10 minutes after a sensor is detected. A detailed manual is yet to come, but here is already some termonology:

- Sensor: A button to click or an analog sensor. A buuton sensor is released after the corresponding action is executed.
- Actuator: An output that needs to be set. This can be a digital switch, an analog sensors, a dummy (for test or further processing) or a timer that is activated on a specific action. Actuators can be set directly, or after processing a sensor or timer event.
- Timer: A timer that can be used to execute an action on a specific moment. A timer can be fixed, based on sunrise or sunset or be an offset to be activated by an actuator.
- Processor: A processor links a combiner when a specific sensor is activated or a timer is fired.
- Dependency: A dependency decides whether or not a combiner will do it's job, based on some outputs. (e.g. always switch off the lights at 11 P.M. except when watching TV at that time.)
- Combiner: A combiner checks whether the dependency passes (or failes) and sets u to 16 outputs. 

Domotion has a domoticz interface to be able to interact with domoticz (and use Domotion for interfaces where domoticz doesn't have a solution for), so the domoticz user interface can be used to control Domotion. Sensors and Actuators that are changed in Domotion are automatically updated in domoticz when there is a connection.

Installation:
-------------
- Browse to: https://github.com/Helly1206/Domotion
- Click the 'Clone or Download' button
- Click 'Download Zip'
- Unzip the zip file to a temporary location
- Open a terminal at this location
- Enter: 'sudo ./install.sh'
- Wait and answer the questions:
	Do you want to install an automatic startup service for Domotion (Y/n)?
   		Default = Y
   		If you want to automatically start Domotion during startup (or don't know), answer Y to this question.
   		If you do not want to install an automatic startup script, answer N to this question.
   	Do you want to install an automatic startup service for Domotion Web Server (Y/n)?
   		Default = Y
   		If you want to automatically start Domotion Web Server during startup (or don't know), answer Y to this question.
   		If you do not want to install an automatic startup script, answer N to this question.

Manually run Domotion:
-------- --- ---------
When you didn't install an automaitc startup service for Domotion
- Run by /opt/Domotion/Domotion

Usage for special options:
         Domotion <args>
         -h, --help: this help file
         -v, --version: print version information

Domotion webserver(s):
-------- -------------
Configure your webserver(s) in /etc/DomoWeb.xml. You can add a maximum of 5 webservers.
Example:
<servers>
	<httpserver>
		<ssl>false</ssl>
		<port>8090</port>
		<certificate></certificate>
		<privatekey></privatekey>
		<externaldeployment>false</externaldeployment>
		<serveradmin>admin@localhost</serveradmin>
		<servername>localhost</servername>
	</httpserver>
	<httpsserver>
		<ssl>true</ssl>
		<port>4043</port>
		<certificate>/etc/letsencrypt/live/example.com/cert.pem</certificate>
		<privatekey>/etc/letsencrypt/live/example.com/privkey.pem</privatekey>
		<externaldeployment>false</externaldeployment>
		<serveradmin>admin@localhost</serveradmin>
		<servername>localhost</servername>
	</httpsserver>
</servers>

When not using external deployment, please enter:
sudo systemctl restart DomoWeb.service

Manually starting the webserver(s):
-------- -------- --- -------------
When you didn't install an automaitc startup service for Domotion Web Server
- Run by /opt/Domotion/DomoWebStarter

Usage for special options:
         DomoWebStarter <args>
         -h, --help: this help file
         -d, --debug: start in debug mode on port 5000

External deployment of webserver by Apache2:
-------- ---------- -- --------- -- --------
Exernal deployment can be used to deploy the webserver on an external server like Apache2. A wsgi file is added for that purpose. When you like to use the Domotion webserver(s) for other purposes than testing, running on an Apache2 server is recommended. To make deploying of the webserver(s) by apache2 easier, an installation program is written, so you don't have to find out everything yourself. This installation program also is capable to add 'default' http and https servers. If you want to do special things, you do have to read the docs of Apache2 or a different webserver.

If you would like to use external deployment by Apache2:
- First make <externaldeployment> true for the required sites in /etc/DomoWeb.xml and take care that all the other fields are correctly filled in (e.g. when using ssl, make the servername equal to the website host).
- Enter: 'sudo ./install.sh -a'
- The webserver(s) are now installed in Apache2 and enabled. Take care that you open the required ports in the firewall when accessing from another computer.

Apps:
-----
Domotion is able to run apps from this version. For more information see the reame from the apps, e.g. 
https://github.com/Helly1206/Domo_app_weather

Installer options:
--------- --------
sudo ./install.sh    --> Installs Domotion
sudo ./install.sh -u --> Uninstalls Domotion
sudo ./install.sh -c --> Deletes compiled files in install folder (only required when copying or zipping the install folder)
sudo ./install.sh -a --> Install Apache2 and/ or configures Apache2 with the Domotion Webserver
sudo ./install.sh -b --> Removes the Domotion Webserver form the Apache2 folder, it doesn't uninstall Apache2, neither removes entries. Remove the entries in /etc/Domotion/DomoWeb.xml and run sudo ./install.sh -a to remove the entries first, before running sudo ./install.sh -b

Security:
---------
CAUTION: Domotion is as safe and secure as your system is. Notice that, especially when using Domotion for unlocking doors etc. there is a rather strong password encryption and secure HTTP is possible, but if someone is able to enter your harddisk, hacking may be possible.

That's all for now ...

Please send Comments and Bugreports to hellyrulez@home.nl