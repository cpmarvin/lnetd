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
    var jsonTable = new JSONTable($("#table"))
    var new_data= jsonTable.toJSON()
    new_data.forEach( function (d) { 
        d.util =0 })
    $('#table').bootstrapTable("load", new_data);
}

