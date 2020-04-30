function addData(chart, label, data) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
    });
    chart.update();
}


function load_graph_data() {

    let url = "http://localhost/IoT_Environment_Monitor_System/backend/php/node_current_status.php";

    RequestData(url, function (packet) {
        
        var packet = packet;
        
        
        for (i = 0; i < Object.keys(packet["data"]).length; i++) {

            
            
            var mac_packet = packet["data"][i];
            
            
            var history = mac_packet["history"];
            
            
            
            console.log(mac_packet);
            console.log(history);
        }
        
        
        
        
        
        
        
        
    });


    var ctx = document.getElementById("tempChart");



}
