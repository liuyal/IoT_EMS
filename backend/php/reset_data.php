<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    try {
        $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD) or die(mysqli_error());
        $db = mysqli_select_db($connect, DB_DATABASE) or die(mysqli_error());
        $response["message"][0] = "Server Connected successfully";
    }
    catch(PDOException $e){
        $response["message"][0] = "Server Connection failed: " . $e->getMessage();
    }
     
    $result = mysqli_query($connect, "TRUNCATE TABLE data") or die(mysql_error());

    if ($result) {
        $response["success"] = 1;
        $response["message"][1] = "data Table cleared";
    }
    else {
        $response["success"] = 0;
        $response["message"][1] = "data Table failed to clear";
    }
    echo json_encode($response);
    mysqli_close($connect);
?>
