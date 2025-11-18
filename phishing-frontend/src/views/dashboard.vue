<script setup>
import { ref, onMounted } from "vue";

// Chart components
import PieChart from "../components/charts/PieChart.vue";
import LineChart from "../components/charts/LineChart.vue";

// Import services
import {
    getGlobalMetrics,
    getRiskDistribution,
    getStatusDistribution,
    getDomainCounts,
    getTopRiskyDomains,
    getMonthlyActivity,
    getDailyActivity,
    getTopRiskyUrls,
    getMostRecentUrls,
    getRecentEvents,
    searchDashboard
} from "../services/dashboardService.js";

/* -------------------------------------------------------
 * REACTIVE STATE
 * ----------------------------------------------------- */
const globalMetrics = ref({});
const riskDistribution = ref({});
const statusDistribution = ref({});
const domainCounts = ref({});
const topRiskyDomains = ref([]);

const monthlyActivity = ref([]);
const dailyActivity = ref([]);

const topRiskyUrls = ref([]);
const mostRecentUrls = ref([]);

const recentEvents = ref([]);

const searchQuery = ref("");
const searchResults = ref([]);

/* -------------------------------------------------------
 * FETCH DASHBOARD DATA
 * ----------------------------------------------------- */
async function loadDashboard() {
    globalMetrics.value = await getGlobalMetrics();
    riskDistribution.value = await getRiskDistribution();
    statusDistribution.value = await getStatusDistribution();

    domainCounts.value = await getDomainCounts();
    topRiskyDomains.value = await getTopRiskyDomains();

    monthlyActivity.value = await getMonthlyActivity();
    dailyActivity.value = await getDailyActivity();

    topRiskyUrls.value = await getTopRiskyUrls();
    mostRecentUrls.value = await getMostRecentUrls();

    recentEvents.value = await getRecentEvents();
}

/* -------------------------------------------------------
 * SEARCH LOGIC
 * ----------------------------------------------------- */
async function handleSearch() {
    if (searchQuery.value.trim().length < 2) return;
    searchResults.value = await searchDashboard(searchQuery.value);
}

onMounted(() => loadDashboard());
</script>

<template>
  <div class="dashboard-container">

    <!-- SEARCH BAR -->
    <div class="search-bar mb-4">
      <input
        type="text"
        v-model="searchQuery"
        @input="handleSearch"
        placeholder="Search URLs, domains…"
        class="form-control"
      >
    </div>

    <!-- SEARCH RESULTS -->
<div v-if="searchResults.length" class="search-results mb-4">
  <h3>Search Results</h3>
  <table class="table table-striped">
    <thead>
      <tr>
        <th>URL</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in searchResults" :key="item.id">
        <td>{{ item.url }}</td>
        <td>{{ item.status }}</td>
      </tr>
    </tbody>
  </table>
</div>

    <!-- GLOBAL METRICS -->
<section class="metrics-section mb-4">
  <h2>Global Metrics</h2>
  <div class="metrics-grid">
    <div class="metric-card">
      <h3>Total URLs</h3>
      <p>{{ globalMetrics.total_urls }}</p>
    </div>
    <div class="metric-card">
      <h3>Safe</h3>
      <p>{{ globalMetrics.safe }}</p>
    </div>
    <div class="metric-card">
      <h3>Suspicious</h3>
      <p>{{ globalMetrics.suspicious }}</p>
    </div>
    <div class="metric-card">
      <h3>Malicious</h3>
      <p>{{ globalMetrics.malicious }}</p>
    </div>
  </div>
</section>

<!-- DISTRIBUTION CHARTS -->
<section class="charts-section mb-4">
  <div class="chart-row">
    <div class="chart-card">
      <h3>Risk Distribution</h3>
      <PieChart
        :labels="Object.keys(riskDistribution)"
        :values="Object.values(riskDistribution)"
      />
    </div>
    <div class="chart-card">
      <h3>Status Distribution</h3>
      <PieChart
        :labels="Object.keys(statusDistribution)"
        :values="Object.values(statusDistribution)"
      />
    </div>
  </div>
</section>

<!-- DOMAIN ANALYTICS -->
<section class="charts-section mb-4">
  <div class="chart-row">
    <div class="chart-card">
      <h3>Domain Counts</h3>
      <PieChart
        :labels="Object.keys(domainCounts)"
        :values="Object.values(domainCounts)"
      />
    </div>
    <div class="chart-card">
      <h3>Top Risky Domains</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Domain</th>
            <th>Risky URLs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in topRiskyDomains" :key="d.domain">
            <td>{{ d.domain }}</td>
            <td>{{ d.count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- TIME SERIES -->
<section class="charts-section mb-4">
  <div class="chart-row">
    <div class="chart-card">
      <h3>Monthly Activity</h3>
      <LineChart
        :labels="monthlyActivity.map(a => a.month)"
        :values="monthlyActivity.map(a => a.scanned)"
      />
    </div>
    <div class="chart-card">
      <h3>Daily Activity</h3>
      <LineChart
        :labels="dailyActivity.map(a => a.day)"
        :values="dailyActivity.map(a => a.scanned)"
      />
    </div>
  </div>
</section>

<!-- TOP URL LISTS -->
<section class="lists-section mb-4">
  <div class="list-row">
    <div class="list-card">
      <h3>Top Risky URLs</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>URL</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="url in topRiskyUrls" :key="url.id">
            <td>{{ url.url }}</td>
            <td>{{ url.risk }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="list-card">
      <h3>Most Recent URLs</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>URL</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="url in mostRecentUrls" :key="url.id">
            <td>{{ url.url }}</td>
            <td>{{ url.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
<!-- RECENT EVENTS -->
<section>
  <h2>Recent Events</h2>
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Timestamp</th>
        <th>Action</th>
        <th>URL</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="event in recentEvents" :key="event.id">
        <td>{{ event.timestamp }}</td>
        <td>{{ event.action }}</td>
        <td>{{ event.url }}</td>
      </tr>
    </tbody>
  </table>
</section>

  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.metrics-grid {
  display: flex;
  gap: 1rem;
}

.metric-card {
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.search-bar input {
  width: 100%;
  padding: 8px;
}
.charts-section, .lists-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-row, .list-row {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.chart-card, .list-card {
  flex: 1 1 48%;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.metric-card {
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: 0.5rem;
  border: 1px solid #ddd;
}
.search-results .table {
  width: 100%;
  border-collapse: collapse;
}

.search-results th, 
.search-results td {
  padding: 0.5rem;
  border: 1px solid #ddd;
}
</style>
