function addData(chart, label, data) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
    });
    chart.update();
}


function load_graph_data() {

    let url = "http://localhost/IoT_Environment_Monitor_System/backend/php/node_current_status.php";

    RequestData(url, function (data) {
        var packet = data;
        
        var history = data["history"];
        
        
        
        
        var tempData = [];
        var humData = [];
        
        
        
        
        console.log(packet)
    });


    var ctx = document.getElementById("tempChart");



}
