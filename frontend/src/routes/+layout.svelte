<script lang="ts">
  import favicon from '$lib/assets/favicon.svg';
  import "../app.css";  // ✅ relative path works the same
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<!-- ✅ Use slot for children -->
<slot />
