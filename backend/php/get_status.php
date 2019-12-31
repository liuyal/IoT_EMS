<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD);
    $db = mysqli_select_db($connect, DB_DATABASE);

    if (isset($_GET['range'])) {
        $range = $_GET['range'];
    }
    else {
        $response["message"][0] = "Missing input parameters";
        $response["success"] = 0;
        echo json_encode($response);
        exit;
    }

    if ($db) {
        $response["message"][0] = "Server Connected successfully";
    }
    else {
        $response["success"] = 0;
        $response["message"][0] = "Server Connection failed";
        echo json_encode($response);
        exit;
    }

    if (strstr( $range, "current")) {
        // TODO: pick mac in sys_config
        $n_online = mysqli_query($connect, "SELECT COUNT(*) as count FROM nodes WHERE status=true;");
        $temp_hum = mysqli_query($connect, "SELECT * FROM data ORDER BY time DESC LIMIT 1;");
        $count = mysqli_fetch_assoc($n_online);
        $data = mysqli_fetch_assoc($temp_hum);

        if ($n_online) {
            $response["message"]["online"] = $count["count"];
        }
        else {
            $response["message"]["online"] = 0;
        }

        if ($data) {
            $response["message"][1] = "Fresh Data Found";
            $response["message"]["mac"] = $data["mac"];
            $response["message"]["temp"] = $data["temp"];
            $response["message"]["hum"] = $data["hum"];
            $response["success"] = 1;
        }   
        else {
            $response["message"][1] = "No Data Found";
            $response["message"]["mac"] = "00:00:00:00:00:00";
            $response["message"]["temp"] = 0.00;
            $response["message"]["hum"] = 0.00;
            $response["success"] = 0;
        }
    }
    else if (strstr( $range, "hour")) {

    }
    else if (strstr( $range, "day")) {

    }
    else if (strstr( $range, "month")) {

    }
    else if (strstr( $range, "year")) {

    }
    else {
        $response["success"] = 0;
        $response["message"][0] = "Incorrect incorrect parameter";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>


