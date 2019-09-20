//test lsp add
//functio to add another row in lsp_table
function add_row_lsp(){
        var newRow = $("<tr>");
        var cols = "";
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //status
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //id
            cols += '<td>' + Math.floor(Math.random() * 900) + '</td>'; //index
            cols += '<td>' + 'gb-pe5-lon' + '</td>'; //source
            cols += '<td>' + 'gb-p10-lon' + '</td>'; //target
            cols += '<td>' + '10.5.8.8,10.8.10.10' + '</td>'; //ero
            cols += '<td>' + '1' + '</td>'; //metric
            cols += '<td>' + '0' + '</td>'; //util
            cols += '<td><input type="button" class="ibtnDel_lsp btn btn-sm btn-danger"  value="Delete"></td>'; //action
            cols += '</tr>'
        newRow.append(cols);
        console.log(newRow)
        $("#lsp_table").append(newRow);
        var jsonTable = new JSONTable($("#lsp_table"))
        var new_data_lsp= jsonTable.toJSON()
        $('#lsp_table').bootstrapTable("load", new_data_lsp);
}

$('#add_row_lsp').click(function() { add_row_lsp() })
// delete row for demands ( lame repeat of code , fix me !!! )
//delete row if button with .ibtnDel_lsp click
$("#lsp_table").on("click", ".ibtnDel_lsp", function (e, value, row, index) {
    console.log('did it click')
    //$(this).closest("tr").remove();
    alertify.notify("LSP removed ..... ", 'error', 5)
    var $table = $('#lsp_table')
    var ids = $.map($table.bootstrapTable('getSelections'), function (row) {
        return row.id;
    });
    $('#lsp_table').bootstrapTable('remove', {
        field: 'id',
        values: ids
    });
})

//end test lsp add 


//function to deepcopy an array of objects
function deep_copy(o) {
   var output, v, key;
   output = Array.isArray(o) ? [] : {};
   for (key in o) {
       v = o[key];
       output[key] = (typeof v === "object") ? deep_copy(v) : v;
   }
   return output;
}

//delete row if button with .ibtnDel click
$("#table").on("click", ".ibtnDel_topology", function (e, value, row, index) {
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
            cols += '<td>' + 'nl-p13-ams' + '</td>'; //source
            cols += '<td>' + 'ke-pe3-nbi' + '</td>'; //target
            cols += '<td>' + '500' + '</td>'; //demand
            cols += '<td><input type="button" class="ibtnDel_demands btn btn-sm btn-danger "  value="Delete"></td>'; //action
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
$("#demands_table").on("click", ".ibtnDel_demands", function (e, value, row, index) {
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
        newRow = []
        newRow[0] = Math.floor(Math.random() * 900)
        newRow[1] = Math.floor(Math.random() * 900)
        newRow[2] = Math.floor(Math.random() * 900)
        newRow[3] = entry[0].value
        newRow[4] = entry[1].value
        newRow[5] = entry[2].value
        newRow[6] = entry[4].value
        newRow[7] = Math.floor(Math.random() * 100)
        newRow[8] = entry[3].value
        newRow[9] = '(\'' +  entry[2].value + '\',\'' + entry[3].value + '\')'
        newRow[10] = 0
        newRow[11] = entry[5].value
        newRow[12] = ''

$(table).bootstrapTable('insertRow',{
            index: '',
            row: {
                state: newRow[0],
                id: newRow[1],
                index: newRow[2],
                source: newRow[3],
                target: newRow[4],
                l_ip: newRow[5],
                metric: newRow[6],
                l_int: newRow[7],
                r_ip: newRow[8],
                l_ip_r_ip: newRow[9],
                util: newRow[10],
                capacity: newRow[11],
                Action: '',
            }
         });

        //reverse
        newRow_rev = []
        newRow_rev[0] = Math.floor(Math.random() * 900)
        newRow_rev[1] = Math.floor(Math.random() * 900)
        newRow_rev[2] = Math.floor(Math.random() * 900)
        newRow_rev[3] = entry[1].value
        newRow_rev[4] = entry[0].value
        newRow_rev[5] = entry[3].value
        newRow_rev[6] = entry[4].value
        newRow_rev[7] = Math.floor(Math.random() * 100)
        newRow_rev[8] = entry[2].value
        newRow_rev[9] = '(\'' +  entry[2].value + '\',\'' + entry[3].value + '\')'
        newRow_rev[10] = 0
        newRow_rev[11] = entry[5].value
        newRow_rev[12] = ''

$(table).bootstrapTable('insertRow',{
            index: '',
            row: {
                state: newRow_rev[0],
                id: newRow_rev[1],
                index: newRow_rev[2],
                source: newRow_rev[3],
                target: newRow_rev[4],
                l_ip: newRow_rev[5],
                metric: newRow_rev[6],
                l_int: newRow_rev[7],
                r_ip: newRow_rev[8],
                l_ip_r_ip: newRow_rev[9],
                util: newRow_rev[10],
                capacity: newRow_rev[11],
                Action: '',
            }
         });
        alertify.notify("Link added ..... ", 'success', 5)

    }
}

//insert delete button for all rows
function TableActions (value, row, index) {
    return [
        '<input type="button" class="ibtnDel_topology btn btn-sm btn-danger "  value="Delete">'
    ].join('');
}

function TableActions_lsp (value, row, index) {
    return [
        '<input type="button" class="ibtnDel_lsp btn btn-sm btn-danger "  value="Delete">'
    ].join('');
}

function TableActions_demands (value, row, index) {
    return [
        '<input type="button" class="ibtnDel_demands btn btn-sm btn-danger "  value="Delete">'
    ].join('');
}

//reset only demands
function reset_demand_only() {
    console.log('reset_demand_only')
    $('#table').bootstrapTable('resetSearch', '');

    //var jsonTable = new JSONTable($("#table"))
    //var new_data= jsonTable.toJSON()

    var table = $('#table')
    table_data = table.bootstrapTable('getData',false);
    new_data = JSON.parse(JSON.stringify(table_data))
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
