<template>
  <div class="urls-page">
    <h2>Manage URLs</h2>
    <section class="info-section">
      <p>
        Here you can manage the list of URLs monitored by the system. You can
        add new URLs, import/export via CSV, and delete all entries if needed.
      </p>
    </section>
      <section class="controls-row">
        <div class="control-card">
          <div class="io-stack">
            <ImportCsv @refresh="loadUrls" />
            <div style="margin-top:8px"><ExportCsv /></div>
          </div>
        </div>
        <div class="control-card">
          <AddUrlForm @url-added="loadUrls" />
        </div>
        
      </section>
      <div style="margin-top:8px">
              <button class="btn btn-danger w-100" @click="confirmDeleteAll">
                Delete All URLs
              </button>
            </div>

    <section class="table-row">
      <div class="table-wrapper">
        <UrlTable :urls="urls" @deleted="loadUrls" @updated="loadUrls" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import ImportCsv from "../components/ImportCsv.vue";
import ExportCsv from "../components/ExportCsv.vue";
import AddUrlForm from "../components/AddUrlForm.vue";
import UrlTable from "../components/UrlTable.vue";
import { getUrls, deleteAll } from "../services/urlService.js";
//test backend connection

const testBackend = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/urls/health");
    const data = await res.json();
    alert(JSON.stringify(data));
  } catch (err) {
    alert("Backend not reachable");
  }
};

//testBackend();
//end test backend connection

export default {
  name: "URLsView",
  components: { ImportCsv, ExportCsv, AddUrlForm, UrlTable },
  
  setup() {
    const urls = ref([]);

    async function loadUrls() {
      urls.value = await getUrls();
    }

    async function confirmDeleteAll() {
      const ok = window.confirm("Delete ALL URLs? This action cannot be undone. Continue?");
      if (!ok) return;
      try {
        const res = await deleteAll();
        // refresh the list
        await loadUrls();
        alert(`Deleted ${res.deleted} URLs. Before: ${res.before}, After: ${res.after}`);
      } catch (err) {
        console.error(err);
        alert("Failed to delete all URLs. Check console for details.");
      }
    }

    onMounted(loadUrls);

    return { urls, loadUrls, confirmDeleteAll };
  }
};
</script>

<style scoped>
.urls-page {
  padding: 16px;
}
.controls-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.control-card {
  flex: 1 1 300px;
  min-width: 220px;
}
.table-row {
  display: block;
}
.table-wrapper {
  width: 100%;
  overflow-x: auto; /* allow horizontal scroll on small screens */
  -webkit-overflow-scrolling: touch;
}

/* Mobile tweaks */
@media (max-width: 640px) {
  .control-card {
    flex: 1 1 100%;
    min-width: 0;
  }
}

/* Make table cells wrap and compact on small screens by targeting table inside UrlTable component */
.table-wrapper table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
}
.table-wrapper th,
.table-wrapper td {
  padding: 0.45rem;
  border: 1px solid #ddd;
  word-break: break-word;
}
</style>
