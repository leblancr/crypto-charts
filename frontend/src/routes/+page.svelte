<!-- FILE: src/routes/+page.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import AuthModal from "$lib/AuthModal.svelte";
  import Watchlist from "$lib/Watchlist.svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  import svelteLogo from "$lib/assets/32px-Svelte_Logo.png";
  import fastapiLogo from "$lib/assets/32px-fastapi-logo.png";
  import postgresLogo from "$lib/assets/32px-Postgresql_elephant.png";
  import freebsdLogo from "$lib/assets/32x32freebsd-logo.png";

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
  <h1 style="color:blue;margin:0;font-size:1.5rem;line-height:50px;">Crypto Charts</h1>

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

<footer class="corner-icons">
  <img src={svelteLogo} alt="Svelte" class="corner-icon" />
  <img src={fastapiLogo} alt="Fastapi" class="corner-icon" />
  <img src={postgresLogo} alt="PostgreSQL" class="corner-icon" />
  <img src={freebsdLogo} alt="FreeBSD" class="corner-icon" />
</footer>

<style>
  .corner-icons {
    position: fixed;
    right: 10px;
    bottom: 10px;
    display: flex;
    gap: 8px;
  }

  .corner-icon {
    width: 16px;
    height: 16px;
    opacity: 0.85;
  }

  .corner-icon:hover {
    opacity: 1;
  }
</style>


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
