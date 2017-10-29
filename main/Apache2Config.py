# -*- coding: utf-8 -*-
#########################################################
# SERVICE : Apache2Config.py                            #
#           Python configure apache2 for Domotion       #
#           I. Helwegen 2017                            #
#########################################################
####################### IMPORTS #########################
import subprocess
import xml.etree.ElementTree as ET
import sys
import os
import re
from getopt import getopt, GetoptError
from apt import Cache
from urlparse import urlparse
from database import db_read
#########################################################

####################### GLOBALS #########################
VERSION="1.00"
XML_FILENAME = "DomoWeb.xml"
DB_FILENAME = "Domotion.db"

#########################################################
# Class : Apache2Config                                 #
#########################################################
class Apache2Config(object):
    def __init__(self):
        self.ports=[]
        self.procs=[]

    def __del__(self):
        pass

    def run(self, argv):
        quick = False
        print "Domotion Home control and automation Apache2 configuration"
        try:
            opts, args = getopt(argv,"hq",["help","quick"])
        except GetoptError:
            print "Version: " + VERSION
            print " "
            print "Enter 'Apache2Config -h' for help"
            exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print "Version: " + VERSION
                print " "
                print "Usage:"
                print "         Apache2Config <args>"
                print "         -h, --help: this help file"
                print "         -q, --quick: quick check for changes and if none, only restart"
                print "                      (no check for Prerequisites)"
                exit()
            elif opt in ("-q", "--quick"):
                quick = True

        self.IsRoot()
        if not quick:
            print "Testing Apache2 installation ..."
            self.PrereqInstalled()

        sites=self.GetAllSites()     
        xmlsites=self.GetSitesFromXML()

        # Deleting old sites
        for site in sites:
            keep = False
            for xmlsite in xmlsites:
                if site[1] == xmlsite[1]:
                    keep = True

            if keep:
                if not quick:
                    print "Keeping site %s on port %d as it is still in DomoWeb.xml"%(site[0], site[1])
            else:
                print "Deleting site %s on port %d"%(site[0], site[1])
                sitename = site[0].split(".")[0]
                if site[2]:
                    self.A2DisSite(sitename)
                self.RemovePort(site[1])
                self.RemoveSite(site[0])

        # Adding new sites
        for xmlsite in xmlsites:
            keep = False
            enabled = False
            for site in sites:
                if site[1] == xmlsite[1]:
                    keep = True
                    enabled = site[2]

            sitename = "Domotion_%d.conf"%xmlsite[1]
            sitename2 = sitename.split(".")[0]

            if keep:
                if not quick:
                    print "Updating site %s on port %d"%(sitename, xmlsite[1])
            else:
                print "Adding site %s on port %d"%(sitename, xmlsite[1])

            email = xmlsite[5]
            server = xmlsite[6]

            if not quick:
                if xmlsite[5] == "":
                    email = self.EmailInput()

                if xmlsite[6] == "":
                    server = self.ServerInput()                    

            content = ""
            prefix=self.GetPrefix()
            if (xmlsite[2]): # https
                content = self.GenConfHttps(xmlsite[1], email, server, xmlsite[3], xmlsite[4], prefix)
            else: #http
                content = self.GenConfHttp(xmlsite[1], email, server, prefix)

            if not quick or (quick and not keep):
                self.AddSite(sitename,content)
                self.AddPort(xmlsite[1])
            else: # quick and keep
                rdcontent = self.ReadSite(sitename)
                if (rdcontent != content):
                    print "Site %s on port %d changed, update site"%(site[0], site[1])
                    self.AddSite(sitename,content)
                    self.AddPort(xmlsite[1])

            if not enabled:
                self.A2EnSite(sitename2)

        print "Restarting Apache2 ..."
        self.A2Restart()
        print "Ready"
        exit()

    def GetXML(self):
        etcpath = "/etc/Domotion/"
        XMLpath = ""
        # first look in etc
        if os.path.isfile(os.path.join(etcpath,XML_FILENAME)):
            XMLpath = os.path.join(etcpath,XML_FILENAME)
        else:
            # then look in home folder
            if os.path.isfile(os.path.join(os.path.expanduser('~'),XML_FILENAME)):
                XMLpath = os.path.join(os.path.expanduser('~'),XML_FILENAME)
            else:
                # look in local folder, hope we may write
                if os.path.isfile(os.path.join(".",XML_FILENAME)):
                    if os.access(os.path.join(".",XML_FILENAME), os.W_OK):
                        XMLpath = os.path.join(".",XML_FILENAME)
                    else: 
                        self.logger.critical("No write access to XML file, exit")
                        exit(1)
                else:
                    self.logger.critical("No XML file found, exit")
                    exit(1)
        return (XMLpath)

    def IsRoot(self):
        if not os.geteuid() == 0:
            sys.exit("Apache2Config must be run as root")

    def PrereqInstalled(self):
        IsInstalled = False
        cache = Cache()

        for pkg in cache:
            if pkg.name == "apache2":
                IsInstalled = pkg.is_installed

        if (not IsInstalled):
            sys.exit("Package 'apache2' is not installed, run 'install.sh -a' first or install manually")

        IsInstalled = False
        for pkg in cache:
            if pkg.name == "libapache2-mod-wsgi":
                IsInstalled = pkg.is_installed

        if (not IsInstalled):
            sys.exit("Package 'libapache2-mod-wsgi' is not installed, run 'install.sh -a' first or install manually")

    def A2Restart(self):
        if self._RunShell("systemctl restart apache2"):
            sys.exit("Error restarting apache2, check logfile")

    def A2EnSite(self, site):
        #apache2ctl -S 2>&1|grep 8090
        if self._RunShell("a2ensite %s"%(site)):
            sys.exit("Error enabling site, check logfile")

    def A2DisSite(self, site):
        if self._RunShell("a2dissite %s"%(site)):
            sys.exit("Error disabling site, check logfile")

    def _RunShell(self, command):
        with open(os.devnull, 'w')  as devnull:
            try:
                osstdout = subprocess.check_call(command.split(), stdout=devnull, stderr=devnull)
            except subprocess.CalledProcessError:
                return 1
        return osstdout

    def EmailInput(self):
        email = "webmaster@localhost"
        valid = None
        
        while not valid:
            sys.stdout.write("Please enter E-mail address <%s>:"%email)

            try:
                line = sys.stdin.readline().strip()
            except KeyboardInterrupt:
                exit("Interrupted")

            if line != "":
                valid=re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", line)
                if not valid:
                    print "Invalid email address, try again"
                else:
                    email = line
            else:
                valid = True
        
        return email

    def ServerInput(self):
        server = "localhost"
        valid = False

        while not valid:
            sys.stdout.write("Please enter server name <%s>:"%server)

            try:
                line = sys.stdin.readline().strip()
            except KeyboardInterrupt:
                exit("Interrupted")

            if line != "":
                try:
                    result = urlparse(line)
                    if not result.scheme:
                        result = urlparse("http://"+line)
                    valid = result.scheme and result.netloc
                except:
                    pass

                if not valid:
                    print "Invalid server name, try again"
                else:
                    server = line
            else:
                valid = True

        return server

    def RemoveSite(self, site):
        availablepath = "/etc/apache2/sites-available"
        sitepath = os.path.join(availablepath, site)
        if os.path.isfile(sitepath):
            os.remove(sitepath)

    def AddSite(self, site, content):
        availablepath = "/etc/apache2/sites-available"
        sitepath = os.path.join(availablepath, site)

        with open(sitepath, "w") as f:
            f.write(content)

    def ReadSite(self, site):
        content = ""
        availablepath = "/etc/apache2/sites-available"
        sitepath = os.path.join(availablepath, site)

        with open(sitepath, "r") as f:
            content = f.read()

        return content        

    def AddPort(self, port):
        etcpath = "/etc/apache2/"
        conffile = "ports.conf"
        confpath = os.path.join(etcpath,conffile)
        if not os.path.isfile(confpath):
            exit("Configuration file '%s' does not exist, check apache installation"%confpath)

        with open(confpath, 'r') as f:
            content = f.read()

        if not self.FindPort(content, port):
            if (not content[-1:] == "\n"):
                content +="\n"
            content += "Listen %d\n"%port

            with open(confpath, "w") as f:
                f.write(content)

        return

    def RemovePort(self, port):
        # if not 80 or 443
        etcpath = "/etc/apache2/"
        conffile = "ports.conf"
        confpath = os.path.join(etcpath,conffile)
        if not os.path.isfile(confpath):
            exit("Configuration file '%s' does not exist, check apache installation"%confpath)

        if (port == 80) or (port == 443):
            print "Notice: system port %d not removed from apache2 config"%port
            return

        with open(confpath, 'r') as f:
            content = f.read()

        if self.FindPort(content, port):
            content2 = ""
            last = False
            for line in content.split("\n"):
                if (line.strip() != "Listen %d"%port):
                    content2 += line + "\n"
                    last = True
                else:
                    last = False
            
            if last:
                content2 = content2[:-1]

            with open(confpath, "w") as f:
                f.write(content2)

        return

    def FindPort(self, content, port):
        Found = False

        for line in content.split("\n"):
            if (line.strip() == "Listen %d"%port):
                Found = True
            
        return Found

    def GetAllSites(self):
        availablepath = "/etc/apache2/sites-available"
        enabledpath = "/etc/apache2/sites-enabled"
        sites = []
        if not os.path.isdir(availablepath):
            exit("Apache2 folder '%s' does not exist, check apache installation"%availablepath)
        for file in os.listdir(availablepath):
            if (file.find("Domotion_")==0) and (file.find(".conf")>0):
                try:
                    portend=file.find(".conf")
                    port=int(file[9:portend])
                except:
                    port=0
                if os.path.isfile(os.path.join(enabledpath,file)):
                    enabled=True
                else:
                    enabled=False
                sites.append((file, port, enabled))

        return sites

    def GetSitesFromXML(self):
        index = 0
        ports=[]
        sites = []
        tree = ET.parse(self.GetXML())
        root = tree.getroot()
        for child in root:
            name=child.tag
            ssl=False
            
            if index>4:
                print ("Server [%s] not started as maximum of 5 servers obtained"%name)
                continue
            else:
               index += 1

            textdep=child.find('externaldeployment')
            if textdep != None:
                if (textdep.text.lower() == "false"):
                    print ("Server [%s] not externally deployed, so not added to apache2"%name)
                    continue
            tssl=child.find('ssl')
            if tssl != None:
                if (tssl.text.lower() == "true"):
                    ssl = True
            
            cert = ""
            key = ""
            if ssl:
                tcert=child.find('certificate')
                if tcert != None:
                    cert = tcert.text
                else:
                    ssl=False

                tkey=child.find('privatekey')
                if tkey != None:
                    key = tkey.text
                else:
                    ssl=False

            port = 5000
            tport=child.find('port')
            if tport != None:
                port=int(tport.text)
            while port in ports:
                port +=1
            ports.append(port)

            email = ""
            temail=child.find('serveradmin')
            if temail != None:
                email=temail.text

            server = ""
            tserver=child.find('servername')
            if tserver != None:
                server=tserver.text

            sites.append((name, port, ssl, cert, key, email, server))

        return sites

    def GenConfHttp(self, port, admin, server, prefix):
        return "<VirtualHost *:%d>\n" \
        "    ServerAdmin %s\n" \
        "    ServerName %s\n" \
        "    \n" \
        "    ErrorLog ${APACHE_LOG_DIR}/error.log\n" \
        "    CustomLog ${APACHE_LOG_DIR}/access.log combined\n" \
        "    \n" \
        "    WSGIDaemonProcess DomoWeb_%d user=www-data group=www-data threads=5\n" \
        "    WSGIScriptAlias %s /var/www/Domotion/DomoWeb.wsgi\n" \
        "    \n" \
        "    <Directory /var/www/Domotion>\n" \
        "        WSGIProcessGroup DomoWeb_%d\n" \
        "        WSGIApplicationGroup %%{GLOBAL}\n" \
        "        Order deny,allow\n" \
        "        Allow from all\n" \
        "    </Directory>\n" \
        "    \n" \
        "</VirtualHost>\n"%(port, admin, server, port, prefix, port)

    def GenConfHttps(self, port, admin, server, cert, key, prefix):
        return "<VirtualHost *:%d>\n" \
        "    ServerAdmin %s\n" \
        "    ServerName %s\n" \
        "    \n" \
        "    ErrorLog ${APACHE_LOG_DIR}/error.log\n" \
        "    CustomLog ${APACHE_LOG_DIR}/access.log combined\n" \
        "    \n" \
        "    WSGIDaemonProcess DomoWeb_%d user=www-data group=www-data threads=5\n" \
        "    WSGIScriptAlias %s /var/www/Domotion/DomoWeb.wsgi\n" \
        "    SSLEngine on\n" \
        "    \n" \
        "    SSLCertificateFile  %s\n" \
        "    SSLCertificateKeyFile %s\n" \
        "    \n" \
        "    <Directory /var/www/Domotion>\n" \
        "        WSGIProcessGroup DomoWeb_%d\n" \
        "        WSGIApplicationGroup %%{GLOBAL}\n" \
        "        Order deny,allow\n" \
        "        Allow from all\n" \
        "    </Directory>\n" \
        "    \n" \
        "</VirtualHost>\n"%(port, admin, server, port, prefix, cert, key, port)

    def GetDB(self):
        etcpath = "/etc/Domotion/"
        DBpath = ""
        # first look in etc
        if os.path.isfile(os.path.join(etcpath,DB_FILENAME)):
            DBpath = os.path.join(etcpath,DB_FILENAME)
        else:
            # then look in home folder
            if os.path.isfile(os.path.join(os.path.expanduser('~'),DB_FILENAME)):
                DBpath = os.path.join(os.path.expanduser('~'),DB_FILENAME)
            else:
                # look in local folder, hope we may write
                if os.path.isfile(os.path.join(".",DB_FILENAME)):
                    if os.access(os.path.join(".",DB_FILENAME), os.W_OK):
                        DBpath = os.path.join(".",DB_FILENAME)
                    else: 
                        self.logger.critical("No write access to DB file, exit")
                        exit(1)
                else:
                    self.logger.critical("No DB file found, exit")
                    exit(1)
        return (DBpath)

    def GetPrefix(self):
        prefix ="/"
        try:
            db=db_read(self.GetDB())
            prefix=db.GetSetting('DomoWeb_prefix')
            if prefix[:1] != "/":
                prefix = "/" + prefix
            if prefix[-1:] == "/":
                prefix = prefix[:-1]
            del db
        except:
            pass

        return prefix

#########################################################
if __name__ == "__main__":
    Apache2Config().run(sys.argv[1:])