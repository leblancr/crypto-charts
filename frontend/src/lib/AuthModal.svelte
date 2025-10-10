<!-- FILE: src/lib/AuthModal.svelte -->
<script lang="ts">
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let isRegister = false;
  let mode: "login" | "register" | "forgot" = isRegister ? "register" : "login";

  let username = "";
  let password = "";
  let newPassword = "";
  let errorMessage: string | null = null;
  let message: string | null = null;

  const API_BASE = import.meta.env.VITE_API_BASE;

  async function handleAuth() {
    const endpoint = mode === "register" ? "register" : "login";
    const resp = await fetch(`${API_BASE}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (resp.ok) {
      if (mode === "register") {
        message = "User created, now log in!";
        mode = "login";
      } else {
        const data = await resp.json();
        dispatch("loginSuccess", { token: data.access_token, username });
        dispatch("close");
      }
      errorMessage = null;
    } else {
      const err = await resp.json();
      errorMessage = err.detail || "Authentication failed";
    }
  }

  async function handleReset() {
    const resp = await fetch(`${API_BASE}/reset-password-direct`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, new_password: newPassword })
    });
    if (resp.ok) {
      message = "Password updated. You can log in with the new password.";
      mode = "login";
      errorMessage = null;
    } else {
      const err = await resp.json();
      errorMessage = err.detail || "Reset failed";
    }
  }

  function switchMode(newMode: "login" | "register" | "forgot") {
    mode = newMode;
    errorMessage = null;
    message = null;
    username = "";
    password = "";
    newPassword = "";
  }

</script>

<div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.35);z-index:9999;">
  <div class="modal" style="padding:1rem;border:1px solid #ccc;border-radius:8px;max-width:380px;">
    {#if mode === "login"}
      <h2>Login</h2>
      <div>
        <input type="text" bind:value={username} placeholder="Username" style="display:block;margin-bottom:0.5rem;" />
        <input type="password" bind:value={password} placeholder="Password" style="display:block;margin-bottom:0.5rem;" />
      </div>
      <button on:click={handleAuth}>Login</button>

      {#if errorMessage}
        <p style="color:red;">{errorMessage}</p>
        <div style="margin-top:0.5rem;">
          <button type="button" on:click={() => switchMode("forgot")} style="color:blue;cursor:pointer;background:none;border:none;padding:0;">
            Forgot password?
          </button>
        </div>
      {/if}

      {#if message}
        <p style="color:green;">{message}</p>
      {/if}
    {:else if mode === "register"}
      <h2>Register</h2>
        <div style="margin-top:.5rem;">
          <button type="button" on:click={() => switchMode("login")} style="color:blue;cursor:pointer;">
            Already have an account? Login
          </button>
        </div>
      <button on:click={handleAuth}>Register</button>

      {#if errorMessage}<p style="color:red;">{errorMessage}</p>{/if}
      {#if message}<p style="color:green;">{message}</p>{/if}

      <div style="margin-top:.5rem;">
        <button type="button" on:click={() => mode="login"} style="color:blue;cursor:pointer;">
          Already have an account? Login
        </button>
      </div>

    {:else if mode === "forgot"}
      <h2>Reset Password</h2>
      <div>
        <input type="text" bind:value={username} placeholder="Username" style="display:block;margin-bottom:0.5rem;" />
        <input type="password" bind:value={newPassword} placeholder="New Password" style="display:block;margin-bottom:0.5rem;" />
      </div>
      <button on:click={handleReset}>Update password</button>

      {#if errorMessage}<p style="color:red;">{errorMessage}</p>{/if}
      {#if message}<p style="color:green;">{message}</p>{/if}

      <div style="margin-top:.5rem;">
        <button type="button" on:click={() => switchMode("login")} style="color:blue;cursor:pointer;background:none;border:none;padding:0;">
          Back to login
        </button>
      </div>
    {/if}
    <button on:click={() => dispatch("close")}>Close</button>
  </div>
</div>

