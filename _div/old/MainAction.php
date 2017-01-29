<?php

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
include "IniSettings.php";
include "TinyWebDBClient.php";
date_default_timezone_set('UTC');
session_start();

class MainAction {
    private $INI = null;
    private $TWDB = null; 
            
    function __construct () { // constructor
        //session_start();
        $this->INI = new IniSettings();
        $this->TWDB = new TinyWebDBClient();
        
        $this->TWDB->SetServiceURL($this->INI->GetServiceURL(),$this->INI->GetServicePort());
        $this->TWDB->SetServiceTimeOut($this->INI->GetServiceTimeOut());
    }
    
    private function DeviceIsOn($pos) {
        if (!isset($_SESSION['Devices'])) {
            throw new Exception("Error: [Devices] values not set");
        }
            
        if ($_SESSION['Devices'][$pos] == '1') {
            return (1);
        } else {
            return (0);
        }
    }
    
    private function CommandIsOn($pos) {
        if (!isset($_SESSION['Commands'])) {
            throw new Exception("Error: [Commands] values not set");
        }
            
        if ($_SESSION['Commands'][$pos] == '1') {
            return (1);
        } else {
            return (0);
        }
    }
    
    private function CommandIsOff($pos) {
        if (!isset($_SESSION['Commands'])) {
            throw new Exception("Error: [Commands] values not set");
        }
            
        if ($_SESSION['Commands'][$pos+4] == '1') {
            return (1);
        } else {
            return (0);
        }
    }
    
    private function SetCommandOn($pos,$SR) {
        if (!isset($_SESSION['Commands'])) {
            throw new Exception("Error: [Commands] values not set");
        }
            
        if ($SR) {
            $_SESSION['Commands'][$pos-1] = '1';
            return (1);
        } else {
            $_SESSION['Commands'][$pos-1] = '0';
            return (0);
        }
    }
    
    private function SetCommandOff($pos,$SR) {
        if (!isset($_SESSION['Commands'])) {
            throw new Exception("Error: [Commands] values not set");
        }
            
        if ($SR) {
            $_SESSION['Commands'][$pos+3] = '1';
            return (1);
        } else {
            $_SESSION['Commands'][$pos+3] = '0';
            return (0);
        }
    }
    
    private function DeviceValueChange($Device) {
        $retval = -1;
        if (isset($_POST['CheckBoxDevice'.$Device]) && (!$this->DeviceIsOn($Device - 1))) {
            $retval = 1;
        }

        if (!isset($_POST['CheckBoxDevice'.$Device]) && ($this->DeviceIsOn($Device - 1))) {
            $retval = 0;
        }
        
        return ($retval);
    }
    
    private function BlindValueChange() {
        $retval = -1;
        if (isset($_POST['ButtonUp'])) {
            $retval = 0; // up = false;
        }

        if (isset($_POST['ButtonDown'])) {
            $retval = 1; // down = true;
        }
        
        return ($retval);
    }
        
    private function CommandValueChangeOn($Command) {
        $retval = -1;
        if (isset($_POST['CheckBoxCommand'.$Command.'On']) && (!$this->CommandIsOn($Command - 1))) {
            $retval = 1;
        }

        if (!isset($_POST['CheckBoxCommand'.$Command.'On']) && ($this->CommandIsOn($Command - 1))) {
            $retval = 0;
        }
        
        return ($retval);
    }
    
    private function CommandValueChangeOff($Command) {
        $retval = -1;
        if (isset($_POST['CheckBoxCommand'.$Command.'Off']) && (!$this->CommandIsOff($Command - 1))) {
            $retval = 1;
        }

        if (!isset($_POST['CheckBoxCommand'.$Command.'Off']) && ($this->CommandIsOff($Command - 1))) {
            $retval = 0;
        }
        
        return ($retval);
    }
    
    private function SendDeviceValue($devnr,$onoff) {
        //echo "Status: Set Device <br/>";
        if ($onoff) {
           // echo "D".chr($devnr+ord('A')-1). ": 1";
            $this->TWDB->StoreValue("D".chr($devnr+ord('A')-1), "1");
        } else {
            //echo "D".chr($devnr+ord('A')-1). ": 0";
            $this->TWDB->StoreValue("D".chr($devnr+ord('A')-1), "0");
        }
    }
    
