<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $response = array();
    $db_name = DB_DATABASE;

    try 
    {
        $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD) or die(mysqli_error());
        $response["message"][0] = "Server Connected successfully";

        mysqli_query($connect, "DROP DATABASE $db_name;");
        $response["message"][1] = "Drop DB successfully";

        mysqli_query($connect, "CREATE DATABASE $db_name;");
        $response["message"][2] = "Create DB successfully";

        $db = mysqli_select_db($connect, DB_DATABASE) or die(mysqli_error());
        
        $result = mysqli_query($connect,"create table data(mac CHAR(20), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (mac, time) );") or die(mysqli_error());
    }
    catch(PDOException $e) 
    {
        $response["Server_connection_MSG"] = "Server Connection failed: " . $e->getMessage();
    }
     
    if ($result)  
    {
        $response["success"] = 1;
        $response["message"][3] = "DB reset successfully";
    }
    else 
    {
        $response["success"] = 0;
        $response["message"][3] = "ERROR: DB reset failed";
    }

    echo json_encode($response);

    mysqli_close($connect);
?>




