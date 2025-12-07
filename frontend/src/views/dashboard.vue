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

// helpers
function safeArray(x) { return Array.isArray(x) ? x : []; }
function safeObject(x) { return x && typeof x === 'object' && !Array.isArray(x) ? x : {}; }
function safeNumber(x) { const n = Number(x); return Number.isFinite(n) ? n : 0; }
function formatNumber(x) { try { return safeNumber(x).toLocaleString(); } catch (e) { return String(safeNumber(x)); } }

// search removed from dashboard (handled elsewhere)

/* -------------------------------------------------------
 * FETCH DASHBOARD DATA
 * ----------------------------------------------------- */
async function loadDashboard() {
    globalMetrics.value = safeObject(await getGlobalMetrics());
    // Normalize risk distribution into canonical buckets so the PieChart always receives
    // { safe: number, suspicious: number, malicious: number }
    try {
      const rawRisk = await getRiskDistribution();
      console.debug("raw risk distribution:", rawRisk);
      const normalized = { safe: 0, suspicious: 0, malicious: 0 };

      if (Array.isArray(rawRisk)) {
        // handle [{ threat: 'malicious', count: 10 }, ...]
        rawRisk.forEach(r => {
          const key = (r.threat || r.label || '').toString().toLowerCase();
          const count = Number(r.count ?? r.value ?? 0);
          if (/malicious|high|malware|phish/.test(key)) normalized.malicious += count;
          else if (/susp|low/.test(key)) normalized.suspicious += count;
          else if (/safe|none|clean/.test(key)) normalized.safe += count;
        });
      } else if (rawRisk && typeof rawRisk === 'object') {
        // handle { safe: n, suspicious: m, malicious: k } or other mappings
        Object.entries(rawRisk).forEach(([k, v]) => {
          const key = k.toString().toLowerCase();
          const count = Number(v || 0);
          if (/malicious|high|malware|phish/.test(key)) normalized.malicious += count;
          else if (/susp|low/.test(key)) normalized.suspicious += count;
          else if (/safe|none|clean/.test(key)) normalized.safe += count;
        });
      }

      riskDistribution.value = normalized;
    } catch (e) {
      console.error('Failed to load risk distribution', e);
      riskDistribution.value = {};
    }
    statusDistribution.value = safeObject(await getStatusDistribution());

    domainCounts.value = safeObject(await getDomainCounts());
    topRiskyDomains.value = safeArray(await getTopRiskyDomains()).slice(0, 10);

    monthlyActivity.value = safeArray(await getMonthlyActivity());
    dailyActivity.value = safeArray(await getDailyActivity());

    // enforce client-side limits and safe shapes
    topRiskyUrls.value = safeArray(await getTopRiskyUrls()).slice(0, 10);
    mostRecentUrls.value = safeArray(await getMostRecentUrls()).slice(0, 10);

    recentEvents.value = safeArray(await getRecentEvents());
}

onMounted(() => loadDashboard());
</script>

<template>
  <div class="dashboard-container">

    <!-- Search removed from dashboard -->

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
      <div class="chart-wrapper">
        <PieChart
          :labels="Object.keys(riskDistribution)"
          :values="Object.values(riskDistribution)"
        />
      </div>
    </div>
    <div class="chart-card">
      <h3>Status Distribution</h3>
      <div class="chart-wrapper">
        <PieChart
          :labels="Object.keys(statusDistribution)"
          :values="Object.values(statusDistribution)"
        />
      </div>
    </div>
  </div>
</section>

<!-- DOMAIN ANALYTICS -->
<section class="charts-section mb-4">
  <div class="chart-row">
    <div class="chart-card">
      <h3>Domain Counts</h3>
      <div class="chart-wrapper">
        <PieChart
          :labels="Object.keys(domainCounts)"
          :values="Object.values(domainCounts)"
        />
      </div>
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
      <div class="chart-wrapper">
        <LineChart
          :labels="monthlyActivity.map(a => a.month)"
          :values="monthlyActivity.map(a => a.scanned)"
        />
      </div>
    </div>
    <div class="chart-card">
      <h3>Daily Activity</h3>
      <div class="chart-wrapper">
        <LineChart
          :labels="dailyActivity.map(a => a.day)"
          :values="dailyActivity.map(a => a.scanned)"
        />
      </div>
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
            <td>
              <span v-if="url.risk_score !== undefined && url.risk_description">{{ url.risk_score }} — {{ url.risk_description }}</span>
              <span v-else-if="url.risk_score !== undefined">{{ url.risk_score }}</span>
              <span v-else>—</span>
            </td>
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

/* Ensure chart cards align and have equal height */
.chart-row {
  align-items: stretch;
}

.chart-card {
  display: flex;
  flex-direction: column;
  /* let the card size itself but provide a reasonable default */
  min-height: 260px;
  max-height: 480px;
  overflow: hidden;
}

/* Chart wrapper ensures a fixed container for the chart component */
.chart-wrapper {
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  /* set a reasonable height that can shrink on small screens */
  min-height: 180px;
}

/* Make chart components fill their wrapper; allow chart libraries to manage aspect */
.chart-wrapper > * {
  width: 100%;
  height: 100%;
}

/* Chart wrapper: constrain visuals without forcing canvas distortion */
.chart-card canvas,
.chart-card svg {
  width: 100% !important;
  height: 100% !important;
  max-height: 360px; /* prevents charts from overflowing on large screens */
}

/* Smaller devices: stack cards vertically and reduce chart sizes */
@media (max-width: 992px) {
  .chart-card {
    min-height: 220px;
    max-height: 420px;
  }
  .chart-card canvas,
  .chart-card svg {
    max-height: 300px;
  }
}

@media (max-width: 600px) {
  .chart-row {
    flex-direction: column;
  }
  .chart-card {
    min-height: 180px;
    max-height: none;
  }
  .chart-card canvas,
  .chart-card svg {
    max-height: 220px;
  }
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
