<script>
  import { onMount } from "svelte";
  import Chart from "chart.js/auto";

  const API_BASE = "http://127.0.0.1:8000";

  let watchlist = [];        // [{ticker, id}, …] from backend
  let prices = {};           // { id: price }
  let selected = null;       // selected coin (id)
  let days = "30";           // chart range
  let canvas;
  let chart;

  // Load watchlist from backend
  async function loadWatchlist() {
    const resp = await fetch(`${API_BASE}/watchlist/1`);
    if (!resp.ok) {
      console.error("Failed to load watchlist:", await resp.text());
      return;
    }
    watchlist = await resp.json();
    console.log("Watchlist from backend:", watchlist);

    // Select first coin if none selected
    if (watchlist.length && !selected) {
      selected = watchlist[0].id;
      await loadChart(selected);
    }

    await loadPrices();
  }

  // Load current prices
  async function loadPrices() {
    if (!watchlist.length) return;

    // ✅ use CoinGecko IDs
    const ids = watchlist.map(c => c.id).join(",");
    const resp = await fetch(`${API_BASE}/coins/current?symbols=${ids}`);
    if (!resp.ok) {
      console.error("Failed to fetch prices:", await resp.text());
      return;
    }
    const data = await resp.json();

    prices = {};
    for (const [id, val] of Object.entries(data)) {
      prices[id] = val.usd;
    }
    console.log("Prices object:", prices);
  }

  // Load history + draw chart
  async function loadChart(id) {
    const resp = await fetch(`${API_BASE}/coins/${id}/history?days=${days}`);
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
            label: id.toUpperCase(),
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

  function selectCoin(id) {
    selected = id;
    loadChart(id);
  }

  function changeDays(event) {
    days = event.target.value;
    if (selected) loadChart(selected);
  }

  onMount(loadWatchlist);
</script>

<!-- Watchlist buttons -->
<div style="margin-top:1rem;">
  {#each watchlist as coin}
    <button
      class:selected={coin.id === selected}
      on:click={() => selectCoin(coin.id)}
      style="margin-right: 0.5rem;"
    >
      {coin.ticker.toUpperCase()}
      {#if prices[coin.id]} ${prices[coin.id].toLocaleString()}{/if}
    </button>
  {/each}
</div>

<!-- Days dropdown -->
<div style="margin-top: 1rem;">
  <label for="days">Range:</label>
  <select id="days" bind:value={days} on:change={changeDays} disabled={!selected}>
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
