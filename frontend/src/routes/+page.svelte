<script>
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let watchlist = [];
  let selected = "";
  const API_BASE = "http://127.0.0.1:8000";
  const USER_ID = 1;   // hardcoded for now

  async function loadWatchlist() {
    try {
      const resp = await fetch(`${API_BASE}/watchlist/${USER_ID}`);
      const data = await resp.json();
      watchlist = data;
      if (watchlist.length > 0) {
        selected = watchlist[0];
      }
    } catch (err) {
      console.error("Error fetching watchlist:", err);
    }
  }

  async function addCoin() {
    const symbol = prompt("Enter coin id (e.g. bitcoin, eth, solana):");
    if (!symbol) return;
    await fetch(`${API_BASE}/watchlist/${USER_ID}/${symbol}`, { method: "POST" });
    await loadWatchlist();
  }

  async function removeCoin() {
    if (!selected) return;
    await fetch(`${API_BASE}/watchlist/${USER_ID}/${selected}`, { method: "DELETE" });
    await loadWatchlist();
  }

  onMount(loadWatchlist);
</script>

<h1>Crypto Dashboard</h1>

<h2>Watchlist</h2>
{#if watchlist.length === 0}
  <p>No coins yet</p>
{:else}
  <select bind:value={selected}>
    {#each watchlist as coin}
      <option value={coin}>{coin.toUpperCase()}</option>
    {/each}
  </select>
{/if}

<div style="margin-top:8px">
  <button on:click={addCoin}>Add Coin</button>
  <button on:click={removeCoin} disabled={!selected}>Remove</button>
</div>

{#if selected}
  <PriceChart symbol={selected}/>
{/if}
