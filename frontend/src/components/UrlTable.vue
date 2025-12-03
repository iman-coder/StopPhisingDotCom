<template>
  <div class="card p-3">
    <h5>URL List</h5>

    <!-- Search box -->
    <div class="mb-3">
      <input
        v-model="query"
        class="form-control"
        placeholder="Search URLs, domain, threat, status or source"
      />
    </div>

    <!-- Edit form -->
    <div v-if="editingUrl" class="card p-3 mb-3">
      <h5>Edit URL</h5>
      <form @submit.prevent="saveEdit">
        <input v-model="editingUrl.url" class="form-control mb-2" placeholder="URL" />
        <input v-model="editingUrl.domain" class="form-control mb-2" placeholder="Domain" />
        <input v-model="editingUrl.threat" class="form-control mb-2" placeholder="Threat" />
        <select v-model="editingUrl.status" class="form-control">
          <option value="" disabled>Select status...</option>
          <option value="Active">active</option>
          <option value="Inactive">inactive</option>
        </select>
        <input v-model="editingUrl.source" class="form-control mb-2" placeholder="Source" />

        <button class="btn btn-success me-2" type="submit">Save</button>
        <button class="btn btn-secondary" type="button" @click="cancelEdit">Cancel</button>
      </form>
    </div>

    <!-- Table -->
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
        <tr v-for="url in items" :key="url.id">
          <td data-label="ID">{{ url.id }}</td>
          <td data-label="URL">{{ url.url }}</td>
          <td data-label="Domain">{{ url.domain }}</td>
          <td data-label="Threat">{{ url.threat }}</td>
          <td data-label="Date Added">{{ url.date_added || url.date }}</td>
          <td data-label="Status">{{ url.status }}</td>
          <td data-label="Source">{{ url.source }}</td>
          <td data-label="Actions">
            <button class="btn btn-warning btn-sm me-1" @click="startEdit(url)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteUrlItem(url.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div class="pagination d-flex align-items-center gap-2">
      <button class="btn btn-sm btn-outline-primary" @click="prevPage" :disabled="page <= 1">
        Prev
      </button>

      <span>Page {{ page }} of {{ totalPages }}</span>

      <button class="btn btn-sm btn-outline-primary" @click="nextPage" :disabled="page >= totalPages">
        Next
      </button>

      <div class="ms-auto">Total: {{ total }}</div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, onMounted, computed } from "vue";
import { getUrls, updateUrl, deleteUrl } from "../services/urlService.js";
import { isAdmin } from "../services/authService.js";

export default {
  name: "UrlTable",
  props: {
    urls: { type: Array, required: false },
  },
  emits: ["deleted", "updated"],

  setup(props, { emit }) {
    const query = ref("");
    const page = ref(1);
    const per_page = ref(20);
    const total = ref(0);
    const items = ref(props.urls || []);
    const editingUrl = ref(null);

    let debounceTimer = null;

    const totalPages = computed(() =>
      Math.max(1, Math.ceil(total.value / per_page.value))
    );

    async function fetchUrls() {
      try {
        const res = await getUrls({ query: query.value, page: page.value, per_page: per_page.value });
        items.value = res.items || [];
        total.value = res.total || 0;
      } catch (err) {
        console.error("Failed to fetch urls", err);
      }
    }

    watch([query, page, per_page], () => {
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        page.value = 1;
        fetchUrls();
      }, 300);
    });

    onMounted(fetchUrls);

    function startEdit(url) {
      editingUrl.value = reactive({ ...url });
    }

    function cancelEdit() {
      editingUrl.value = null;
    }

    async function saveEdit() {
      if (!editingUrl.value) return;

      try {
        await updateUrl(editingUrl.value.id, { ...editingUrl.value });
        emit("updated");
        editingUrl.value = null;
        fetchUrls();
      } catch (err) {
        console.error("Failed to save edit:", err);
        alert("Failed to save changes. Check console for details.");
      }
    }

    async function deleteUrlItem(id) {
      if (!isAdmin()) {
        alert("Only admin users can delete URLs.");
        return;
      }
      try {
        await deleteUrl(id);
        emit("deleted");
        fetchUrls();
      } catch (err) {
        console.error("Failed to delete url:", err);
        alert("Failed to delete URL. Check console for details.");
      }
    }

    function prevPage() {
      if (page.value > 1) {
        page.value -= 1;
        fetchUrls();
      }
    }

    function nextPage() {
      if (page.value < totalPages.value) {
        page.value += 1;
        fetchUrls();
      }
    }

    return {
      query,
      page,
      per_page,
      total,
      items,
      editingUrl,
      startEdit,
      cancelEdit,
      saveEdit,
      deleteUrlItem,
      prevPage,
      nextPage,
      totalPages,
    };
  },
};
</script>

<style scoped>
/* Mobile table layout */
@media (max-width: 640px) {
  table.table {
    border: 0;
  }
  table.table thead {
    display: none;
  }
  table.table tbody,
  table.table tr,
  table.table td {
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
  }
  table.table td::before {
    content: attr(data-label) ":";
    font-weight: 600;
    margin-right: 8px;
  }

  /* Edit form buttons */
  .card form input.form-control {
    width: 100%;
  }
  .card form .btn {
    width: 100%;
    margin-bottom: 8px;
  }
}
</style>
