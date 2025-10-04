<script>
  import { onMount } from "svelte";
  import Chart from "chart.js/auto";

  export let symbol; // coin id (string)

  let canvas;
  let chart;

  const API_BASE = "http://127.0.0.1:8000";

  async function loadData() {
    if (!symbol) return;  // ✅ guard against undefined
    try {
      const resp = await fetch(`${API_BASE}/coins/${symbol}/history?days=30`);
      if (!resp.ok) {
        console.error("History fetch failed:", await resp.text());
        return;
      }
      const data = await resp.json();

      const labels = data.map(d => new Date(d.timestamp).toLocaleDateString());
      const values = data.map(d => d.price);

      if (chart) chart.destroy();

      chart = new Chart(canvas, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: symbol.toUpperCase() + " / USD",
              data: values,
              borderColor: "rgba(43, 245, 39, 0.75)",
              backgroundColor: "rgba(54, 162, 235, 0.1)",
              borderWidth: 2,
              fill: true,
              pointRadius: 0,
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { title: { display: true, text: "Date" } },
            y: { title: { display: true, text: "Price (USD)" } }
          }
        }
      });
    } catch (err) {
      console.error("Error loading chart:", err);
    }
  }

  onMount(loadData);

  // reactive: reload chart only when symbol actually changes
  $: if (symbol) loadData();
</script>

<div style="height:400px;">
  <canvas bind:this={canvas}></canvas>
</div>
