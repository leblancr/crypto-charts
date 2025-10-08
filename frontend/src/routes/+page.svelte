<!-- FILE: src/routes/+page.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import AuthModal from "$lib/AuthModal.svelte";
  import Watchlist from "$lib/Watchlist.svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let token: string | null = null;
  let currentUser: string | null = null;
  let selected: string | null = null;

  let showAuthModal = false;   // ✅ start hidden
  let isRegister = false;

  function handleLoginSuccess(e) {
    token = e.detail.token;
    currentUser = e.detail.username;
    localStorage.setItem("token", e.detail.token);
    localStorage.setItem("username", e.detail.username);
    showAuthModal = false;     // ✅ hide after login
  }

  function logout() {
    token = null;
    currentUser = null;
    localStorage.clear();
  }

  onMount(() => {
    token = localStorage.getItem("token");
    currentUser = localStorage.getItem("username");
  });
</script>

<!-- Top bar -->
<div style="display:flex;justify-content:center;align-items:center;position:relative;height:50px;padding:0 1rem;margin-bottom:1rem;">
  <h1 style="color:blue;margin:0;font-size:1.5rem;line-height:50px;">Crypto Dashboard</h1>

  <div style="position:absolute;right:1rem;top:0;height:100%;display:flex;align-items:center;gap:0.5rem;">
    {#if currentUser}
      <span>Logged in as <strong>{currentUser}</strong></span>
      <button on:click={logout}>Logout</button>
    {:else}
      <button on:click={() => { showAuthModal = true; isRegister = false; }}>Login</button>
      |
      <button on:click={() => { showAuthModal = true; isRegister = true; }}>Register</button>
    {/if}
  </div>
</div>

<!-- Auth modal shows ONLY when user clicks Login/Register -->
{#if showAuthModal}
  <AuthModal {isRegister}
             on:loginSuccess={handleLoginSuccess}
             on:close={() => showAuthModal = false}/>
{/if}

<!-- Watchlist & chart after login -->
{#if currentUser && token}
  <Watchlist {token} on:coinSelected={(e) => selected = e.detail} />
{/if}

{#if selected}
  <PriceChart symbol={selected} />
{/if}
