<!--
To change this template, choose Tools | Templates
and open the template in the editor.
-->
<!DOCTYPE html>
<html>
    <head>
        <?php
        // put your code here
        include "IniSettings.php";
        include "TinyWebDBClient.php";
	 error_reporting(E_ALL^E_NOTICE^E_WARNING); 
        date_default_timezone_set('UTC');
	 session_start();
        ?>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta http-equiv="refresh" content="
            <?php 
            if (isset($_SESSION['Refresh'])) {
                echo ($_SESSION['Refresh']); 
            } else {
                echo (10);
            }
            ?>">
        <title></title>
    </head>
    <body>
        <?php         
        class Main {
            const text1st = "Enable: ";
            const flagon = "<on>";
            const flagoff = "<off>";
            const text2nd = ", Auto: ";
            const flagup = "<up>";
            const flagdown = "<down>";
            private $INI = null;
            private $TWDB = null; 
                   
            function __construct () { // constructor
                //session_start();
                $this->INI = new IniSettings();
                $this->TWDB = new TinyWebDBClient();
                
                $this->TWDB->SetServiceURL($this->INI->GetServiceURL(),$this->INI->GetServicePort());
                $this->TWDB->SetServiceTimeOut($this->INI->GetServiceTimeOut());
                
                if (!isset($_SESSION['Commands'])) {
                    $_SESSION['Commands'] = "00000000";
                }
                if (!isset($_SESSION['LoginState'])) {
                    $_SESSION['LoginState'] = 99;
                }
            }
            
            private function GetLoginState() {
                // S0..5
                $sState = $this->TWDB->GetValue("PWD");
                if ($sState[0] == 'S') {
                    $_SESSION['LoginState'] = $sState[1]-'0';
                    return ($sState[1]-'0');
                } else {
                    $_SESSION['LoginState'] = 99; //self::LIST_UNKNOWN;
                    return (99); //self::LIST_UNKNOWN;
                }
            }
            
            private function ArduinoGetTime() {
                $Time_Val = (int)($this->TWDB->GetValue("TIME"));

                return ($this->CalcnPrintTime($Time_Val));
            }

    
            private function CalcnPrintTime($Time_Val) {
		return (date("d-m-Y H:i:s",$Time_Val)); // unix time in ms
                //("dd-MM-yyyy HH:mm:ss"); //01-05-2008 14:39:45
            } 
    
           // public function DeviceIsOn($DvcStat) {
           //     return ($DvcStat[0] == '1');
           // }
    
            public function DeviceIsOn($DvcStat, $pos) {
                if ($DvcStat[$pos] == '1') {
                    return ("Checked");
                } else {
                    return ("");
                }
            }
    
            public function GetBlindString($FlagEnabled, $FlagAuto) {
                if ($FlagEnabled == "Checked") {
                    $BlindStatus = self::text1st . self::flagon . self::text2nd;
                    if ($FlagAuto == "") { // == HomeCtrlMainScreen.dir_up) {
                        $BlindStatus .= self::flagup;
                    } else {
                        $BlindStatus .= self::flagdown;
                    }
                } else {
                    $BlindStatus = self::text1st . self::flagoff . self::text2nd . self::flagdown;
                }
                return ($BlindStatus);
            }
    
            public function ArduinoGetDeviceStatus() {
                return ($this->TWDB->GetValue("DZ"));
            }                   
            
            public function Refresh() {                
                $DeviceName1 = $this->INI->GetDeviceName(1);
                $DeviceName2 = $this->INI->GetDeviceName(2);
                $DeviceName3 = $this->INI->GetDeviceName(3);
                $DeviceName4 = $this->INI->GetDeviceName(4);
                $DeviceName5 = $this->INI->GetDeviceName(5);
                $DeviceName6 = $this->INI->GetDeviceName(6);
                $DeviceName7 = $this->INI->GetDeviceName(7);
                $DeviceName8 = $this->INI->GetDeviceName(8);
                $DeviceName9 = $this->INI->GetDeviceName(9);
                $DeviceName10 = $this->INI->GetDeviceName(10);
                $DeviceName11 = $this->INI->GetDeviceName(11);
                $DeviceName12 = $this->INI->GetDeviceName(12);
                $DeviceName13 = $this->INI->GetDeviceName(13);
                $DeviceName14 = $this->INI->GetDeviceName(14);
                $DeviceName15 = $this->INI->GetDeviceName(15);
                $DeviceName16 = $this->INI->GetDeviceName(16);
                $CommandName1 = $this->INI->GetCommandName(1);
                $CommandName2 = $this->INI->GetCommandName(2);
                $CommandName3 = $this->INI->GetCommandName(3);
                $CommandName4 = $this->INI->GetCommandName(4);
                                
                if ($_SESSION['LoginState'] == 3) { //LIST_LOGGEDIN
                    if ($this->GetLoginState() == 3) { //LIST_LOGGEDIN
                        $Status = "Logged In";
                        $DateTime = $this->ArduinoGetTime();
                
                        $Devices = $this->ArduinoGetDeviceStatus();
                        $ValCheckBoxDevice1 = $this->DeviceIsOn($Devices,0);
                        $ValCheckBoxDevice2 = $this->DeviceIsOn($Devices,1);
                        $ValCheckBoxDevice3 = $this->DeviceIsOn($Devices,2);
                        $ValCheckBoxDevice4 = $this->DeviceIsOn($Devices,3);
                        $ValCheckBoxDevice5 = $this->DeviceIsOn($Devices,4);
                        $ValCheckBoxDevice6 = $this->DeviceIsOn($Devices,5);
                        $ValCheckBoxDevice7 = $this->DeviceIsOn($Devices,6);
                        $ValCheckBoxDevice8 = $this->DeviceIsOn($Devices,7);
                        $ValCheckBoxDevice9 = $this->DeviceIsOn($Devices,8);
                        $ValCheckBoxDevice10 = $this->DeviceIsOn($Devices,9);
                        $ValCheckBoxDevice11 = $this->DeviceIsOn($Devices,10);
                        $ValCheckBoxDevice12 = $this->DeviceIsOn($Devices,11);
                        $ValCheckBoxDevice13 = $this->DeviceIsOn($Devices,12);
                
                        $BlindInfo = $this->GetBlindString($this->DeviceIsOn($Devices,14), $this->DeviceIsOn($Devices,13));
                    } else {
                        $Status = "Not Logged In";
                        header('Location: Access.php');
                        exit();
                    }
                } else {
                    $Status = "Not Logged In";
                    header('Location: Access.php');
                    exit();
                    /*$DateTime = $this->CalcnPrintTime(0);
                    
                    $Devices = "0000000000000000";
                    $ValCheckBoxDevice1 = "";
                    $ValCheckBoxDevice2 = "";
                    $ValCheckBoxDevice3 = "";
                    $ValCheckBoxDevice4 = "";
                    $ValCheckBoxDevice5 = "";
                    $ValCheckBoxDevice6 = "";
                    $ValCheckBoxDevice7 = "";
                    $ValCheckBoxDevice8 = "";
                    $ValCheckBoxDevice9 = "";
                    $ValCheckBoxDevice10 = "";
                    $ValCheckBoxDevice11 = "";
                    $ValCheckBoxDevice12 = "";
                    $ValCheckBoxDevice13 = "";
                
                    $BlindInfo = $this->GetBlindString("", "");*/
                }
                               
                // Bring devices to session;
                $_SESSION['Devices'] = $Devices;
                
                $ValCheckBoxCommand1On=$this->DeviceIsOn($_SESSION['Commands'],0);
                $ValCheckBoxCommand2On=$this->DeviceIsOn($_SESSION['Commands'],1);
                $ValCheckBoxCommand3On=$this->DeviceIsOn($_SESSION['Commands'],2);
                $ValCheckBoxCommand4On=$this->DeviceIsOn($_SESSION['Commands'],3);
                $ValCheckBoxCommand1Off=$this->DeviceIsOn($_SESSION['Commands'],4);
                $ValCheckBoxCommand2Off=$this->DeviceIsOn($_SESSION['Commands'],5);
                $ValCheckBoxCommand3Off=$this->DeviceIsOn($_SESSION['Commands'],6);
                $ValCheckBoxCommand4Off=$this->DeviceIsOn($_SESSION['Commands'],7);
                
                require "../Layout/Main.html";
            }
        }
        
        $Main = new Main();
        $Main->Refresh();
        ?>
    </body>
</html>