    private function SendCommandValue($cmdnr,$onoff) {
        //echo "Status: Set Command <br/>";
        if ($onoff) {
            //echo "C".chr($cmdnr+ord('A')-1). ": 1";
            $this->TWDB->StoreValue("C".chr($cmdnr+ord('A')-1), "1");
        } else {
            //echo "C".chr($cmdnr+ord('A')-1). ": 0";
            $this->TWDB->StoreValue("C".chr($cmdnr+ord('A')-1), "0");
        }
    }
    
    public function CheckChangesAndExecute() {
        // Check Devices
        if ($this->DeviceValueChange(1)>=0) {
            $this->SendDeviceValue(1, $this->DeviceValueChange(1));
        }
        if ($this->DeviceValueChange(2)>=0) {
            $this->SendDeviceValue(2, $this->DeviceValueChange(2));
        }
        if ($this->DeviceValueChange(3)>=0) {
            $this->SendDeviceValue(3, $this->DeviceValueChange(3));
        }
        if ($this->DeviceValueChange(4)>=0) {
            $this->SendDeviceValue(4, $this->DeviceValueChange(4));
        }
        if ($this->DeviceValueChange(5)>=0) {
            $this->SendDeviceValue(5, $this->DeviceValueChange(5));
        }
        if ($this->DeviceValueChange(6)>=0) {
            $this->SendDeviceValue(6, $this->DeviceValueChange(6));
        }
        if ($this->DeviceValueChange(7)>=0) {
            $this->SendDeviceValue(7, $this->DeviceValueChange(7));
        }
        if ($this->DeviceValueChange(8)>=0) {
            $this->SendDeviceValue(8, $this->DeviceValueChange(8));
        }
        if ($this->DeviceValueChange(9)>=0) {
            $this->SendDeviceValue(9, $this->DeviceValueChange(9));
        }
        if ($this->DeviceValueChange(10)>=0) {
            $this->SendDeviceValue(10, $this->DeviceValueChange(10));
        }
        if ($this->DeviceValueChange(11)>=0) {
            $this->SendDeviceValue(11, $this->DeviceValueChange(11));
        }
        if ($this->DeviceValueChange(12)>=0) {
            $this->SendDeviceValue(12, $this->DeviceValueChange(12));
        }
        if ($this->DeviceValueChange(13)>=0) {
            $this->SendDeviceValue(13, $this->DeviceValueChange(13));
        }
        // Check blinds
        if ($this->BlindValueChange()>=0) {
            $this->SendDeviceValue(16, $this->BlindValueChange());
        }
        
        // Check commands
        if ($this->CommandValueChangeOn(1)==1) {
            $this->SendCommandValue(1,1);
            $this->SetCommandOn(1,1);
            $this->SetCommandOff(1,0);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOn(1,0);
        } else if ($this->CommandValueChangeOff(1)==1) {
            $this->SendCommandValue(1,0);
            $this->SetCommandOn(1,0);
            $this->SetCommandOff(1,1);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOff(1,0);
        }
        if ($this->CommandValueChangeOn(2)==1) {
            $this->SendCommandValue(2,1);
            $this->SetCommandOn(2,1);
            $this->SetCommandOff(2,0);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOn(2,0);
        } else if ($this->CommandValueChangeOff(2)==1) {
            $this->SendCommandValue(2,0);
            $this->SetCommandOn(2,0);
            $this->SetCommandOff(2,1);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOff(2,0);
        }
        if ($this->CommandValueChangeOn(3)==1) {
            $this->SendCommandValue(3,1);
            $this->SetCommandOn(3,1);
            $this->SetCommandOff(3,0);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOn(3,0);
        } else if ($this->CommandValueChangeOff(3)==1) {
            $this->SendCommandValue(3,0);
            $this->SetCommandOn(3,0);
            $this->SetCommandOff(3,1);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOff(3,0);
        }
        if ($this->CommandValueChangeOn(4)==1) {
            $this->SendCommandValue(4,1);
            $this->SetCommandOn(4,1);
            $this->SetCommandOff(4,0);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOn(4,0);
        } else if ($this->CommandValueChangeOff(4)==1) {
            $this->SendCommandValue(4,0);
            $this->SetCommandOn(4,0);
            $this->SetCommandOff(4,1);
        } else if ($this->CommandValueChangeOff(4)==0) {
            $this->SetCommandOff(4,0);
        }
    }
}

$CMainAction = new MainAction();
$CMainAction->CheckChangesAndExecute();
header('Location: Main.php');

?>
