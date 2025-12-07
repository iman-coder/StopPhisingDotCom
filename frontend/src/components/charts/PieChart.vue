<template>
  <div>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart, PieController, ArcElement, Tooltip, Legend } from "chart.js";

Chart.register(PieController, ArcElement, Tooltip, Legend);

const props = defineProps({
  labels: Array,
  values: Array,
  colors: Array
});

const canvas = ref(null);
let chartInstance = null;

function safeArray(x) {
  return Array.isArray(x) ? x : [];
}

onMounted(() => {
  const labels = safeArray(props.labels);
  const values = safeArray(props.values);

  // Only create the chart with valid arrays to avoid Chart.js errors
  chartInstance = new Chart(canvas.value, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: values,
          backgroundColor: props.colors || ["#4caf50", "#ff9800", "#f44336"]
        }
      ]
    },
    options: { responsive: true }
  });
});

watch([() => props.labels, () => props.values], () => {
  if (!chartInstance) return;
  const labels = safeArray(props.labels);
  const values = safeArray(props.values);
  chartInstance.data.labels = labels;
  chartInstance.data.datasets[0].data = values;
  chartInstance.update();
});
</script>
