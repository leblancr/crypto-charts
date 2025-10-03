const ctx = document.getElementById("priceChart").getContext("2d");
let priceChart = null; // we create it after data is fetched

function formatData(data) {
    if (!Array.isArray(data)) {
        console.error("Unexpected data format:", data);
        return { labels: [], values: [] };
    }
    return {
        labels: data.map(d => new Date(d.timestamp).toLocaleString()),
        values: data.map(d => d.price)
    };
}

async function updateChart(symbol = "bitcoin", days = 30) {
    try {
        const response = await fetch(`/coins/${symbol}/history?days=${days}`);
        const data = await response.json();
        const formatted = formatData(data);

        if (!priceChart) {
            // create chart first time with your style
            priceChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: formatted.labels,
                    datasets: [{
                        label: symbol.toUpperCase() + " / USD",
                        data: formatted.values,
                        borderColor: "rgba(43, 245, 39, 0.75)",     // line color
                        backgroundColor: "rgba(54, 162, 235, 0.1)", // fill color
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,   // no dots
                        tension: 0.2      // smooth curve
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
        } else {
            // update chart with new data AND styling each time
            priceChart.data.labels = formatted.labels;
            priceChart.data.datasets[0] = {
                label: symbol.toUpperCase() + " / USD",
                data: formatted.values,
                borderColor: "rgba(43, 245, 39, 0.75)",
                backgroundColor: "rgba(54, 162, 235, 0.1)",
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.2
            };
            priceChart.update();
        }
    } catch (err) {
        console.error("Error updating chart:", err);
    }
}

// dropdown handler
document.getElementById("symbol").addEventListener("change", e => updateChart(e.target.value));

// initial load
updateChart();
