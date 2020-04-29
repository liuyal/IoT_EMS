<?php
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

    if (isset($_GET["table"])) { $table = $_GET["table"]; } 
    else { $table = "data"; }

    if (strstr($table, "data")) {
        $result = mysqli_query($connect, "SELECT * FROM $table ORDER BY time ASC;");
    } else {
        $result = mysqli_query($connect, "SELECT * FROM $table;");
    }

    if ($result && mysqli_num_rows($result) > 0 && strstr($table, "data")) {
        $response["data"] = array();
        while ($row = mysqli_fetch_array($result)) {
            $data = array();
            $data["mac"] = $row["mac"];
            $data["time"] = $row["time"];
            $data["temp"] = $row["temp"];
            $data["hum"] = $row["hum"];
            array_push($response["data"], $data);
        }
        $response["success"] = 1;
        $response["message"][1] = "Data found successfully";
    } else if ($result && mysqli_num_rows($result) > 0 && strstr($table, "nodes")) {
        $response["data"] = array();
        while ($row = mysqli_fetch_array($result)) {
            $data = array();
            $data["mac"] = $row["mac"];
            $data["ip"] = $row["ip"];
            $data["port"] = $row["port"];
            $data["start_time"] = $row["start_time"];
            $data["time_stamp"] = $row["time_stamp"];
            $data["status"] = $row["status"];
            $data["display"] = $row["display"];
            array_push($response["data"], $data);
        }
        $response["success"] = 1;
        $response["message"][1] = "Node data found successfully";
    } else if ($result && mysqli_num_rows($result) > 0 && strstr($table, "system_config")) {
        $response["data"] = array();
        while ($row = mysqli_fetch_array($result)) {
            $data = array();
            $data["host_ip"] = $row["host_ip"];
            $data["host_port"] = $row["host_port"];
            $data["display_mac"] = $row["display_mac"];
            array_push($response["data"], $data);
        }
        $response["success"] = 1;
        $response["message"][1] = "System Configuration data found successfully";
    } else if ($result && mysqli_num_rows($result) > 0 && strstr($table, "daily_avg")) {
        $response["data"] = array();
        while ($row = mysqli_fetch_array($result)) {
            $data = array();
            $data["mac"] = $row["mac"];
            $data["date"] = $row["date"];
            $data["avg_temp"] = $row["avg_temp"];
            $data["avg_hum"] = $row["avg_hum"];
            array_push($response["data"], $data);
        }
        $response["success"] = 1;
        $response["message"][1] = "Daily average data found successfully";
    } else if ($result && mysqli_num_rows($result) < 1) {
        $response["success"] = 0;
        $response["message"][1] = "No data found in table: $table";
    } else {
        $response["success"] = 0;
        $response["message"][1] = "No table matching input: $table found";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
