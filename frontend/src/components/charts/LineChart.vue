<template>
  <div>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from "chart.js";

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale);

const props = defineProps({
  labels: Array,
  values: Array
});

const canvas = ref(null);
let chartInstance = null;

function safeArray(x) {
  return Array.isArray(x) ? x : [];
}

onMounted(() => {
  const labels = safeArray(props.labels);
  const values = safeArray(props.values);

  chartInstance = new Chart(canvas.value, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Activity",
          data: values,
          borderColor: "#2196f3",
          backgroundColor: "rgba(33,150,243,0.2)"
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
