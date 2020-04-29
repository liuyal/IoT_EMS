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
        let url = "http://localhost/IoT_Environment_Monitor_System/backend/php/get_status.php";
        RequestData(url, function (json) {
            var data = json;
            var online = data["data"]["online"];
            var temp = data["data"][0]["last_temp"];
            var hum = data["data"][0]["last_hum"];
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

    let url = "http://localhost/IoT_Environment_Monitor_System/backend/php/get_status.php";
    
    RequestData(url, function (data) {
        var packet = data;
        console.log(packet)
        
        var ctx = document.getElementById("tempChart");

        var myChart = new Chart(ctx, {
            type: 'line',

            data: {

                labels: [1, 2, 3, 4],

                datasets: [{
                        label: "Data",
                        backgroundColor: "#e755ba",
                        // Insert styling, colors etc here
                        data: [
                                {x: 1, y: 127},
                                {x: 2, y: 140},
                                {x: 3, y: 135},
                                {x: 4, y: 122}
                              ]
                }]
            }
        });
        
        
        
    });
}












