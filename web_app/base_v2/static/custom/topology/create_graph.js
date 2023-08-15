function graph(web_ip,graph_url,source,interface,capacity) {
    console.log('this is the web_ip inside graph function - ????????',web_ip,graph_url)
    Plotly.purge(graph2)
    var url = web_ip+'?ip='+interface+'&'+'host='+source
    //var url1 = {{ url_for('api_blueprint.get_forecast')|tojson }}
    //console.log('this is the url1 inside graph',url1)
    var interface_name = $.ajax({type: "GET", url: url, async: false, dataType:'json'}).responseText;
    //console.log(url)
    var rawDataURL = graph_url+'?ip='+interface+'&'+'host='+source
    console.log('rawDataURL',rawDataURL)
    //// map the fields 
    var xField = 'time';
    var yField = 'bps';
    /// create selector 
    var selectorOptions = {
        buttons: [{
            step: 'minute',
            stepmode: 'backward',
            count: 30,
            label: '30m'
        }, {
            step: 'hour',
            stepmode: 'backward',
            count: 1,
            label: '1h'
        }, {
            step: 'hour',
            stepmode: 'todate',
            count: 3,
            label: '3h'
        }, {
            step: 'hour',
            stepmode: 'todate',
            count: 6,
            label: '6h'
        }, {
            step: 'all',
        }],
    };
    ////prepare the graph
    Plotly.d3.csv(rawDataURL, function(err, rawData) {
        var width = document.getElementById("graph2").clientWidth - 30
        console.log('rawData->',rawData)
        if(err) throw err;
        var data = prepData(rawData);
        var layout = {
            showlegend: true,
            autoresize: true,
            width: width,
            height: 360,
            title: 'Router: ' + source + ' Interface: '+ interface_name + ' Speed: ' + capacity +' Mbps',
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
            name: interface_name,
            x: x,
            y: y
        }];

    }
}

