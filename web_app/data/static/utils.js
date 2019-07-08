//delete row if button with .ibtnDel click
$("#table").on("click", ".ibtnDel", function (e, value, row, index) {
    //$(this).closest("tr").remove();
    alertify.notify("Link removed ..... ", 'error', 5)
    var $table = $('#table')
    var ids = $.map($table.bootstrapTable('getSelections'), function (row) {
        return row.id;
    });
    $('#table').bootstrapTable('remove', {
        field: 'id',
        values: ids
    });
})

//functio to add another row in demands_table
function add_row_demands(){
	var newRow = $("<tr>");
        var cols = "";
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //status
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //id
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //index
            cols += '<td>' + 'source-edit-me' + '</td>'; //source
            cols += '<td>' + 'target-edit-me' + '</td>'; //target
            cols += '<td>' + 'demand-edit-me' + '</td>'; //demand
            cols += '<td><input type="button" class="ibtnDel btn btn-sm btn-danger "  value="Delete"></td>'; //action
            cols += '</tr>'
        newRow.append(cols);
        console.log(newRow)
        console.log(cols)
        $("#demands_table").append(newRow);
        var jsonTable = new JSONTable($("#demands_table"))
        var new_data= jsonTable.toJSON()
        $('#demands_table').bootstrapTable("load", new_data);
}

$('#add_row_demands').click(function() { add_row_demands() })
// delete row for demands ( lame repeat of code , fix me !!! ) 
//delete row if button with .ibtnDel click
$("#demands_table").on("click", ".ibtnDel", function (e, value, row, index) {
    //$(this).closest("tr").remove();
    alertify.notify("Demand removed ..... ", 'error', 5)
    var $table = $('#demands_table')
    var ids = $.map($table.bootstrapTable('getSelections'), function (row) {
        return row.id;
    });
    $('#demands_table').bootstrapTable('remove', {
        field: 'id',
        values: ids
    });
})
//
//function to add another row ( add both the form and reverse ) 
function editObject() {
    if ($('#add-link-form').parsley().validate() ) {
        var entry = $('#add-link-form').serializeArray()
        var newRow = $("<tr>");
        var cols = "";
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //status
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //id
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //index
            cols += '<td>' + entry[0].value + '</td>'; //source
            cols += '<td>' + entry[1].value + '</td>'; //target
            cols += '<td>' + entry[2].value + '</td>'; //l_ip
            cols += '<td>' + entry[4].value + '</td>'; //metric
            cols += '<td>' + Math.floor(Math.random() * 100) + '</td>'; //l_int
            cols += '<td>' + entry[3].value + '</td>'; //r_ip
            cols += '<td>'+'('+  entry[2].value + ',' + entry[3].value + ')'+'</td>'; //lip_rip_pair
            cols += '<td>' + 0 + '</td>';  //util
            cols += '<td>' + entry[5].value + '</td>'; //capacity
            cols += '<td><input type="button" class="ibtnDel btn btn-sm btn-danger "  value="Delete"></td>';
            cols += '</tr>'
        newRow.append(cols);
        console.log(newRow)
        $("#table").append(newRow);
        //reverse
        var newRow_rev = $("<tr>");
        var cols_rev = "";
            cols_rev += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //status
            cols_rev += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //id
            cols_rev += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //index
            cols_rev += '<td>' + entry[1].value + '</td>'; //source
            cols_rev += '<td>' + entry[0].value + '</td>'; //target
            cols_rev += '<td>' + entry[3].value + '</td>'; //l_ip
            cols_rev += '<td>' + entry[4].value + '</td>'; //metric
            cols_rev += '<td>' + Math.floor(Math.random() * 100) + '</td>'; //l_int
            cols_rev += '<td>' + entry[2].value + '</td>'; //r_ip
            cols_rev += '<td>'+'('+  entry[2].value + ',' + entry[3].value + ')'+'</td>'; //lip_rip_pair
            cols_rev += '<td>' + 0 + '</td>'; //util
            cols_rev += '<td>' + entry[5].value + '</td>'; //capacity
            cols_rev += '<td><input type="button" class="ibtnDel btn btn-sm btn-danger "  value="Delete"></td>';
        console.log(cols_rev)
        newRow_rev.append(cols_rev);
        $("#table").append(newRow_rev);
        //reload data into the table to allow modify of the metric
        var jsonTable = new JSONTable($("#table"))
        var new_data= jsonTable.toJSON()
        $('#table').bootstrapTable("load", new_data);
        alertify.notify("Link added ..... ", 'success', 5)

    }
}

