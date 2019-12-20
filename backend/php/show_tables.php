<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();

    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    try {
        $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD);
        $db = mysqli_select_db($connect, DB_DATABASE);
        $response["message"][0] = "Server Connected successfully";
    }
    catch(PDOException $e){
        $response["message"][0] = "Server Connection failed: " . $e->getMessage();
    }

    $result = mysqli_query($connect, "show tables;");
     
    if (mysqli_num_rows($result) > 0) {
        $response["data"] = array();

        while ($row = mysqli_fetch_array($result)) {
            $data = array();
            $data["table"] = $row["Tables_in_nova"];
            array_push($response["data"], $data);
        }
        $response["success"] = 1;
        $response["message"][1] = "Tables found successfully";
    }	
    else {
    	$response["success"] = 0;
        $response["message"][1] = "No tables found";
        
    }
    echo json_encode($response);
    mysqli_close($connect);
?>
