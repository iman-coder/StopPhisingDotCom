<template>
  <div class="card p-3">
    <h5>URL List</h5>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>URL</th>
          <th>Domain</th>
          <th>Threat</th>
          <th>Date Added</th>
          <th>Status</th>
          <th>Source</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="url in urls.length ? urls : mockData" :key="url.id">
          <td data-label="ID">{{ url.id }}</td>
          <td data-label="URL">{{ url.url }}</td>
          <td data-label="Domain">{{ url.domain }}</td>
          <td data-label="Threat">{{ url.threat }}</td>
          <td data-label="Date Added">{{ url.date }}</td>
          <td data-label="Status">{{ url.status }}</td>
          <td data-label="Source">{{ url.source }}</td>
          <td data-label="Actions">
            <button class="btn btn-warning btn-sm me-1" @click="startEdit(url)">
              Update
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteUrlItem(url.id)">
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="editingUrl" class="card p-3 mt-3">
    <h5>Edit URL</h5>
    <form @submit.prevent="saveEdit">
      <input v-model="editingUrl.url" class="form-control mb-2" placeholder="URL" />
      <input v-model="editingUrl.domain" class="form-control mb-2" placeholder="Domain" />
      <input v-model="editingUrl.threat" class="form-control mb-2" placeholder="Threat" />
      <!-- date is set automatically on the backend; removed from edit form -->
      <input v-model="editingUrl.status" class="form-control mb-2" placeholder="Status" />
      <input v-model="editingUrl.source" class="form-control mb-2" placeholder="Source" />
      <button class="btn btn-success me-2" type="submit">Save</button>
      <button class="btn btn-secondary" type="button" @click="cancelEdit">Cancel</button>
    </form>
  </div>
</template>

<script>
import { deleteUrl, updateUrl } from "../services/urlService.js";
import { ref, reactive } from "vue";
import { isAdmin } from "../services/authService.js";

export default {
  name: "UrlTable",
  props: {
    urls: { type: Array, required: true }
  },
  emits: ["deleted", "updated"],
  setup(props, { emit }) {
    const mockData = [
      { id: 1, url: "https://example.com", domain: "example.com", threat: "phishing", date: "2024-01-01", status: "active", source: "user" },
      { id: 2, url: "http://bad.com", domain: "bad.com", threat: "malware", date: "2024-01-02", status: "inactive", source: "admin" },
      { id: 3, url: "https://testsite.org", domain: "testsite.org", threat: "suspicious", date: "2024-01-03", status: "active", source: "user" }
    ];
    const editingUrl = ref(null);
    async function saveEdit() {
      // call updateUrl service here
      if (!editingUrl.value) return;
      try {
        // send a plain object copy to avoid proxy/serialization issues
        const payload = { ...editingUrl.value };
        await updateUrl(editingUrl.value.id, payload);
        emit("updated");
        editingUrl.value = null; // hide the edit card
      } catch (err) {
        console.error("Failed to save edit:", err);
        // show a minimal user-visible error
        alert("Failed to save changes. Check console for details.");
      }
    }

    function startEdit(url) {
      // create a reactive copy inside the ref so v-model works correctly
      editingUrl.value = reactive({ ...url });
    }

    function cancelEdit() {
      editingUrl.value = null;
    }

    async function deleteUrlItem(id) {
      if (!isAdmin()) {
        alert('Only admin users can delete URLs.');
        return;
      }
      await deleteUrl(id);
      emit("deleted");
    }

    return { mockData, editingUrl, saveEdit, deleteUrlItem, startEdit, cancelEdit };
  }
};
</script>

<style scoped>
/* Responsive table -> card layout on small screens */
@media (max-width: 640px) {
  table.table {
    border: 0;
  }
  table.table thead {
    display: none;
  }
  table.table tbody, table.table tr, table.table td {
    display: block;
    width: 100%;
  }
  table.table tr {
    margin-bottom: 12px;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 8px;
  }
  table.table td {
    padding: 6px 8px;
    border: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  table.table td::before {
    content: attr(data-label) ":";
    font-weight: 600;
    margin-right: 8px;
    flex: 0 0 auto;
  }
  /* Actions buttons stack nicely */
  table.table td[data-label="Actions"] {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
}

/* Make edit form inputs full-width on small screens */
@media (max-width: 640px) {
  .card form input.form-control {
    width: 100%;
    box-sizing: border-box;
  }
  .card form .btn {
    width: 100%;
    margin-bottom: 8px;
  }
}
</style>
