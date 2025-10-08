<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";
  import { authFetch } from "$lib/authFetch";
  const dispatch = createEventDispatcher();

  let watchlist: any[] = [];
  let topCoins: any[] = [];
  let newCoin = "";
  let selected: string | null = null;

  const API_BASE = "http://127.0.0.1:8000";

  async function addCoinToWatchlist() {
    if (!newCoin) return;
    const resp = await authFetch(`/watchlist/${newCoin}`, { method: "POST" });
    const data = await resp.json();

    if (resp.ok) {
      if (data.detail.includes("already")) {
        console.log(data.detail); // or show a message in the UI
      } else {
        console.log(data.detail); // "BITCOIN added"
      }
      newCoin = "";
      await loadWatchlist();   // always refresh UI
    } else {
      console.error("Add failed:", data);
    }
  }

  async function loadTopCoins() {
    const resp = await fetch(`${API_BASE}/coins/top50`);
    if (resp.ok) topCoins = await resp.json();
  }

  async function loadWatchlist() {
    const resp = await authFetch(`/watchlist`);
    if (resp.ok) {
      watchlist = await resp.json();
      console.log("Updated watchlist:", watchlist);  // ⬅ check after remove
      if (watchlist.length > 0 && !selected) {
        selected = watchlist[0].coingecko_id;
        dispatch("coinSelected", selected);
      }
      await updateWatchlistWithPrices();
    }
  }

  async function updateWatchlistWithPrices() {
    if (!watchlist.length) return;
    const ids = watchlist.map(c => c.coingecko_id).join(",");
    const resp = await fetch(`${API_BASE}/coins/current?symbols=${ids}`);
    if (resp.ok) {
      const data = await resp.json();
      watchlist = watchlist.map(c => ({
        ...c,
        price: data[c.coingecko_id]?.usd || null
      }));
    }
  }

  async function removeCoinFromWatchlist() {
    if (!selected) return;
    const resp = await authFetch(`/watchlist/${selected}`, { method: "DELETE" });  // ✅ resp is defined
    if (resp.ok) {
      console.log(`${selected} removed`);
      selected = null;
      await loadWatchlist();   // refreshes UI
    } else {
      console.error("Remove failed:", await resp.text());
    }
  }

  onMount(() => {
    loadTopCoins();
    loadWatchlist();
  });
</script>

<div>
  <select bind:value={newCoin}>
    <option value="">-- Select coin --</option>
    {#each topCoins as c}
      <option value={c.id}>{c.symbol.toUpperCase()} - {c.name}</option>
    {/each}
  </select>
  <button on:click={addCoinToWatchlist}>Add Coin</button>
  <button on:click={removeCoinFromWatchlist} disabled={!selected}>Remove</button>
</div>

<div style="margin-top:1rem;">
  {#each watchlist as coin}
    <button
      class:selected={coin.coingecko_id === selected}
      on:click={() => {
        selected = coin.coingecko_id;
        dispatch("coinSelected", selected);
      }}
    >
      {coin.coingecko_id.toUpperCase()}
      {#if coin.price} ${coin.price.toLocaleString()}{/if}
    </button>
  {/each}
</div>

<!-- <pre>{JSON.stringify(watchlist, null, 2)}</pre> -->
