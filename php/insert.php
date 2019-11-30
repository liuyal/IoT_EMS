<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $response = array();

    if (isset($_GET['mac']) && isset($_GET['time']) && isset($_GET['temp']) && isset($_GET['hum'])) {
        
        $mac = $_GET['mac'];
        $time = $_GET['time'];
        $temp = $_GET['temp'];
        $hum = $_GET['hum'];
     
        try 
        {
            $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD);
            $db = mysqli_select_db($connect, DB_DATABASE);
            $response["message"][0] = "Server Connected successfully";
        }
        catch(PDOException $e)
        {
            $response["message"][0] = "Server Connection failed: " . $e->getMessage();
        }
     
        $result = mysqli_query($connect, "INSERT INTO data(mac,time,temp,hum) VALUES('$mac','$time','$temp','$hum');");

        if ($result) 
        {
            $response["success"] = 1;
            $response["message"][1] = "Data successfully inserted";
        } 
        else 
        {
            $response["success"] = 0;
            $response["message"][1] = "Data failed to insert";
        }
    } 
    else 
    {
        $response["success"] = 0;
        $response["message"][0] = "Parameter(s) are missing. Please check the request";
    }
    echo json_encode($response);
    mysqli_close($connect);
?>
