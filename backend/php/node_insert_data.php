<?php

    function getUserIpAddr(){
        if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
            $ip = $_SERVER['HTTP_CLIENT_IP'];
        } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
        } else {
            $ip = $_SERVER['REMOTE_ADDR'];
        }
        return $ip;
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

    if (isset($_GET["mac"]) && isset($_GET["time"]) && isset($_GET["temp"]) && isset($_GET["hum"])) {
        $mac = $_GET["mac"];
        $time = $_GET["time"];
        $temp = $_GET["temp"];
        $hum = $_GET["hum"];
    } else {
        $response["success"] = 0;
        $response["message"][0] = "Parameter(s) are missing (mac, time, temp, hum). Please check request";
        echo json_encode($response);
        exit;
    }

    $insert_result = mysqli_query($connect, "INSERT INTO data(mac, time, temp, hum) VALUES('$mac', $time, $temp , $hum);");
    
    if ($insert_result) { 
        $response["message"][1] = "Data successfully inserted"; 
    } else { 
        $response["message"][1] = "Data failed to insert"; 
    }

    $find_mac = mysqli_query($connect, "SELECT mac FROM nodes WHERE mac='$mac';");
    $update_result = false;
    $ip = getUserIpAddr();

    if ($find_mac && $find_mac->num_rows == 0) {
        $update_result = mysqli_query($connect, "INSERT INTO nodes(mac, ip, port, start_time, time_stamp, status) VALUES('$mac', '$ip', 0, $time, $time, true)");
    } else if ($find_mac) {
        $update_result = mysqli_query($connect, "UPDATE nodes SET time_stamp=$time, status=true WHERE mac='$mac';");
    }

    if ($update_result) { 
        $response["message"][2] = "Node:'$mac' status updated"; 
    } else { 
        $response["message"][2] = "Node:'$mac' failed to update status"; 
    }

    if ($insert_result && $update_result) {
        $response["success"] = 1;
    } else {
        $response["success"] = 0;
    }
    
    echo json_encode($response);
    mysqli_close($connect);
?>
