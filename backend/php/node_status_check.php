<?php

    function getUserIpAddr() {
        if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
            $ip = $_SERVER['HTTP_CLIENT_IP'];
        } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
        } else {
            $ip = $_SERVER['REMOTE_ADDR'];
        }
        return $ip;
    }

    function secondsToTime($seconds) {
        $dtF = new \DateTime('@0');
        $dtT = new \DateTime("@$seconds");
        $time = $dtF->diff($dtT);
        return $time->format('%a days, %H:%I:%S');
    }    

    function timeConvert($delta) {
        if ($delta < 2) {
            $return_time = " second";
        } else if ($delta < 60) {
            $return_time = " seconds";
        } else if ($delta/60 == 1) {
            $return_time = " minute";
        } else if ($delta/60 > 1 && $delta/60 < 60) {
            $return_time = " minutes";
        } else if ($delta/(60*60) == 1) {
            $return_time = " hour";
        } else {
            $return_time = " hours";
        }
        return $return_time;
    }

    ini_set("display_errors","on");
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD);
    $db = mysqli_select_db($connect, DB_DATABASE);

    if ($db) {
        $response["message"][0] = "Server Connected successfully";
    } else {
        $response["success"] = 0;
        $response["message"][0] = "Server Connection failed";
        echo json_encode($response);
        exit;
    }

    if (isset($_GET["mac"]) && isset($_GET["state"])) {
        $mac = $_GET["mac"];
        $state = $_GET["state"];
        $mode = "set_node";
    } else if (isset($_GET['mac']) && isset($_GET['display'])) {    
        $mac = $_GET['mac'];
        $display = $_GET['display'];
        $mode = "set_display";
    } else {
        $mode = "check";
    }

    if ($mode == "set_node") {
        $ip = getUserIpAddr();
        $time = time();
        $find_mac = mysqli_query($connect, "SELECT mac FROM nodes WHERE mac='$mac';");
        $update_result = false;

        if ($find_mac && $find_mac->num_rows  < 1) {
            $update_result = mysqli_query($connect, "INSERT INTO nodes(mac, ip, port, start_time, time_stamp, status) VALUES('$mac', '$ip', 0, $time, $time, true)");
            $response["message"][1] = "New Node $mac.";
            $response["message"][2] = "Inserted into nodes table.";
        } else if ($find_mac) {
            if ($state == "on") {
                $update_result = mysqli_query($connect, "UPDATE nodes SET ip='$ip', start_time=$time, time_stamp=$time, status=true WHERE mac='$mac';");
                $response["message"][1] = "Node $mac Turned On.";
                
            } else if ($state == "pong") {
                $update_result = mysqli_query($connect, "UPDATE nodes SET time_stamp=$time, status=true WHERE mac='$mac';");
                $response["message"][1] = "Node $mac Pinged.";
            }
        }
        if ($update_result) {
            $response["success"] = 1;
            $response["message"][2] = "Updated nodes table.";
        } else {
            $response["success"] = 0;
            $response["message"][2] = "ERROR Updating nodes table.";
        }

    } else if ($mode == "set_display") {
        $find_mac = mysqli_query($connect, "SELECT mac FROM nodes WHERE mac='$mac';");
        if ($find_mac->num_rows == 0) { 
            $response["success"] = 0;
            $response["message"][0] = "MAC: $mac not found in table";
        } else { 
            $result = false;
            if ($display == "true"){
                $result = mysqli_query($connect, "UPDATE nodes SET display=true WHERE mac='$mac';");
            } else if ($display == "false") {
                $result = mysqli_query($connect, "UPDATE nodes SET display=false WHERE mac='$mac';");
            } else {
                $response["success"] = 0;
                $response["message"][0] = "Invalid display input: $display.";
            }
            if ($result && ($display == true || $display == false) ){
                $response["success"] = 1;
                $response["message"][0] = "Display set to $display for Node: $mac";
            }
        }
    } else if ($mode == "check") {

        $timeout = 5*60;
        $list_nodes = mysqli_query($connect, "SELECT mac, start_time, time_stamp, status FROM nodes;");

        if ($list_nodes && $list_nodes->num_rows < 1) {
            $response["success"] = 0;
            $response["message"][0] = "No Nodes Found.";
        } else {

            $current_time = time();
            while ($row = mysqli_fetch_array($list_nodes)) {
                
                $mac = $row["mac"];
                $start_time = $row["start_time"];
                $node_time = $row["time_stamp"];
                $delta = $current_time - $node_time;

                if ($delta > $timeout) {
                    
                    $time_info = secondsToTime($delta) . timeConvert($delta);
                    $update_status = mysqli_query($connect,"UPDATE nodes SET start_time=0, status=false WHERE mac='$mac';");
                    
                    if ($update_status) {
                        $response["success"] = 1;
                        $response["message"][$row["mac"]][0] = "Node: $mac last seen $time_info ago.";
                        $response["message"][$row["mac"]][1] = "Updating status to offline.";
                    } else {
                        $response["success"] = 0;
                        $response["message"][$row["mac"]][0] = "Failed to Update node: $mac status.";
                    }
                } else {
                    
                    $start_delta = $current_time - $start_time;
                    
                    $time_info = secondsToTime($delta) . timeConvert($delta);
                    $up_time = secondsToTime($start_delta) . timeConvert($start_delta);
                    $update_status = mysqli_query($connect, "UPDATE nodes SET status=true WHERE mac='$mac';");
                    
                    if ($update_status) {
                        $response["success"] = 1;
                        $response["message"][$row["mac"]][0] = "Node: $mac last seen $time_info ago.";
                        $response["message"][$row["mac"]][1] = "Updating status to online.";
                        $response["message"][$row["mac"]][2] = "Online for $up_time.";
                        
                    } else {
                        $response["success"] = 0;
                        $response["message"][$row["mac"]][0] = "Failed to Update node: $mac status.";
                    }
                }
            }
        }
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
