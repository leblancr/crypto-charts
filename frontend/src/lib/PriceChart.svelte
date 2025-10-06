<script lang="ts">
  import { onMount } from "svelte";
  import Chart from "chart.js/auto";

  export let symbol: string;   // 👈 this is the prop from +page.svelte
  export let ticker: string | null;

  const API_BASE = "http://127.0.0.1:8000";

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;
  let days = "30";
  let errorMessage: string | null = null;

  async function loadChart() {
    if (!symbol) return;
    const resp = await fetch(`${API_BASE}/coins/${symbol}/history?days=${days}`);
    if (!resp.ok) {
      if (resp.status === 429) {
        errorMessage = "⚠️ Too many requests — please wait a moment and try again.";
      } else {
        errorMessage = `⚠️ Error loading chart: ${resp.statusText}`;
      }
      return;
    }
    errorMessage = null; // clear previous errors when request succeeds
    const data = await resp.json();

    const labels = data.map((d: any) => new Date(d.timestamp).toLocaleString());
    const values = data.map((d: any) => d.price);

    if (chart) chart.destroy();
    chart = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: ticker ? `${ticker.toUpperCase()} / ${symbol}` : symbol.toUpperCase(),
            data: values,
            borderColor: "rgba(43,245,39,0.75)",
            backgroundColor: "rgba(54,162,235,0.1)",
            borderWidth: 2,
            fill: true,
            pointRadius: 0,
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }

  function changeDays(e: Event) {
    days = (e.target as HTMLSelectElement).value;
    loadChart();
  }

  // onMount(loadChart);
  $: if (symbol) loadChart();

</script>

{#if errorMessage}
  <div style="margin:1rem; padding:0.5rem; background:#fee; color:#900; border:1px solid #c00; border-radius:6px;">
    {errorMessage}
  </div>
{/if}

<!-- Days dropdown -->
<div style="margin-top: 1rem;">
  <label for="days">Range:</label>
  <select id="days" bind:value={days} on:change={changeDays}>
    <option value="1">1 day (minute data)</option>
    <option value="7">7 days (hourly)</option>
    <option value="30">30 days (hourly)</option>
    <option value="90">90 days (hourly)</option>
    <option value="365">365 days (daily)</option>
  </select>
</div>

<!-- Chart -->
<div style="height:400px; margin-top:1rem;">
  <canvas bind:this={canvas}></canvas>
</div>
