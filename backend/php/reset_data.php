<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");
    $db_name = DB_DATABASE;

    if (isset($_GET['data'])){
        $table = $_GET['data'];
    }
    else {
        $table = "db";
    }

    try {
        $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD);
        $db = mysqli_select_db($connect, DB_DATABASE);
        $response["message"][0] = "Server Connected successfully";
    }
    catch(PDOException $e){$response["message"][0] = "Server Connection failed: " . $e->getMessage();}

    if ($table == "db"){
        mysqli_query($connect, "DROP DATABASE $db_name;");
        $response["message"][1] = "Drop DB successfully";
        mysqli_query($connect, "CREATE DATABASE $db_name;");
        $response["message"][2] = "Create DB successfully";

        $db = mysqli_select_db($connect, DB_DATABASE);
        
        $result1 = mysqli_query($connect,"CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));");
        $result2 = mysqli_query($connect,"CREATE Table nodes(mac VARCHAR(17), ip CHAR(39), port INT, time_stamp INT, status boolean, display boolean, PRIMARY KEY (mac));");
        $result3 = mysqli_query($connect,"CREATE Table system_config(host_ip CHAR(39), host_port CHAR(39));");
        $result4 = mysqli_query($connect,"CREATE TABLE daily_avg(mac VARCHAR(17), date BIGINT, avg_temp DECIMAL (18, 2), avg_hum DECIMAL (18, 2), PRIMARY KEY (mac, date));");
    }
    else {
        $result_T = mysqli_query($connect, "TRUNCATE TABLE $table");
    }

    if ($table != "db" && $result_T) {
        $response["success"] = 1;
        $response["message"][1] = "Table: $table cleared";
    }
    else if ($table != "db" && !$result_T) {
        $response["success"] = 0;
        $response["message"][1] = "Table: $table failed to clear";
    }

    if ($table == "db" && $result1) {
        $response["message"][3] = "data Table created successfully";
    }
    else if ($table == "db" && !$result1) {
        $response["message"][3] = "ERROR: DB failed to create data table";
    }

    if ($table == "db" && $result2) {
        $response["message"][4] = "nodes Table created successfully";
    }
    else if ($table == "db" && !$result2){
        $response["message"][4] = "ERROR: DB failed to create nodes table";
    }

    if ($table == "db" && $result3) {
        $response["message"][5] = "system_config Table created successfully";
    }
    else if ($table == "db" && !$result3){
        $response["message"][5] = "ERROR: DB failed to create system_config table";
    }
    if ($table == "db" && $result4) {
        $response["message"][6] = "daily_avg Table created successfully";
    }
    else if ($table == "db" && !$result4){
        $response["message"][6] = "ERROR: DB failed to create daily_avg table";
    }

    if ($table == "db" && $result1 && $result2 && $result3 && $result4) {
        $response["success"] = 1;
        $response["message"][7] = "DB reset complete";
    }
    else if ($table == "db" && (!$result1 || !$result2 || !$result3)) {
        $response["success"] = 0;
        $response["message"][7] = "ERROR: DB reset failed";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
