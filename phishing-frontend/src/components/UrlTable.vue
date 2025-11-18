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
          <td>{{ url.id }}</td>
          <td>{{ url.url }}</td>
          <td>{{ url.domain }}</td>
          <td>{{ url.threat }}</td>
          <td>{{ url.date }}</td>
          <td>{{ url.status }}</td>
          <td>{{ url.source }}</td>
          <td>
            <button class="btn btn-warning btn-sm me-1" @click="editingUrl = reactive({ ...url })">
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
      <input v-model="editingUrl.date" type="date" class="form-control mb-2" placeholder="Date" />
      <input v-model="editingUrl.status" class="form-control mb-2" placeholder="Status" />
      <input v-model="editingUrl.source" class="form-control mb-2" placeholder="Source" />
      <button class="btn btn-success me-2" type="submit">Save</button>
      <button class="btn btn-secondary" type="button" @click="editingUrl = null">Cancel</button>
    </form>
  </div>
</template>

<script>
import { deleteUrl, updateUrl } from "../services/urlService.js";
import { ref, reactive } from "vue";

export default {
  name: "UrlTable",
  props: {
    urls: { type: Array, required: true }
  },
  setup(props, { emit }) {
    const mockData = [
      { id: 1, url: "https://example.com", domain: "example.com", threat: "phishing", date: "2024-01-01", status: "active", source: "user" },
      { id: 2, url: "http://bad.com", domain: "bad.com", threat: "malware", date: "2024-01-02", status: "inactive", source: "admin" },
      { id: 3, url: "https://testsite.org", domain: "testsite.org", threat: "suspicious", date: "2024-01-03", status: "active", source: "user" }
    ];
    const editingUrl = ref(null);
    async function saveEdit() {
      // call updateUrl service here
      await updateUrl(editingUrl.value.id, editingUrl.value);
      emit("updated"); 
      editingUrl.value = null; // hide the edit card
    }

    async function deleteUrlItem(id) {
      await deleteUrl(id);
      emit("deleted");
    }

    return { mockData, editingUrl, saveEdit, deleteUrlItem };
  }
};
</script>
