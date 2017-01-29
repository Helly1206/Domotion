<?php

include "IniSettings.php";
date_default_timezone_set('UTC');
session_start();

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
class SettingsAction {
    private $INI = null;
    
    function __construct () { // constructor
        $this->INI = new IniSettings();
    }
    
    public function SetSettings() {
        if (isset($_POST['ServiceURL'])) {
            $this->INI->SetServiceURL($_POST['ServiceURL']);         
        }
        if (isset($_POST['ServicePort'])) {
            $this->INI->SetServicePort($_POST['ServicePort']);         
        }
        if (isset($_POST['ServiceTimeout'])) {
            $this->INI->SetServiceTimeOut($_POST['ServiceTimeout']);         
        }
        if (isset($_POST['Sleeptime'])) {
            $this->INI->SetSleepTime($_POST['Sleeptime']);         
        }
        if (isset($_POST['Username'])) {
            $this->INI->SetUserName($_POST['Username']);         
        }
        header('Location: Main.php');
    }  
}

if (isset($_POST['Ok'])) {
    $CSettingsAction = new SettingsAction();
    $CSettingsAction->SetSettings();
} else if (isset($_POST['File'])) {
    require "IniEdit.php";
} else {
    // cancel
    header('Location: Main.php');
}
?>
