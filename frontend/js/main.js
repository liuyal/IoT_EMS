function load_table() {

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("data").innerHTML = this.responseText;
        }
    };
    xhttp.open("GET", "http://localhost/php/show_tables.php", true);
    xhttp.send();
}

