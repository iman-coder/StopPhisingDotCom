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

onMounted(() => {
  chartInstance = new Chart(canvas.value, {
    type: "pie",
    data: {
      labels: props.labels,
      datasets: [
        {
          data: props.values,
          backgroundColor: props.colors || ["#4caf50", "#ff9800", "#f44336"]
        }
      ]
    },
    options: { responsive: true }
  });
});

watch([() => props.labels, () => props.values], () => {
  if (chartInstance) {
    chartInstance.data.labels = props.labels;
    chartInstance.data.datasets[0].data = props.values;
    chartInstance.update();
  }
});
</script>
