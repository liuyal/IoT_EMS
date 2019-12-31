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
    }
    else {
        $response["success"] = 0;
        $response["message"][0] = "Server Connection failed";
        echo json_encode($response);
        exit;
    }
    
    $n_online = mysqli_query($connect, "SELECT COUNT(*) as count FROM nodes WHERE status=true;");
    $count = mysqli_fetch_assoc($n_online);

    $get_mac = mysqli_query($connect, "SELECT display_mac as mac FROM system_config;");
    $mac_array = mysqli_fetch_assoc($get_mac);
    $mac = implode($mac_array);

    $temp_hum = mysqli_query($connect, "SELECT * FROM data WHERE mac='$mac' ORDER BY time DESC LIMIT 1;");
    $data = mysqli_fetch_assoc($temp_hum);

    $history = mysqli_query($connect, "SELECT temp, hum FROM data WHERE mac='$mac' ORDER BY time DESC LIMIT 60;");
    $last_hour = mysqli_fetch_assoc($history);


    if ($data && $n_online) {
        $response["message"][1] = "Fresh Data Found";
        $response["data"]["online"] = $count["count"];
        $response["data"]["mac"] = $data["mac"];
        $response["data"]["temp"] = $data["temp"];
        $response["data"]["hum"] = $data["hum"];
        $response["data"]["history"] = [0];
        $response["success"] = 1;
    }   
    else {
        $response["message"][1] = "No Data Found";
        $response["data"]["online"] = 0;
        $response["data"]["mac"] = "00:00:00:00:00:00";
        $response["data"]["temp"] = 0.00;
        $response["data"]["hum"] = 0.00;
        $response["data"]["history"] = [0];
        $response["success"] = 0;
    }

    echo json_encode($response);
    mysqli_close($connect);
?>


