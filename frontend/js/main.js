function RequestData(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) {
            return;
        }
        if (xhr.status != 200) {
            alert(xhr.status + ': ' + xhr.statusText);
        } else {
            callback(JSON.parse(xhr.responseText));
        }
    }
}


function fresh_data() {
    const url = "http://localhost/Temperature_System/backend/php/get_fresh_data.php";
    RequestData(url, function (json) {
        var data = json;
        var online = data["message"]["online"];
        var temp = data["message"]["temp"];
        var hum = data["message"]["hum"];
        document.getElementById('n_online').innerHTML = online;
        document.getElementById('temp').innerHTML = temp+"&ordm;C";
        document.getElementById('hum').innerHTML = hum + "%";
    });
}


function load_fresh() {

    window.setInterval(function () {
        var time = new Date();
        var h = ("0" + time.getUTCHours()).slice(-2);
        var m = ("0" + time.getUTCMinutes()).slice(-2);
        var s = ("0" + time.getUTCSeconds()).slice(-2);
        document.getElementById('current_time').innerHTML = h + ":" + m + ":" + s;

        fresh_data();

    }, 1000);

}
