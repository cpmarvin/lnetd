
function generate_pie(div_id,data_values,data_labels) {

    var pieData = {
      datasets: [{
        data: data_values,
        backgroundColor: Chart['colorschemes'].tableau.Tableau10,
        borderColor: Chart['colorschemes'].tableau.Tableau10,
      }],
      labels: data_labels
    };

    var pieOptions = {
      responsive: true,
      cutoutPercentage: 70,
      legend: {
          display: true,
          position: "bottom",
          align: "left",
      },
      animation: {
          animateScale: true,
          animateRotate: true
      },
      plugins: {
        datalabels: {
           display: false,
           align: 'center',
           anchor: 'center'
        },
       colorschemes: {
          scheme: 'brewer.Paired12'
       },
      }
    };
    if ($("#"+div_id).length) {
      var pieChartCanvas = $("#"+div_id).get(0).getContext("2d");
      var pieChart = new Chart(pieChartCanvas, {
        type: 'pie',
        data: pieData,
        options: pieOptions
      });
    }
}


