<template>
  <div class="card p-3 mb-3">
    <h5>Add a new URL</h5>
    <form @submit.prevent="submitForm" class="form-grid">
      <input v-model="url.url" class="form-control" placeholder="Enter URL..." />
      <input v-model="url.domain" class="form-control" placeholder="Enter Domain..." />
      <input v-model="url.threat" class="form-control" placeholder="Threat Category..." />
      <select v-model="url.risk_rating" class="form-control">
        <option value="" disabled>Risk rating...</option>
        <option value="Very Low">Very Low</option>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
        <option value="Very High">Very High</option>
      </select>
      <select v-model="url.status" class="form-control">
        <option value="" disabled>Select status...</option>
        <option value="Active">active</option>
        <option value="Inactive">inactive</option>
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
      risk_rating: "",
      status: "",
      source: ""
    });

    function scoreToLabel(n) {
      const v = Number(n);
      if (!Number.isFinite(v)) return null;
      if (v >= 75) return 'Very High';
      if (v >= 60) return 'High';
      if (v >= 40) return 'Medium';
      if (v >= 20) return 'Low';
      return 'Very Low';
    }

    async function submitForm() {
      // If the user selected a rating, prefer that as the threat label
      const payload = { ...url.value };
      if (payload.risk_rating) {
        payload.threat = payload.risk_rating;
      }
      // If threat was entered as a numeric string, map it to label
      if (payload.threat && /^[0-9]+$/.test(String(payload.threat).trim())) {
        const label = scoreToLabel(Number(payload.threat));
        if (label) payload.threat = label;
      }

      // remove UI-only fields before sending
      delete payload.risk_rating;

      await addUrl(payload);
      url.value = { url: "", domain: "", threat: "", risk_rating: "", status: "", source: "" };
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
