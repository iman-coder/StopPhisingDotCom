<template>
  <div class="card p-3 mb-3">
    <h5>Add a new URL</h5>
    <form @submit.prevent="submitForm" class="form-grid">
      <input v-model="url.url" class="form-control" placeholder="Enter URL..." />
      <input v-model="url.domain" class="form-control" placeholder="Enter Domain..." />
      <input v-model="url.threat" class="form-control" placeholder="Threat Category..." />
      <select v-model="url.status" class="form-control">
        <option value="" disabled>Select status...</option>
        <option value="Active">Active</option>
        <option value="Inactive">Inactive</option>
      </select>
      <input v-model="url.source" class="form-control" placeholder="Source..." />
      <div class="button-wrapper">
        <button class="btn btn-primary" type="submit">Add URL</button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from "vue";
import { addUrl } from "../services/urlService.js";

export default {
  name: "AddUrlForm",
  setup(_, { emit }) {
    const url = ref({
      url: "",
      domain: "",
      threat: "",
      status: "",
      source: ""
    });

    async function submitForm() {
      await addUrl(url.value);
      url.value = { url: "", domain: "", threat: "", status: "", source: "" };
      emit("url-added"); // trigger table refresh
    }

    return { url, submitForm };
  }
};
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  align-items: end;
}

/* Center the button under the inputs */
.button-wrapper {
  grid-column: 1 / -1; /* span all columns */
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.button-wrapper .btn {
  width: 150px; /* optional fixed width */
}
</style>