//insert delete button for all rows
function TableActions (value, row, index) {
    return [
        '<input type="button" class="ibtnDel btn btn-sm btn-danger "  value="Delete">'
    ].join('');
}

//reset only demands
function reset_demand_only() {
    console.log('reset_demand_only')
    $('#table').bootstrapTable('resetSearch', '');
    var jsonTable = new JSONTable($("#table"))
    var new_data= jsonTable.toJSON()
    new_data.forEach( function (d) { 
        d.util =0 })
    $('#table').bootstrapTable("load", new_data);
}

//forcast function 
function forecast_data(df_bps, df_bps_lower, df_bps_upper) {
    // create selector
    var selectorOptions = {
        buttons: [
	{
            step: 'all',
        }],
    };
    // //prepare the graph

    var data = [prepData_bps(df_bps), prepData_bps_lower(df_bps_lower), prepData_bps_upper(df_bps_upper)];

    var layout = {
        showlegend: true,
        autoresize: true,
        width: document.getElementById('graph_forecast').clientWidth,
        height: 371,
        title: 'Traffic Forecast',
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
            title: 'Mbps'
        }
    };

    Plotly.newPlot('graph_forecast', data, layout);

    // //prepare the data
    function prepData_bps(rawData) {
        xField = 'ds'
        yField = 'bps'
        var x = [];
        var y = [];

        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            marker: {color: 'red'},
            name: 'Trend',
            x: x,
            y: y
        }; }
    function prepData_bps_lower(rawData) {
        xField = 'ds'
        yField = 'bps_lower'
        var x = [];
        var y = [];

        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            line: {width: 1, color: '#1705ff'},
            name: 'lower band',
            x: x,
            y: y
        }; }
    function prepData_bps_upper(rawData) {
        xField = 'ds'
        yField = 'bps_upper'
        var x = [];
        var y = [];

        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            fill: 'tonexty',
            line: {color: '#57b88f'},
            name: 'upper band',
            x: x,
            y: y
        }; }
}

function graph_aggr_year(data,capacity,graph_id,source_cc,target_cc) {

    var rawDataURL = data
    console.log(rawDataURL)
    // // map the fields
    var xField = 'time';
    var yField = 'bps';
    // / create selector
    var selectorOptions = {
        buttons: [{
            step: 'hour',
            stepmode: 'backward',
            count: 24,
            label: '24h'
        }, {
            step: 'day',
            stepmode: 'backward',
            count: 14,
            label: '2weeks'
        }, {
            step: 'month',
            stepmode: 'backward',
            count: 1,
            label: '1month'
        }, {
            step: 'month',
            stepmode: 'backward',
            count: 6,
            label: '6months'
        }, {
            step: 'all',
            label: '1year'
        }],
    };
    // //prepare the graph
    var data = prepData(data);
    var layout = {
        showlegend: true,
        autoresize: true,
        width: document.getElementById(graph_id).clientWidth,
        height: 371,
        title: source_cc + ' to ' + target_cc + ' Capacity: ' + capacity + ' Mbps',
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
            title: 'Mbps'
        }
    };

    Plotly.newPlot(graph_id, data, layout);

    // //prepare the data
    function prepData(rawData) {
        var x = [];
        var y = [];

        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return [{
            mode: 'lines',
            connectgaps: 'false',
            fill: 'tonexty',
            line: {width: 1, shape: 'spline', color: 'rgb(153, 204, 255)'},
            name: 'Total Traffic',
            x: x,
            y: y
        }]; }
}
