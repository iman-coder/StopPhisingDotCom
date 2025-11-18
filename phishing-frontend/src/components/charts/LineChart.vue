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

onMounted(() => {
  chartInstance = new Chart(canvas.value, {
    type: "line",
    data: {
      labels: props.labels,
      datasets: [
        {
          label: "Activity",
          data: props.values,
          borderColor: "#2196f3",
          backgroundColor: "rgba(33,150,243,0.2)"
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
