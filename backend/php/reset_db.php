<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $response = array();
    $db_name = DB_DATABASE;

    try {
        $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD) or die(mysqli_error());
        $response["message"][0] = "Server Connected successfully";

        mysqli_query($connect, "DROP DATABASE $db_name;");
        $response["message"][1] = "Drop DB successfully";

        mysqli_query($connect, "CREATE DATABASE $db_name;");
        $response["message"][2] = "Create DB successfully";

        $db = mysqli_select_db($connect, DB_DATABASE) or die(mysqli_error());
        
        $result1 = mysqli_query($connect,"CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));") or die(mysqli_error());
        $result2 = mysqli_query($connect,"CREATE Table nodes(mac VARCHAR(17), ip CHAR(39), port INT, time_stamp INT, status boolean, PRIMARY KEY (mac));") or die(mysqli_error());
        $result3 = mysqli_query($connect,"CREATE Table system_config(host_ip CHAR(39), host_port CHAR(39));") or die(mysqli_error());

    }
    catch(PDOException $e) {$response["Server_connection_MSG"] = "Server Connection failed: " . $e->getMessage();}
     
    if ($result1) {$response["message"][3] = "data Table created successfully";}
    else {$response["message"][3] = "ERROR: DB failed to create data table";}

    if ($result2) {$response["message"][4] = "nodes Table created successfully";}
    else {$response["message"][4] = "ERROR: DB failed to create nodes table";}

    if ($result3) {$response["message"][5] = "system_config Table created successfully";}
    else {$response["message"][5] = "ERROR: DB failed to create system_config table";}

    if ($result1 && $result2 && $result3) {
        $response["success"] = 1;
        $response["message"][6] = "DB reset complete";
    }
    else {
        $response["success"] = 0;
        $response["message"][6] = "ERROR: DB reset failed";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>




