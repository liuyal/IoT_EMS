<?php
    ini_set('display_errors','on');
    header("Access-Control-Allow-Origin: *");
    header("Content-Type: application/json; charset=UTF-8");

    $response = array();
    $filepath = realpath (dirname(__FILE__));
    require_once($filepath."/dbconfig.php");

    if (isset($_GET['mac']) && isset($_GET['display'])) {
        $mac = $_GET['mac'];
        $display = $_GET['display'];
        
        if (!strstr( $display, 'true') && !strstr( $display, 'false')) {
            $response["success"] = 0;
            $response["message"][1] = "Invalid display input: $display";
            echo json_encode($response);
            exit;
        }
    }
    else{
        $response["success"] = 0;
        $response["message"][0] = "Parameter(s) are missing. Please check request";
        echo json_encode($response);
        exit;
    }

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

    $find_mac = mysqli_query($connect, "SELECT mac FROM nodes WHERE mac='$mac';");

    if ($find_mac && $find_mac->num_rows == 0) { 
        $response["success"] = 0;
        $response["message"][1] = "MAC: $mac not found in table";
    }
    else { 

        $result = mysqli_query($connect, "UPDATE nodes SET display=$display WHERE mac='$mac';");

        if ($result) {
            $response["success"] = 1;
            $response["message"][1] = "Display set to $display for Node: $mac";
        }
    }
    
    echo json_encode($response);
    mysqli_close($connect);
?>
