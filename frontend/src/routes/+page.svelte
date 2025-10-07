<script lang="ts">
  import { onMount } from "svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let errorMessage: string | null = null;
  let prices: Record<string, number> = {};
  let watchlist: string[] = [];
  let selected: string | null = null;
  let topCoins = [];
  let newCoin = "";

  let showAuthModal = false;
  let isRegister = false; // toggle between login/register
  let username = "";
  let password = "";
  let token: string | null = null;
  let currentUser: string | null = null;

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
        selected = watchlist[0].coingecko_id;   // ✅ use coingecko_id
      }
      await updateWatchlistWithPrices();   // <-- fetch prices after watchlist
    } catch (err) {
      console.error("Error fetching watchlist:", err);
    }
  }

  async function removeCoinFromWatchlist() {
    if (!selected) return;
    await fetch(`${API_BASE}/watchlist/1/${selected}`, { method: "DELETE" });
    selected = null;
    await loadWatchlist();
  }

  async function updateWatchlistWithPrices() {
    if (!watchlist.length) return;

    const ids = watchlist.map(c => c.coingecko_id).join(",");
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

  async function registerUser() {
    const resp = await fetch(`${API_BASE}/users/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (resp.ok) {
      alert("User created, now log in!");
    } else {
      const err = await resp.json();
      errorMessage = "Register failed: " + err.detail;
    }
  }

  async function loginUser() {
    const resp = await fetch(`${API_BASE}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (resp.ok) {
      const data = await resp.json();
      token = data.access_token;
      currentUser = username;
      localStorage.setItem("token", token);
      localStorage.setItem("username", username);
    } else {
      const err = await resp.json();
      errorMessage = "Login failed: " + err.detail;
    }
  }

  async function handleAuth() {
    const endpoint = isRegister ? "signup" : "login";
    const resp = await fetch(`${API_BASE}/users/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (resp.ok) {
      if (isRegister) {
        alert("User created, now log in!");
        isRegister = false;
      } else {
        const data = await resp.json();
        token = data.access_token;
        currentUser = username;
        localStorage.setItem("token", token);
        localStorage.setItem("username", username);
        showAuthModal = false;
      }
    } else {
      const err = await resp.json();
      errorMessage = (isRegister ? "Register" : "Login") + " failed: " + err.detail;
    }
  }

  function logoutUser() {
    token = null;
    currentUser = null;
    localStorage.removeItem("token");
    localStorage.removeItem("username");
  }


  // ✅ run when the page loads
  onMount(() => {
    token = localStorage.getItem("token");
    currentUser = localStorage.getItem("username");

    loadTopCoins();
    loadWatchlist();
  });

</script>
<div style="position: absolute; top: 10px; right: 10px;">
  {#if currentUser}
    <span>Welcome, {currentUser}</span>
    <a href="#" on:click={logoutUser} style="margin-left: 10px;">Logout</a>
  {:else}
    <a href="#" on:click={() => { isRegister = false; showAuthModal = true }}>Login</a>
    <a href="#" on:click={() => { isRegister = true; showAuthModal = true }} style="margin-left: 10px;">Register</a>
  {/if}
</div>

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
      class:selected={coin.coingecko_id === selected}
      on:click={() => (selected = coin.coingecko_id)}
      style="margin-right:0.5rem;"
    >
      {coin.coingecko_id.toUpperCase()}
      {#if coin.price} ${coin.price.toLocaleString()}{/if}
    </button>
  {/each}
</div>

<!-- Chart -->
{#if selected}
  <PriceChart symbol={selected} />
{/if}

{#if showAuthModal}
  <div style="
    position: fixed;
    top:0; left:0; width:100%; height:100%;
    background: rgba(0,0,0,0.5);
    display:flex; align-items:center; justify-content:center;
  ">
    <div style="background:#fff; padding:20px; border-radius:8px; min-width:250px;">
      <h3 style="margin-top:0;">{isRegister ? "Register" : "Login"}</h3>
      <input placeholder="Username" bind:value={username} style="display:block; margin:0.5rem 0; width:100%;" />
      <input type="password" placeholder="Password" bind:value={password} style="display:block; margin:0.5rem 0; width:100%;" />
      <button on:click={handleAuth}>{isRegister ? "Register" : "Login"}</button>
      <button on:click={() => showAuthModal = false} style="margin-left:10px;">Cancel</button>
    </div>
  </div>
{/if}

