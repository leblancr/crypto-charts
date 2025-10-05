<script lang="ts">
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let watchlist: string[] = [];
  let selected = "";
  const API_BASE = "http://127.0.0.1:8000";
  const USER_ID = 1;

  async function loadWatchlist() {
    try {
      const resp = await fetch(`${API_BASE}/watchlist/${USER_ID}`);
      watchlist = await resp.json();
      if (watchlist.length > 0 && !selected) {
        selected = watchlist[0];
      }
    } catch (err) {
      console.error("Error fetching watchlist:", err);
    }
  }

  async function addCoin() {
    const symbol = prompt("Enter coin id (e.g. bitcoin, ethereum, cardano):");
    if (!symbol) return;
    await fetch(`${API_BASE}/watchlist/${USER_ID}/${symbol}`, { method: "POST" });
    await loadWatchlist();
  }

  async function removeCoin() {
    if (!selected) return;
    await fetch(`${API_BASE}/watchlist/${USER_ID}/${selected}`, { method: "DELETE" });
    selected = "";
    await loadWatchlist();
  }

  onMount(loadWatchlist);
</script>

g<h1>Crypto Dashboard</h1>

<div style="margin-top:8px">
  <button on:click={addCoin}>Add Coin</button>
  <button on:click={removeCoin} disabled={!selected}>Remove</button>
</div>

<!-- Chart -->
{#if selected}
  <PriceChart symbol={selected}/>
{/if}
