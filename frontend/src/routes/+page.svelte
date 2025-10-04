<script>
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let text = "loading...";
  let watchlist = [];
  let selected = "";

  function addCoin() {
        const symbol = prompt("Enter coin id (e.g. bitcoin, eth, solana):");
    if (!symbol) return;
     fetch(`${API_BASE}/watchlist/${symbol}`, { method: "POST" });
     loadWatchlist();
  }

   async function loadWatchlist() {
    try {
      const resp = await fetch(`${API_BASE}/watchlist`);
      const data = await resp.json();
      watchlist = data;
      if (watchlist.length > 0) {
        selected = watchlist[0];   // always set to first string
      }
    } catch (err) {
      error = String(err);
      console.error("Error fetching watchlist:", err);
    }
  }


  function removeCoin() {
      if (!selected) return;
      fetch(`${API_BASE}/watchlist/${selected}`, { method: "DELETE" });
      loadWatchlist();
  }

  onMount(async () => {
    try {
      const resp = await fetch("http://127.0.0.1:8000/watchlist");
      text = await resp.text();
      console.log("RAW RESPONSE:", text);
    } catch (err) {
      text = "error: " + err;
      console.error("FETCH FAILED:", err);
    }
  });
</script>

<h1>Debug Watchlist</h1>
<pre>{text}</pre>

<h1>Crypto Dashboard</h1>

<h2>Watchlist:</h2>
{#if watchlist.length === 0}
  <p>No coins yet</p>
{:else}
  <select bind:value={selected}>
    {#each watchlist as coin}
      <option value={coin}>{coin.toUpperCase()}</option>
    {/each}
  </select>
{/if}

<div style="margin-top: 8px;">
  <button on:click={addCoin}>Add Coin</button>
  <button on:click={removeCoin} disabled={!selected}>Remove</button>
</div>

{#if selected}
  <PriceChart symbol={selected} />
{/if}
