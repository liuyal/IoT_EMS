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

            /*TODO: push fresh value and pop old value*/

            var data = {};
            var index = []
            for (i = 0; i < Object.keys(packet["data"]).length; i++) {
                data[packet["data"][i]["mac"]] = [];
                data[packet["data"][i]["mac"]]["temp"] = [];
                data[packet["data"][i]["mac"]]["hum"] = [];
                data[packet["data"][i]["mac"]]["time"] = [];

                for (j = packet["data"][i]["history"].length - 1; j >= 0; j--) {
                    var data_index = packet["data"][i]["history"].length - 1 - j;
                    data[packet["data"][i]["mac"]]["time"][data_index] = packet["data"][i]["history"][j][1].toHHMMSS();
                    data[packet["data"][i]["mac"]]["temp"][data_index] = packet["data"][i]["history"][j][2];
                    data[packet["data"][i]["mac"]]["hum"][data_index] = packet["data"][i]["history"][j][3];
                    index[j] = j;
                }

                var last_time = packet["data"][i]["history"][0][1];
                var last_temp = packet["data"][i]["history"][0][2];
                var last_hum = packet["data"][i]["history"][0][3];


                if (packet["data"][i]["history"].length < 30) {

                    
                    if (tempchart.getDatasetMeta(0).data[tempchart.getDatasetMeta(0).data.length - 1]._xScale.max != last_time.toHHMMSS()) {

                        tempchart.data.labels.push((last_time).toHHMMSS());
                        tempchart.data.datasets.forEach((database) => {
                            database.data.push(last_temp);
                        });
                        tempchart.update();
                    }

                } else {



                }
            }
        });
    }, 1000);
    
}





