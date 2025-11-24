<!-- ImportCsv.vue -->
<template>
  <div class="my-4 p-3 border rounded bg-light">
    <h5>Import CSV</h5>

    <input type="file" accept=".csv" @change="onFileChange" class="form-control" />

    <button 
      class="btn btn-primary mt-2"
      :disabled="!csvFile"
      @click="uploadCsv"
    >
      Upload CSV
    </button>

    <p v-if="message" class="mt-2">{{ message }}</p>
  </div>
</template>

<script>
import { importCSV } from "../services/csvService";

export default {
  name: "ImportCsv",
  data() {
    return {
      csvFile: null,
      message: "",
    };
  },
  methods: {
    onFileChange(e) {
      this.csvFile = e.target.files[0];
    },

    async uploadCsv() {
      if (!this.csvFile) return;

      try {
        const result = await importCSV(this.csvFile);
        // server is expected to return a JSON { message: '...' } or similar
        this.message = (result && result.message) || "Import successful!";
        this.$emit("refresh");
      } catch (err) {
        console.error("CSV import failed:", err);
        this.message = "Import failed. Check console for details.";
      }
    }
  }
};
</script>
