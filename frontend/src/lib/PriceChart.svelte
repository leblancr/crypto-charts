<script>
  import { onMount, onDestroy } from "svelte";
  import Chart from "chart.js/auto";

  const API_BASE = "http://127.0.0.1:8000";

  let watchlist = [];        // coins from backend
  let prices = {};           // { coinOrId: price }
  let selected = null;       // selected coin
  let days = "30";           // bound to <select>
  let canvas;
  let chart;

  // Map tickers to CoinGecko IDs
  const ID_MAP = {
    ada: "cardano",
    eth: "ethereum",
    btc: "bitcoin",
    bitcoin: "bitcoin",
    cardano: "cardano",
    ethereum: "ethereum"
  };

  // --- helpers to reduce 429s ---
  let priceInterval = null;   // single timer for price polling
  let loadingPrices = false;  // prevent overlapping requests
  let loadingHistory = false;

  function priceForButton(coin) {
    const id = ID_MAP[coin?.toLowerCase()] || coin?.toLowerCase();
    return prices[coin] ?? prices[id] ?? null;
  }

  // Load watchlist from backend (/watchlist/1)
  async function loadWatchlist() {
    const resp = await fetch(`${API_BASE}/watchlist/1`);
    if (!resp.ok) {
      console.error("Failed to load watchlist:", await resp.text());
      return;
    }
    const data = await resp.json();
    watchlist = Array.isArray(data) ? data : (data.coins || []);
    if (watchlist.length && !selected) {
      selected = watchlist[0];
      await loadChart(selected);
    }
  }

  // Load current prices (polled once per minute)
  async function loadPrices() {
    if (!watchlist.length || loadingPrices) return;
    loadingPrices = true;
    try {
      const symbols = watchlist.join(",");
      const resp = await fetch(`${API_BASE}/coins/current?symbols=${symbols}`);
      if (!resp.ok) {
        if (resp.status === 429) {
          console.warn("429 from /coins/current — skipping this cycle");
          return;
        }
        console.error("Prices error:", resp.status, await resp.text());
        return;
      }
      const data = await resp.json();
      prices = {};
      for (const [k, v] of Object.entries(data)) {
        prices[k] = v.usd;
      }
    } catch (e) {
      console.error("Network error fetching prices:", e);
    } finally {
      loadingPrices = false;
    }
  }

  // Load history + draw chart
  async function loadChart(symbol) {
    if (!symbol || loadingHistory) return;
    loadingHistory = true;
    try {
      const id = ID_MAP[symbol?.toLowerCase()] || symbol?.toLowerCase();
      const resp = await fetch(`${API_BASE}/coins/${id}/history?days=${days}`);
      if (!resp.ok) {
        if (resp.status === 429) {
          console.warn("429 from /coins/{id}/history — skipping");
          return;
        }
        console.error("Failed to load history:", resp.status, await resp.text());
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
              label: (ID_MAP[symbol?.toLowerCase()] || symbol).toUpperCase() + " / USD",
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
    } catch (e) {
      console.error("Network error loading history:", e);
    } finally {
      loadingHistory = false;
    }
  }

  // User selects a coin
  function selectCoin(coin) {
    selected = coin;
    loadChart(selected);   // one fetch per click
  }

  // on change of days
  function changeDays(e) {
    days = e.target.value;
    if (selected) loadChart(selected);
  }

  // ⬇️ this replaces the old reactive $: block
  onMount(() => {
    loadWatchlist();
    loadPrices();
    priceInterval = setInterval(loadPrices, 60000); // poll once per minute
  });

  onDestroy(() => {
    if (priceInterval) clearInterval(priceInterval);
  });
</script>

<!-- ✅ Watchlist buttons -->
<div style="margin-top:1rem;">
  {#each watchlist as coin}
    <button
      class:selected={coin === selected}
      on:click={() => selectCoin(coin)}
    >
      {coin.toUpperCase()} {#if priceForButton(coin)}${priceForButton(coin).toLocaleString()}{/if}
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
