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

    $result = mysqli_query($connect, "SHOW TABLES;");
     
    if ($result && mysqli_num_rows($result) > 0) {
        $response["data"] = array();
        while ($row = mysqli_fetch_array($result)) {
            $data = array();
            $data["table"] = $row["Tables_in_nova"];
            array_push($response["data"], $data);
        }
        $response["success"] = 1;
        $response["message"][1] = "Tables found successfully";
    } else {
    	$response["success"] = 0;
        $response["message"][1] = "Empty database, no tables found";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
