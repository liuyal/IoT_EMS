var colors = ["#3cba9f", "#3e95cd", "#8e5ea2", "#e8c3b9", "#c45850", ];

var tempchart;

var humchart;

var last_time_plot = {};

var chart_config1 = {
    type: 'line',
    data: {
        labels: []
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: 'white',
                    beginAtZero: true
                },
                gridLines: {
                    display: false,
                    color: "rgba(0, 0, 0, 0)",
                }
                }],
            xAxes: [{
                ticks: {
                    fontColor: 'white',
                    beginAtZero: true
                },
                gridLines: {
                    
                    color: "rgba(0, 0, 0, 0)",
                }
                }]
        },
        legend: {
            display: true,
            labels: {
                fontColor: 'rgb(255, 255, 255)'
            }
        }
    }
};

var chart_config2 = {
    type: 'line',
    data: {
        labels: []
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: 'white',
                    beginAtZero: true
                },
                gridLines: {
                     display: false,
                    color: "rgba(0, 0, 0, 0)",
                }
                }],
            xAxes: [{
                ticks: {
                    fontColor: 'white',
                    beginAtZero: true
                },
                gridLines: {
                    color: "rgba(0, 0, 0, 0)",
                }
                }]
        },
        legend: {
            display: true,
            labels: {
                fontColor: 'rgb(255, 255, 255)'
            }
        }
    }
};



function load_graph_data() {
    let url = "http://localhost/IoT_Environment_Monitor_System/backend/php/node_current_status.php";
    RequestData(url, function (packet) {

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
        }


        for (let [key] of Object.entries(data)) {

            var tempDataset = {
                label: key,
                borderWidth: 2,
                backgroundColor: "rgba(0,0,0,0.0)",
                pointBackgroundColor: colors[Object.keys(data).indexOf(key)],
                borderColor: colors[Object.keys(data).indexOf(key)],
                data: data[key]["temp"]
            };

            var humDataset = {
                label: key,
                borderWidth: 2,
                backgroundColor: "rgba(0,0,0,0.0)",
                pointBackgroundColor: colors[Object.keys(data).indexOf(key)],
                borderColor: colors[Object.keys(data).indexOf(key)],
                data: data[key]["hum"]
            };

            tempchart.data.labels = data[key]["time"];
            humchart.data.labels = data[key]["time"];
            tempchart.data.datasets.push(tempDataset);
            humchart.data.datasets.push(humDataset);
            humchart.update();
            tempchart.update();
            console.log(data[key]);
        }
    });
}


String.prototype.toHHMMSS = function () {
    var date = new Date(parseInt(this, 10) * 1000);
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();

    if (hours < 10) hours = "0".concat(hours);
    if (minutes < 10) minutes = "0".concat(minutes);
    if (seconds < 10) seconds = "0".concat(seconds);

    return hours + ':' + minutes;
}
