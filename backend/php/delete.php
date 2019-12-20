<?php
    ini_set('display_errors','on');
    header('content-type: application/json; charset=utf-8');
    header("access-control-allow-origin: *");
    
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    $response = array();


    if (isset($_GET['mac']) && isset($_GET['time'])) {
        $mac = $_GET['mac'];
        $time = $_GET['time'];    

        if (isset($_GET['table'])) {$table = $_GET['table'];}
        else {$table = "data";}
        
        try {
            $connect = mysqli_connect(DB_SERVER, DB_USER, DB_PASSWORD) or die(mysqli_error());
            $db = mysqli_select_db($connect, DB_DATABASE) or die(mysqli_error());
            $response["message"][0] = "Server Connected successfully";
        }
        catch(PDOException $e){
            $response["message"][0] = "Server Connection failed: " . $e->getMessage();
        }

        $result = mysqli_query($connect, "DELETE FROM $table WHERE mac=$mac and time=$time");
     
        if (mysqli_affected_rows($connect) > 0) {
            $response["success"] = 1;
            $response["message"][1] = "Data successfully deleted";
        } 
        else {
            $response["success"] = 0;
            $response["message"][1] = "No data found in by given mac & time";
        }
    } 
    else {
        $response["success"] = 0;
        $response["message"][0] = "Parameter(s) are missing. Please check the request";
    }
    echo json_encode($response);
    mysqli_close($connect);
?>
