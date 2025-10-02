const ctx = document.getElementById('priceChart').getContext('2d');
let chart = null;

async function fetchHistory(symbol, days=30) {
  const resp = await fetch(`http://127.0.0.1:8000/coins/${symbol}/history?days=${days}`);
  return await resp.json();
}

function formatData(data) {
  const labels = data.map(item => new Date(item.timestamp).toLocaleDateString());
  const prices = data.map(item => item.price);
  return { labels, prices };
}

async function updateChart(symbol) {
  const data = await fetchHistory(symbol);
  const { labels, prices } = formatData(data);

  if (chart) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = prices;
    chart.update();
  } else {
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: symbol.toUpperCase() + ' / USD',
          data: prices,
          borderColor: 'rgba(43, 245, 39, .75)', // soft blue with 70% opacity
          backgroundColor: 'rgba(54, 162, 235, 0.1)', // optional, for fill
          borderWidth: 2,
          fill: true,
          pointRadius: 0, // hides all points
          tension: 0.2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: 'Date' } },
          y: { title: { display: true, text: 'Price (USD)' }, beginAtZero: false }
        },
        plugins: {
          legend: { display: true, position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        }
      }
    });
  }
}

// Initial chart
updateChart('bitcoin');

// Change coin dynamically
document.getElementById('symbol').addEventListener('change', e => {
  updateChart(e.target.value);
});
