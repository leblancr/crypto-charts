<script lang="ts">
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let isRegister = false;
  let username = "";
  let password = "";
  let errorMessage: string | null = null;

  const API_BASE = "http://127.0.0.1:8000";

  async function handleAuth() {
    const endpoint = isRegister ? "register" : "login";
    const resp = await fetch(`${API_BASE}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (resp.ok) {
      if (isRegister) {
        alert("User created, now log in!");
      } else {
        const data = await resp.json();
        dispatch("loginSuccess", { token: data.access_token, username });
      }
      errorMessage = null;
    } else {
      const err = await resp.json();
      errorMessage = (isRegister ? "Register" : "Login") + " failed: " + err.detail;
    }
  }
</script>

<div style="
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5); /* dark backdrop */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
">
  <div style="
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    min-width: 200px;
    max-width: 300px;
    width: 100%;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  ">
    <h3>{isRegister ? "Register" : "Login"}</h3>

    <input placeholder="Username" bind:value={username} style="display:block; margin:0.5rem 0; width:100%;" />
    <input type="password" placeholder="Password" bind:value={password} style="display:block; margin:0.5rem 0; width:100%;" />

    <button on:click={handleAuth}>
      {isRegister ? "Register" : "Login"}
    </button>
    <button on:click={() => dispatch("close")} style="margin-left: 10px;">
      Cancel
    </button>
  </div>
</div>
