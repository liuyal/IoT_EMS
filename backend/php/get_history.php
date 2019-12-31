<?php
    ini_set("display_errors","on");
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD);
    $db = mysqli_select_db($connect, DB_DATABASE);

    if (isset($_GET["range"])) {
        $range = $_GET["range"];
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
    
    }
    else if (strstr( $range, "hourly")) {

    }
    else if (strstr( $range, "daily")) {

    }
    else if (strstr( $range, "monthly")) {

    }
    else if (strstr( $range, "yearly")) {

    }
    else {
        $response["success"] = 0;
        $response["message"][0] = "Incorrect incorrect parameter";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>


