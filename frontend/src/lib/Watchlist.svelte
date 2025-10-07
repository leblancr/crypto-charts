<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();

  let watchlist: any[] = [];
  let topCoins: any[] = [];
  let newCoin = "";
  let selected: string | null = null;

  const API_BASE = "http://127.0.0.1:8000";
  const USER_ID = 1;

  async function loadTopCoins() {
    const resp = await fetch(`${API_BASE}/coins/top50`);
    if (resp.ok) topCoins = await resp.json();
  }

  async function loadWatchlist() {
    const resp = await fetch(`${API_BASE}/watchlist/${USER_ID}`);
    if (resp.ok) {
      watchlist = await resp.json();
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
        price: data[c.id]?.usd || null
      }));
    }
  }

  async function addCoinToWatchlist() {
    if (!newCoin) return;
    await fetch(`${API_BASE}/watchlist/${USER_ID}/${newCoin}`, { method: "POST" });
    newCoin = "";
    await loadWatchlist();
  }

  async function removeCoinFromWatchlist() {
    if (!selected) return;
    await fetch(`${API_BASE}/watchlist/${USER_ID}/${selected}`, { method: "DELETE" });
    selected = null;
    await loadWatchlist();
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
