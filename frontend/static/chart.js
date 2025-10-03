const ctx = document.getElementById("priceChart").getContext("2d");
const PRICE_FETCH_INTERVAL = 60000; // 60 seconds

let latestSymbol = null; // guards against out-of-order responses
let priceChart = null; // we create it after data is fetched
let lastPriceFetch = 0;

// Cache last successful series so the chart can stay visible during 429s
const lastSeriesBySymbol = new Map();

function clearStatus() {
  const el = document.getElementById("status");
  if (el) el.textContent = "";
}

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

async function loadTop50() {
  try {
    const resp = await fetch("/coins/top50"); // must exist in your backend
    const coins = await resp.json();

    const container = document.getElementById("topCoins");
    container.innerHTML = "<h3>Top 50 Coins</h3>";

    coins.forEach(c => {
      const btn = document.createElement("button");
      btn.textContent = `${c.symbol.toUpperCase()} (${c.name})`;
      btn.style.margin = "4px";
      btn.addEventListener("click", async () => {
        await fetch(`/watchlist/${c.id}`, { method: "POST" });
        await populateDropdown();
      });
      container.appendChild(btn);
    });
  } catch (err) {
    console.error("Error loading top coins:", err);
  }
}

// Show why we're using cached data (e.g., "429 Too Many Requests")
function showStaleStatus(symbol, note) {
  const el = document.getElementById("status");
  if (!el) return;
  const base = `Showing cached ${symbol.toUpperCase()} data`;
  el.textContent = note ? `${base} (${note}).` : `${base} (rate limited).`;
}

async function updateLivePrice(symbol) {
  const now = Date.now();
  if (now - lastPriceFetch < PRICE_FETCH_INTERVAL) {
    return; // 🔹 skip if we fetched too recently
  }
  lastPriceFetch = now;

  const reqFor = symbol;                   // capture intent
  try {
    const resp = await fetch(`/coins/${symbol}/price`);
    if (reqFor !== latestSymbol) return;   // drop late/out-of-order responses

    if (!resp.ok) {
      let note;
      try {
        const err = await resp.json();
        note = err?.detail || `${resp.status} ${resp.statusText}`;
      } catch {
        note = `${resp.status} ${resp.statusText}`;
      }
      showStaleStatus(symbol, note);
      return;
    }

    const data = await resp.json();
    // Prefer the requested key; if backend keyed by another id, use first key as fallback
    const key = symbol.toLowerCase();
    const coin = data[key] ?? data[Object.keys(data || {})[0]];

    if (!coin || typeof coin.usd !== "number") {
      showStaleStatus(symbol, "price payload missing");
      return;
    }

    // Only update if still the latest selection
    if (reqFor !== latestSymbol) return;
    document.getElementById("livePrice").textContent =
      `${symbol.toUpperCase()}: $${coin.usd.toLocaleString()} (${(coin.usd_24h_change ?? 0).toFixed(2)}%)`;
    clearStatus();
  } catch (err) {
    console.error("Error fetching live price:", err);
  }
}

async function updateChart(symbol = "bitcoin", days = 30) {
    try {
        const response = await fetch(`/coins/${symbol}/history?days=${days}`);

        if (!response.ok) {
          let note;
          try {
            const err = await response.json();          // FastAPI usually: { detail: "..." }
            note = err?.detail || `${response.status} ${response.statusText}`;
          } catch {
            note = `${response.status} ${response.statusText}`;
          }

          const cached = lastSeriesBySymbol.get(symbol);
          if (cached && priceChart) {
            showStaleStatus(symbol, note);              // keep previous line
            priceChart.update();
            return;
          }

             // Try persistent cache on first load / no memory cache
            const saved = localStorage.getItem(`series:${symbol}`);
            if (saved) {
              const formatted = JSON.parse(saved);
              showStaleStatus(symbol, note ? `${note}; restored cached data` : "restored cached data");

              if (!priceChart) {
                // create the chart from persisted data
                priceChart = new Chart(ctx, {
                  type: "line",
                  data: {
                    labels: formatted.labels,
                    datasets: [{
                      label: symbol.toUpperCase() + " / USD",
                      data: formatted.values,
                      borderColor: "rgba(43, 245, 39, 0.75)",
                      backgroundColor: "rgba(54, 162, 235, 0.1)",
                      borderWidth: 2,
                      fill: true,
                      pointRadius: 0,
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
              } else {
                // update current chart from persisted data
                priceChart.data.labels = formatted.labels;
                priceChart.data.datasets[0].data = formatted.values;
                priceChart.data.datasets[0].label = symbol.toUpperCase() + " / USD";
                priceChart.update();
              }
              return;
            }

          // No cache for this symbol; show error status and leave whatever is on screen
          showStaleStatus(symbol, note);
          return;
        }

        const data = await response.json();
        const formatted = formatData(data);

        // Handle "200 OK" with empty/invalid payload: keep previous line and show note
        if (!Array.isArray(data) || formatted.labels.length === 0 || formatted.values.length === 0) {
          const cached = lastSeriesBySymbol.get(symbol) || JSON.parse(localStorage.getItem(`series:${symbol}`) || "null");
          if (cached && priceChart) {
            showStaleStatus(symbol, "empty history payload");
            priceChart.update();
            return;
          }
          showStaleStatus(symbol, "empty history payload");
          return;
        }

        // We have good data — only proceed if still the latest selection
        if (symbol !== latestSymbol) return;

        clearStatus();                 // we have fresh data again
        lastSeriesBySymbol.set(symbol, formatted);
        localStorage.setItem(`series:${symbol}`, JSON.stringify(formatted));

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
      latestSymbol = coins[0];
      await updateChart(coins[0]);       // coins is a list of strings now
      await updateLivePrice(coins[0]);   // keep header in sync
    }
  } catch (err) {
    console.error("Error populating dropdown:", err);
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
  latestSymbol = symbol;
  updateChart(symbol);
  updateLivePrice(symbol);
});

// initial load
populateDropdown().then(() => {
  const select = document.getElementById("symbol");
  if (select.value) {
    latestSymbol = symbol;
    updateLivePrice(select.value);
  }
});

// load top 50 buttons
loadTop50();
