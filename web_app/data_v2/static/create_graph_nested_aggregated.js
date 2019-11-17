function graph(web_ip,source,target,capacity) {
    Plotly.purge(graph2)
    var rawDataURL = 'http://'+web_ip+':8801/api/graph_aggregated?'+'source='+source+'&'+'target='+target
    //console.log(rawDataURL)
    //// map the fields
    var xField = 'time';
    var yField = 'bps';
    /// create selector
    var selectorOptions = {
        buttons: [{
            step: 'hour',
            stepmode: 'backward',
            count: 24,
            label: '24h'
        }, {
            step: 'day',
            stepmode: 'backward',
            count: 2,
            label: '2d'
        }, {
            step: 'day',
            stepmode: 'backward',
            count: 14,
            label: '14d'
        }, {
            step: 'day',
            stepmode: 'backward',
            count: 30,
            label: '1m'
        }, {
            step: 'all',
        }],
    };
    ////prepare the graph
    Plotly.d3.csv(rawDataURL, function(err, rawData) {
        var width = document.getElementById("graph2").clientWidth - 30
        if(err) throw err;
        var data = prepData(rawData);
        var layout = {
            showlegend: true,
            autoresize: true,
            width: width,
            height: 360,
            title: 'Country: ' + source + ' to ' + target + ' Speed: ' + capacity +' Mbps',
            xaxis: {
                fixedrange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                type: 'date',
                title: 'Time',
            },
            yaxis: {
                fixedrange: true,
                autotick: true,
                autorange: true,
                tickformat: ".3s",
                title: 'bps'
            }
        };

        Plotly.newPlot('graph2', data, layout);
    });
    ////prepare the data
    function prepData(rawData) {
        var x = [];
        var y = [];

        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]);
        });

        return [{
            mode: 'lines',
            connectgaps: 'false',
            fill: 'tonexty',
            line: { width: 1 , shape: 'spline' , color: 'rgb(153, 204, 255)' },
            name: 'Traffic',
            x: x,
            y: y
        }];

    }
}

