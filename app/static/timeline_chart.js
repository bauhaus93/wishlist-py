$.drawChart = function (canvasId, labels, datapoints) {
  var ctx = document.getElementById(canvasId).getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Forderungen",
          data: datapoints,
        },
      ],
    },
    options: {
      legend: { display: false },
      tooltips: {
        callbacks: {
          label: function (tooltipItems, data) {
            return (
              data.datasets[tooltipItems.datasetIndex].label +
              ": " +
              tooltipItems.yLabel +
              " €"
            );
          },
        },
      },
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: false,
            },
          },
        ],
      },
    },
  });
};
