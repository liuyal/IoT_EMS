$(document).ready(function () {
    tempchart = new Chart(document.getElementById('tempChart'), chart_config1);
    humchart = new Chart(document.getElementById('humChart'), chart_config2);
    load_graph_data();
})


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
        let url = "http://localhost/IoT_Environment_Monitor_System/backend/php/node_current_status.php";
        RequestData(url, function (packet) {
            var dataPacket = packet;
            var online = dataPacket["online"];
            var time = dataPacket["data"][0]["last_time"];
            var temp = dataPacket["data"][0]["last_temp"];
            var hum = dataPacket["data"][0]["last_hum"];
            document.getElementById('n_online').innerHTML = online;
            document.getElementById('temp').innerHTML = temp + "&ordm;C";
            document.getElementById('hum').innerHTML = hum + "%";
            document.getElementById('current_time').innerHTML = hms;
            if (online == 0) document.getElementById('wifi_on').innerHTML = "wifi_off";
            else document.getElementById('wifi_on').innerHTML = "wifi";
        });
    }, 1000);
    
}





