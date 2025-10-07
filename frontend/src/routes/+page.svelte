<script lang="ts">
  import AuthModal from "$lib/AuthModal.svelte";
  import Watchlist from "$lib/Watchlist.svelte";
  import PriceChart from "$lib/PriceChart.svelte";

  let token: string | null = null;
  let currentUser: string | null = null;
  let selected: string | null = null;

  let showAuthModal = false;
  let isRegister = false;
  let username: string = "";
  let password: string = "";

  function handleLoginSuccess(e) {
    token = e.detail.token;
    currentUser = e.detail.username;
    localStorage.setItem("token", token);
    localStorage.setItem("username", currentUser);
    showAuthModal = false;
  }

  function logout() {
    token = null;
    currentUser = null;
    localStorage.clear();
  }
</script>

<!-- Top-right controls -->
<div>
  <button on:click={() => { showAuthModal = true; isRegister = false; }}>
    Login
  </button>
  |
  <button on:click={() => { showAuthModal = true; isRegister = true; }}>
    Register
  </button>
</div>

{#if showAuthModal}
  <AuthModal {isRegister}
             on:loginSuccess={handleLoginSuccess}
             on:close={() => showAuthModal = false}/>
{/if}

<h1 style="text-align:center; color:blue;">Crypto Dashboard</h1>

<Watchlist on:coinSelected={(e) => selected = e.detail} />

{#if selected}
  <PriceChart symbol={selected} />
{/if}
