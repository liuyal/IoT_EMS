
function load_fresh() {

    window.setInterval(function () {
        var time = new Date();
        var h = ("0" + time.getUTCHours()).slice(-2);
        var m = ("0" + time.getUTCMinutes()).slice(-2);
        var s = ("0" + time.getUTCSeconds()).slice(-2);
        document.getElementById('current_time').innerHTML = h + ":" + m + ":" + s;
//        console.log( h + ":" + m + ":" + s);








    }, 1000);


    //    var xhttp = new XMLHttpRequest();
    //    xhttp.onreadystatechange = function () {
    //        if (this.readyState == 4 && this.status == 200) {
    //            document.getElementById("data").innerHTML = this.responseText;
    //        }
    //    };
    //    xhttp.open("GET", "http://localhost/php/show_tables.php", true);
    //    xhttp.send();
}
