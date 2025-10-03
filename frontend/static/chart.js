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

async function populateDropdown() {
  try {
    const response = await fetch("/watchlist");
    const coins = await response.json();

    const select = document.getElementById("symbol");
    select.innerHTML = ""; // clear existing options

    coins.forEach(coin => {
      const option = document.createElement("option");
      option.value = coin;
      option.textContent = coin.toUpperCase();
      select.appendChild(option);
    });

    // auto-update chart for the first coin in list
    if (coins.length > 0) {
      select.value = coins[0];
      updateChart(coins[0].coin);
    }
  } catch (err) {
    console.error("Error populating dropdown:", err);
  }
}

async function updateLivePrice(symbol) {
  try {
    const resp = await fetch(`/coins/${symbol}/price`);
    const data = await resp.json();
    const coin = data[symbol];   // <-- dynamic key here
    if (coin) {
      document.getElementById("livePrice").textContent =
        `${symbol.toUpperCase()}: $${coin.usd.toLocaleString()} (${coin.usd_24h_change.toFixed(2)}%)`;
    } else {
      document.getElementById("livePrice").textContent = "No price data available";
    }
  } catch (err) {
    console.error("Error fetching live price:", err);
  }
}

// Event listeners for buttons
document.getElementById('addCoin').addEventListener('click', async () => {
  const symbol = prompt("Enter coin to add:");
  if (!symbol) return;
  await fetch(`/watchlist/${symbol}`, { method: 'POST' });
  await populateDropdown();
});

document.getElementById('removeCoin').addEventListener('click', async () => {
  const symbol = document.getElementById('symbol').value;
  await fetch(`/watchlist/${symbol}`, { method: 'DELETE' });
  await populateDropdown();
});

// dropdown handler
document.getElementById("symbol").addEventListener("change", e => {
  const symbol = e.target.value;
  updateChart(symbol);
  updateLivePrice(symbol);
});

// initial load
populateDropdown().then(() => {
  const select = document.getElementById("symbol");
  if (select.value) {
    updateLivePrice(select.value);
  }
});
