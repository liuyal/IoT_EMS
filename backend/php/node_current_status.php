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
    
    $check_online = mysqli_query($connect, "SELECT COUNT(*) as count FROM nodes WHERE status=true;");
    $n_online = mysqli_fetch_assoc($check_online);

    if ($check_online) { $response["online"] = $n_online["count"]; }
    else { $response["online"] = 0; }

    $get_mac = mysqli_query($connect, "SELECT mac FROM nodes WHERE display=true;");
    if ($get_mac->num_rows == 0) {
        $response["success"] = 0;
        $response["message"][1] = "No Nodes to Display";
        echo json_encode($response);
        exit;
    }

    $limit = 60;
    $history = false;
    $counter = 0;
    
    while ($row = mysqli_fetch_array($get_mac)) {
        
        $mac = $row["mac"];
        $history = mysqli_query($connect, "SELECT mac, time, temp, hum FROM data WHERE mac='$mac' ORDER BY time DESC LIMIT $limit;");
        $data = mysqli_fetch_all($history);

        if ($history && count($data) > 0 && count($data) == $limit) {
            $response["message"][$counter + 1] = "Fresh data found for $mac";
            $response["data"][$counter]["mac"] = $mac;
            $response["data"][$counter]["last_time"] = $data[0][1];
            $response["data"][$counter]["last_temp"] = $data[0][2];
            $response["data"][$counter]["last_hum"] = $data[0][3];
            $response["data"][$counter]["history"] = $data;
        } else if ($history && count($data) > 0 && count($data) < $limit) {
           
            $missing = $limit - count($data);
            $epoch = intval($data[count($data) - 1][1]) - 86000;
            $dt = new DateTime("@$epoch");
            $table = $dt->format("Ymd") . "_data";

            $history2 = mysqli_query($connect, "SELECT mac, time, temp, hum FROM $table WHERE mac='$mac' ORDER BY time DESC LIMIT $missing;");
            
            if ($history2) {
                $data2 = mysqli_fetch_all($history2);
                $response["message"][$counter + 1] = "Fresh data found for $mac";
                $response["data"][$counter]["mac"] = $mac;
                $response["data"][$counter]["last_time"] = $data[0][1];
                $response["data"][$counter]["last_temp"] = $data[0][2];
                $response["data"][$counter]["last_hum"] = $data[0][3];
                $response["data"][$counter]["history"] = array_merge($data, $data2);
            } else {
                $response["message"][$counter + 1] = "Fresh data found for $mac, (<1H)";
                $response["data"][$counter]["mac"] = $mac;
                $response["data"][$counter]["last_time"] = $data[0][1];
                $response["data"][$counter]["last_temp"] = $data[0][2];
                $response["data"][$counter]["last_hum"] = $data[0][3];
                $response["data"][$counter]["history"] = $data;
            }

        } else {
            $response["message"][$counter + 1] = "No data found for $mac";
            $response["data"][$counter]["mac"] = $mac;
            $response["data"][$counter]["last_time"] = 0;
            $response["data"][$counter]["last_temp"] = 0;
            $response["data"][$counter]["last_hum"] = 0;
            $response["data"][$counter]["history"] = [0];   
        }
        $counter++;
    }

    if ($history && $check_online) {
        $response["success"] = 1;
    } else {
        $response["success"] = 0;
    }
    
    echo json_encode($response);
    mysqli_close($connect);
?>


