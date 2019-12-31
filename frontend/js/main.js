function RequestData(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) {
            return;
        }
        if (xhr.status != 200) {
            console.log(xhr.status + ': ' + xhr.statusText);
        } else {
            callback(JSON.parse(xhr.responseText));
        }
    }
}


function load_fresh() {
    window.setInterval(function () {
        var time = new Date();
        var h = ("0" + time.getUTCHours()).slice(-2);
        var m = ("0" + time.getUTCMinutes()).slice(-2);
        var s = ("0" + time.getUTCSeconds()).slice(-2);
        var hms = h + ":" + m + ":" + s;
        let url = "http://localhost/Temperature_System/backend/php/get_status.php";
        RequestData(url, function (json) {
            var data = json;
            var online = data["data"]["online"];
            var temp = data["data"]["temp"];
            var hum = data["data"]["hum"];
            document.getElementById('n_online').innerHTML = online;
            document.getElementById('temp').innerHTML = temp + "&ordm;C";
            document.getElementById('hum').innerHTML = hum + "%";
            document.getElementById('current_time').innerHTML = hms;
            if (online == 0) {
                document.getElementById('wifi_on').innerHTML = "wifi_off";
            } else {
                document.getElementById('wifi_on').innerHTML = "wifi";
            }
        });
    }, 1000);
}


function load_graph_data() {

    let url = "http://localhost/Temperature_System/backend/php/select_from_table.php?table=data";
    RequestData(url, function (json) {
        var data = json["data"];
        
        console.log(data)


    });
}
