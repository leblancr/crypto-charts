<script>
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let watchlist = [];
  let selected = "";   // ✅ start as empty string not null
  let error = "";

  const API_BASE = "http://127.0.0.1:8000";

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

  onMount(loadWatchlist);
</script>

<h1>Crypto Dashboard</h1>

<h2>Watchlist:</h2>
<select bind:value={selected}>
  {#each watchlist as coin}
    <option value={coin}>{coin.toUpperCase()}</option>
  {/each}
</select>

{#if selected}
  <PriceChart symbol={selected} />
{/if}
