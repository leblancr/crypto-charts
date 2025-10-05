<script>
  import { onMount } from "svelte";
  import Chart from "chart.js/auto";

  const API_BASE = "http://127.0.0.1:8000";

  let watchlist = [];        // coins from backend
  let prices = {};           // { coin: price }
  let selected = null;       // selected coin
  let days = "30";           // bound to <select>
  let canvas;
  let chart;

  // Load watchlist from backend (/watchlist/1)
  async function loadWatchlist() {
    const resp = await fetch(`${API_BASE}/watchlist/1`);
    if (!resp.ok) {
      console.error("Failed to load watchlist:", await resp.text());
      return;
    }
    const data = await resp.json();
    // adjust to your backend’s actual shape
    watchlist = Array.isArray(data) ? data : (data.coins || []);
    if (watchlist.length && !selected) {
      selected = watchlist[0];
      await loadChart(selected);
    }
    await loadPrices();
  }

  // Load current prices
  async function loadPrices() {
    if (!watchlist.length) return;
    const symbols = watchlist.join(",");
    const resp = await fetch(`${API_BASE}/coins/current?symbols=${symbols}`);
    if (!resp.ok) return;
    const data = await resp.json();
    prices = {};
    data.forEach(item => {
      prices[item.symbol] = item.usd;
    });
  }

  // Load history + draw chart
  async function loadChart(symbol) {
    selected = symbol;
    const resp = await fetch(`${API_BASE}/coins/${symbol}/history?days=${days}`);
    if (!resp.ok) {
      console.error("Failed to load history:", await resp.text());
      return;
    }
    const data = await resp.json();

    const labels = data.map(d => new Date(d.timestamp).toLocaleString());
    const values = data.map(d => d.price);

    if (chart) chart.destroy();

    chart = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: symbol.toUpperCase() + " / USD",
            data: values,
            borderColor: "rgba(43, 245, 39, 0.75)",
            backgroundColor: "rgba(54, 162, 235, 0.1)",
            borderWidth: 2,
            fill: true,
            pointRadius: 0,
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: "Time" } },
          y: { title: { display: true, text: "Price (USD)" } }
        }
      }
    });
  }

  // Reload chart when days changes
  $: if (selected && days) {
    Promise.resolve().then(() => loadChart(selected));
  }

  onMount(loadWatchlist);
</script>

<h1>My Watchlist</h1>

<!-- Watchlist list -->
<ul>
  {#each watchlist as coin}
    <li on:click={() => loadChart(coin)} style="cursor:pointer;">
      {coin.toUpperCase()} – {prices[coin] ? `$${prices[coin]}` : ""}
    </li>
  {/each}
</ul>

<!-- Days dropdown -->
<div style="margin-top: 1rem;">
  <label for="days">Range:</label>
  <select id="days" bind:value={days} disabled={!selected}>
    <option value="1">1 day (minute data)</option>
    <option value="7">7 days (hourly)</option>
    <option value="30">30 days (hourly)</option>
    <option value="90">90 days (hourly)</option>
    <option value="365">365 days (daily)</option>
  </select>
</div>

<!-- Chart -->
{#if selected}
  <div style="height:400px; margin-top:1rem;">
    <canvas bind:this={canvas}></canvas>
  </div>
{:else}
  <div style="margin-top:1rem; color:#666;">Select a coin to view its chart.</div>
{/if}
