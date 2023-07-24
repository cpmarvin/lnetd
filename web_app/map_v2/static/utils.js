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
            cols += '<td>' + Math.floor(Math.random() * 100) + '</td>'; //r_int
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
            cols_rev += '<td>' + Math.floor(Math.random() * 100) + '</td>'; //r_int
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
    var jsonTable = new JSONTable($("#table"))
    var new_data= jsonTable.toJSON()
    new_data.forEach( function (d) { 
        d.util =0 })
    $('#table').bootstrapTable("load", new_data);
}


function graph_aggr(data,capacity,graph_id,source_cc,target_cc) {
    var rawDataURL = data
    //pop last interval from array , it's mostly 0 in not exactly on the hours due to aggregataion
    rawDataURL.pop()
    //lame , promise issues
    div_id = data[0]['div_id']+'div_id'
    //console.log('this is the div_id inside graph_aggr',div_id)
    $( "#"+div_id ).empty();
    title = data[0]['name'] + 'Capaci'
    // / create selector
    var selectorOptions = {
        visible: true,
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
            label: 'all'
        }],
    };
    // //prepare the graph
    var data = [ prepData(data), prepDataIn(data), prepDataCir(data), prepDataCirIn(data), prepDataCapacity(data), prepDataCapacityIn(data) ];
    var layout = {
        showlegend: true,
        legend: {
           y: 0.5,
           font: {
            size: 12
           }
        },
        autoresize: true,
        width: document.getElementById(div_id).clientWidth,
        height: 380,
        margin: {
         l: 50,
         r: 0,
         b: 40,
         t: 0,
         pad: 0,
        },
        title1: title,
        xaxis: {
            fixedrange: true,
            rangeselector: selectorOptions,
            rangeslider: {},
            type: 'date',
            title: 'Time',
        },
        yaxis: {
            fixedrange: false,
            autotick: true,
            autorange: true,
            tickformat: ".3s",
            title: 'bps'
        }
    };

    Plotly.newPlot(div_id, data, layout, {scrollZoom: true} );
    // //prepare the data
    function prepData(rawData) {
        //map the fields
        var xField = 'time';
        var yField = 'bps_out';
        var x = [];
        var y = [];
        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            fill: 'tonexty',
            fillcolor: '#99CCFF',
            line: {width: 1, shape: 'spline', color: '#99CCFF'},
            name: 'OUT',
            x: x,
            y: y
        }; }
     //prepare the data trace2 bps_in
    function prepDataIn(rawData) {
        //map the fields
        var xField = 'time';
        var yField = 'bps_in';
        var x = [];
        var y = [];
        //pop last interval as it's going to be 0 if not exactly on the outer
        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(-datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            fill: 'tozeroy',
            fillcolor: '#57b88f',
            line: {width: 1, shape: 'spline', color: '#57b88f'},
            name: 'IN',
            x: x,
            y: y
        }; }

    // //prepare the data
    function prepDataCir(rawData) {
        //map the fields
        var xField = 'time';
        var yField = 'cir';
        var x = [];
        var y = [];
        //pop last interval as it's going to be 0 if not exactly on the outer
        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return {
            type: 'lines',
            connectgaps: 'false',
            line: {width: 2, dash: 'dot', color: 'rgb(219, 64, 82)'},
            name: 'Cir-OUT',
	    showlegend: true,
            visible: "legendonly",
            x: x,
            y: y
        }; }

    // //prepare the data
    function prepDataCirIn(rawData) {
        //map the fields
        var xField = 'time';
        var yField = 'cir';
        var x = [];
        var y = [];
        //pop last interval as it's going to be 0 if not exactly on the outer
        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(-datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            line: {width: 2, dash: 'dot', color: 'rgb(219, 64, 82)'},
            name: 'Cir-IN',
	    showlegend: true,
            visible: "legendonly",
            x: x,
            y: y
        }; }

//capacity IN
    function prepDataCapacity(rawData) {
        //map the fields
        var xField = 'time';
        var yField = 'capacity';
        var x = [];
        var y = [];
        //pop last interval as it's going to be 0 if not exactly on the outer
        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            line: {width: 2, dash: 'dot', color: 'rgb(219, 64, 82)'},
            name: 'Cap-OUT',
            showlegend: true,
            visible: "legendonly",
            x: x,
            y: y
        }; }

//capacity IN
    function prepDataCapacityIn(rawData) {
        //map the fields
        var xField = 'time';
        var yField = 'capacity';
        var x = [];
        var y = [];
        //pop last interval as it's going to be 0 if not exactly on the outer
        rawData.forEach(function(datum, i) {

            x.push(new Date(datum[xField]));
            y.push(-datum[yField]); });

        return {
            mode: 'lines',
            connectgaps: 'false',
            line: {width: 2, dash: 'dot', color: 'rgb(219, 64, 82)'},
            name: 'Cap-IN',
            showlegend: true,
	    visible: "legendonly",
            x: x,
            y: y
        }; }

}
