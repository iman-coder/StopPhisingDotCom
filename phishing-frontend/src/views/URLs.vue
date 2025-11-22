<template>
  <div>
    <!--<button @click="testBackend">Test Backend</button>-->
    <h2>Manage URLs</h2>
    <ImportCsv @refresh="loadUrls" />
    <AddUrlForm @url-added="loadUrls" />
    <ExportCsv />
    <UrlTable :urls="urls" @deleted="loadUrls" @updated="loadUrls" />
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import ImportCsv from "../components/ImportCsv.vue";
import ExportCsv from "../components/ExportCsv.vue";
import AddUrlForm from "../components/AddUrlForm.vue";
import UrlTable from "../components/UrlTable.vue";
import { getUrls } from "../services/urlService.js";
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

    onMounted(loadUrls);

    return { urls, loadUrls };
  }
};
</script>
