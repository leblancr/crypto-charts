<script lang="ts">
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let errorMessage: string | null = null;
  let prices: Record<string, number> = {};
  let watchlist: string[] = [];
  let selected = "";
  const API_BASE = "http://127.0.0.1:8000";
  const USER_ID = 1;

  async function loadPrices() {
    console.log("loadPrices called");
    if (!watchlist.length) return;
    try {
      const resp = await fetch(`${API_BASE}/coins/current?symbols=${watchlist.join(",")}`);
      if (!resp.ok) {
        if (resp.status === 429) {
          errorMessage = "Too many requests to the price API. Please wait a minute and try again.";
        } else {
          errorMessage = `Error fetching prices: ${resp.statusText}`;
        }
        return;
      }

      const data = await resp.json();
      console.log("data from backend:", data);  // 👈 add this
      prices = {};
      // data looks like: {"bitcoin":{"usd":27400}, "ethereum":{"usd":1600}}
      for (const [symbol, value] of Object.entries(data)) {
        prices[symbol] = (value as any).usd;
      }
      errorMessage = null; // clear error when successful
      console.log("prices object:", prices);  // 👈 add this
    } catch (err) {
      errorMessage = "Network error fetching prices.";
      console.error("Error fetching prices:", err);
    }
  }

  async function loadWatchlist() {
    try {
      const resp = await fetch(`${API_BASE}/watchlist/${USER_ID}`);
      watchlist = await resp.json();
      if (watchlist.length > 0 && !selected) {
        selected = watchlist[0];
      }
      await loadPrices();   // <-- fetch prices after watchlist
    } catch (err) {
      console.error("Error fetching watchlist:", err);
    }
    await loadPrices();
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

<h1 style="text-align: center;">Crypto Dashboard</h1>

{#if errorMessage}
  <div style="margin:1rem; padding:0.5rem; background:#fee; color:#900; border:1px solid #c00; border-radius:6px;">
    {errorMessage}
  </div>
{/if}

<div style="margin-top:8px">
  <button on:click={addCoin}>Add Coin</button>
  <button on:click={removeCoin} disabled={!selected}>Remove</button>
</div>

<!-- Chart -->
{#if selected}
  <PriceChart symbol={selected}/>
{/if}
