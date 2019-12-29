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

    // TODO: get current, last hour, day, month, year

    $n_online = mysqli_query($connect, "SELECT COUNT(*) as count FROM nodes WHERE status=true;");
    $temp_hum = mysqli_query($connect, "SELECT * FROM data ORDER BY time DESC LIMIT 1;");

    $count = mysqli_fetch_assoc($n_online);
    $data = mysqli_fetch_assoc($temp_hum);

    if ($n_online) {
        $response["message"]["online"] = $count["count"];
    }
    else {
        $response["message"]["online"] = 0;
    }

    if ($data) {
        $response["message"][1] = "Fresh Data Found";
        $response["message"]["mac"] = $data["mac"];
        $response["message"]["temp"] = $data["temp"];
        $response["message"]["hum"] = $data["hum"];
        $response["success"] = 1;
    }   
    else {
        $response["message"][1] = "No Data Found";
        $response["message"]["mac"] = "00:00:00:00:00:00";
        $response["message"]["temp"] = 0.00;
        $response["message"]["hum"] = 0.00;
        $response["success"] = 0;
    }

    echo json_encode($response);
    mysqli_close($connect);
?>
