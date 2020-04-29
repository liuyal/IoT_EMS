<?php
    ini_set("display_errors","on");
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");
    $db_name = DB_DATABASE;

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

    if (isset($_GET["table"])) {
        $table = $_GET["table"];
    } else {
        $response["message"][0] = "Parameter(s) are missing (table). Please check request";
        $response["success"] = 0;
        echo json_encode($response);
        exit;
    }

    if ($table == "nova"){
        $result_drop = mysqli_query($connect, "DROP DATABASE $db_name;");
        $result_create = mysqli_query($connect, "CREATE DATABASE $db_name;");
        $db = mysqli_select_db($connect, DB_DATABASE);
        $result1 = mysqli_query($connect,"CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));");
        $result2 = mysqli_query($connect,"CREATE Table nodes(mac VARCHAR(17), ip CHAR(39), port INT, start_time BIGINT, time_stamp BIGINT, status boolean, display boolean DEFAULT False, PRIMARY KEY (mac));");
        $result3 = mysqli_query($connect,"CREATE Table system_config(host_ip CHAR(39), host_port INT);");
        $result4 = mysqli_query($connect,"CREATE TABLE daily_avg(mac VARCHAR(17), date BIGINT, avg_temp DECIMAL (18, 2), avg_hum DECIMAL (18, 2), PRIMARY KEY (mac, date));");
        
        if ($result_drop) { $response["message"][1] = "Drop DB successfully"; }
        else { $response["message"][1] = "ERROR: Failed to drop DB"; }

        if ($result_create) { $response["message"][2] = "Create DB successfully"; }
        else { $response["message"][2] = "ERROR: Failed to create DB"; }

        if ($result1) { $response["message"][3] = "data Table created successfully"; }
        else { $response["message"][3] = "ERROR: DB failed to create data table"; }

        if ($result2) { $response["message"][4] = "nodes Table created successfully"; }
        else { $response["message"][4] = "ERROR: DB failed to create nodes table"; }

        if ($result3) { $response["message"][5] = "system_config Table created successfully"; }
        else { $response["message"][5] = "ERROR: DB failed to create system_config table"; }
        
        if ($result4) { $response["message"][6] = "daily_avg Table created successfully"; }
        else { $response["message"][6] = "ERROR: DB failed to create daily_avg table"; }

        if ($result1 && $result2 && $result3 && $result4) {
            $response["success"] = 1;
            $response["message"][7] = "DataBase $table reset successfully complete";
        } else {
            $response["success"] = 0;
            $response["message"][7] = "ERROR: DataBase $table reset failed";
        }
    } else {
        $result_T = mysqli_query($connect, "TRUNCATE TABLE $table");
        if ($result_T) {
            $response["success"] = 1;
            $response["message"][1] = "Table: $table cleared";
        }
        else {
            $response["success"] = 0;
            $response["message"][1] = "Table: $table failed to clear";
        }
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
