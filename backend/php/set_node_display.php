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
    catch(PDOException $e){$response["message"][0] = "Server Connection failed: " . $e->getMessage();}

    if (isset($_GET['mac']) && isset($_GET['display'])) {
        
        $mac = $_GET['mac'];
        $display = $_GET['display'];

        $find_mac = mysqli_query($connect, "SELECT mac FROM nodes WHERE mac='$mac';");

        if ($find_mac->num_rows == 0) { 
            $response["success"] = 0;
            $response["message"][0] = "MAC: $mac not found in table";
        }
        else{ 

            $result = false;

            if ($display == "true"){
                $result = mysqli_query($connect, "UPDATE nodes SET display=true WHERE mac='$mac';");
            }
            else if ($display == "false") {
                $result = mysqli_query($connect, "UPDATE nodes SET display=false WHERE mac='$mac';");
            }
            else{
                $response["success"] = 0;
                $response["message"][0] = "Invalid display input: $display";
            }

            if ($result && ($display == true || $display == false) ){
                $response["success"] = 1;
                $response["message"][0] = "Display set to $display for Node: $mac";
            }
        }
    }
    else{
        $response["success"] = 0;
        $response["message"][0] = "Parameter(s) are missing. Please check request";
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
