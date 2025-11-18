<!-- ExportCsv.vue -->
<template>
  <div class="my-3">
    <button class="btn btn-success" @click="downloadCsv">
      Export CSV
    </button>
  </div>
</template>

<script>
import { exportCSV } from "../services/csvService";

export default {
  name: "ExportCsv",
  methods: {
    async downloadCsv() {
      const csvData = await exportCSV();

      const blob = new Blob([csvData], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "urls_export.csv";
      a.click();

      window.URL.revokeObjectURL(url);
    }
  }
};
</script>
