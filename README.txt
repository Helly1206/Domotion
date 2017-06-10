Domotion v0.9.8

Domotion Home Control and Automation

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
- Browse to: https://github.com/Helly1206/Domotion
- Click the 'Clone or Download' button
- Click 'Download Zip'
- Unzip the zip file to a temporary location
- Open a terminal at this location
- Enter: 'sudo ./install.sh'
- Wait and answer the question:
	Do you want to install an automatic startup service for Domotion (Y/n)?
   		Default = Y
   		If you want to automatically start Domotion during startup (or don't know), answer Y to this question.
   		If you do not want to install an automatic startup script, answer N to this question.

Manual run Domotion:
- Run by /opt/Domotion/Domotion

Usage for special options:
         Domotion <args>
         -h: help: this help file
         -d: default: run on port 5000 with no login (for debugging)
         -n: no-login: run with no login (for forgotten password)
         -v: version: print version information

CAUTION: Domotion is as safe as your system is. Notice that, especially when usng Domotion for unlocking doors etc. There is a rather strong password encryption and secure HTTP is possible, but if someone is able to enter your harddisk, hacking may be possible.

That's all for now ...

Please send Comments and Bugreports to hellyrulez@home.nl