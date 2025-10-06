<script lang="ts">
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let errorMessage: string | null = null;
  let prices: Record<string, number> = {};
  let watchlist: string[] = [];
  let selected: string | null = null;
  let topCoins = [];
  let newCoin = "";

  const API_BASE = "http://127.0.0.1:8000";
  const USER_ID = 1;

  async function addCoinToWatchlist() {
    if (!newCoin) return;
    await fetch(`${API_BASE}/watchlist/1/${newCoin}`, { method: "POST" });
    newCoin = ""; // reset the dropdown after adding
    await loadWatchlist();
  }

  async function loadTopCoins() {
    const resp = await fetch(`${API_BASE}/coins/top50`);
    if (resp.ok) {
      topCoins = await resp.json();
    }
  }

  async function loadWatchlist() {
    try {
      const resp = await fetch(`${API_BASE}/watchlist/${USER_ID}`);
      watchlist = await resp.json();
      if (watchlist.length > 0 && !selected) {
        selected = watchlist[0].id;
      }
      await updateWatchlistWithPrices();   // <-- fetch prices after watchlist
    } catch (err) {
      console.error("Error fetching watchlist:", err);
    }
    await updateWatchlistWithPrices();
  }

  async function removeCoinFromWatchlist() {
    if (!selected) return;
    await fetch(`${API_BASE}/watchlist/1/${selected}`, { method: "DELETE" });
    selected = null;
    await loadWatchlist();
  }

  async function updateWatchlistWithPrices() {
    if (!watchlist.length) return;

    const ids = watchlist.map(c => c.id).join(",");
    const resp = await fetch(`${API_BASE}/coins/current?symbols=${ids}`);
    if (!resp.ok) {
      console.error("Failed to fetch prices:", await resp.text());
      return;
    }

    const data = await resp.json();

    // Merge prices into watchlist
    watchlist = watchlist.map(c => ({
      ...c,
      price: data[c.id]?.usd || null
    }));
  }

  // ✅ run when the page loads
  onMount(() => {
    loadTopCoins();
    loadWatchlist();
  });

</script>

<h1 style="text-align: center; color: blue;">Crypto Dashboard</h1>

<div style="margin-top:8px">
  <select bind:value={newCoin}>
    <option value="">-- Select coin --</option>
    {#each topCoins as c}
      <option value={c.id}>{c.symbol.toUpperCase()} - {c.name}</option>
    {/each}
  </select>
  <button on:click={addCoinToWatchlist}>Add Coin</button>
  <button on:click={removeCoinFromWatchlist} disabled={!selected}>Remove</button>
</div>

<style>
  /* Base select box */
  select {
    background: #111;   /* dark background */
    color: #eee;        /* light text */
    border: 1px solid #444;
    padding: 4px;
    border-radius: 4px;
  }

  /* Options inside dropdown */
  option {
    background: #111;
    color: #eee;
  }

  /* WebKit (Chrome/Edge/Safari) scrollbar */
  select::-webkit-scrollbar {
    width: 10px;
  }
  select::-webkit-scrollbar-track {
    background: #222;
  }
  select::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 6px;
    border: 2px solid #222;
  }

  /* Firefox scrollbar */
  select {
    scrollbar-width: thin;
    scrollbar-color: #555 #222;
  }
</style>

{#if errorMessage}
  <div style="margin:1rem; padding:0.5rem; background:#fee; color:#900; border:1px solid #c00; border-radius:6px;">
    {errorMessage}
  </div>
{/if}

<!-- Watchlist buttons -->
<div style="margin-top:1rem;">
  {#each watchlist as coin}
    <button
      class:selected={coin.id === selected}
      on:click={() => (selected = coin.id)}
      style="margin-right:0.5rem;"
    >
      {coin.ticker.toUpperCase()}
      {#if coin.price} ${coin.price.toLocaleString()}{/if}
    </button>
  {/each}
</div>


<!-- Chart -->
{#if selected}
  <PriceChart symbol={selected}/>
{/if}
