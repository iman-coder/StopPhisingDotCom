// dashboardService.js
import axios from "axios";

const API = "http://localhost:8000/dashboard";
const USE_MOCKS = true; // ⬅ Switch to false to use real backend

/* -------------------------------------------------------
 * MOCK DATA DEFINITIONS
 * ----------------------------------------------------- */
const mockGlobalMetrics = {
    total_urls: 120,
    safe: 80,
    suspicious: 25,
    malicious: 15,
};

const mockRiskDistribution = {
    safe: 80,
    suspicious: 25,
    malicious: 15,
};

const mockStatusDistribution = {
    scanned: 100,
    pending: 15,
    failed: 5,
};

const mockDomainCounts = {
    "google.com": 20,
    "facebook.com": 10,
    "paypal.com": 5,
    "github.com": 3,
    "apple.com": 2,
};

const mockTopRiskyDomains = [
    { domain: "paypal.com", count: 5 },
    { domain: "unknownsite.ru", count: 4 },
    { domain: "random-phish.com", count: 3 },
];

const mockMonthlyActivity = [
    { month: "2025-01", scanned: 20, suspicious: 5, malicious: 2 },
    { month: "2025-02", scanned: 30, suspicious: 8, malicious: 3 },
    { month: "2025-03", scanned: 40, suspicious: 10, malicious: 5 },
];

const mockDailyActivity = [
    { day: "2025-03-01", scanned: 3, suspicious: 0, malicious: 0 },
    { day: "2025-03-02", scanned: 5, suspicious: 1, malicious: 0 },
    { day: "2025-03-03", scanned: 7, suspicious: 1, malicious: 1 },
];

const mockTopRiskyUrls = [
    { id: 1, url: "http://evil.com", risk: "malicious" },
    { id: 2, url: "http://phish.co", risk: "malicious" },
    { id: 3, url: "http://weird.xyz", risk: "suspicious" },
];

const mockMostRecentUrls = [
    { id: 10, url: "http://google.com", status: "safe" },
    { id: 11, url: "http://suspicious.net", status: "suspicious" },
    { id: 12, url: "http://randomsite.com", status: "safe" },
];

const mockRecentEvents = [
    { id: 1, action: "scanned", url: "http://google.com", timestamp: "2025-03-01 12:00" },
    { id: 2, action: "added", url: "http://evil.com", timestamp: "2025-03-01 13:00" },
    { id: 3, action: "deleted", url: "http://oldsite.net", timestamp: "2025-03-01 14:00" },
];

const mockSearchResults = [
    { id: 2, url: "http://phish.co", status: "malicious" },
    { id: 3, url: "http://paypal.com.fake", status: "suspicious" },
];

/* -------------------------------------------------------
 * HELPERS
 * ----------------------------------------------------- */
async function mock(data) {
    return new Promise(resolve =>
        setTimeout(() => resolve(data), 300) // simulate network delay
    );
}

/* -------------------------------------------------------
 * 1. GLOBAL METRICS
 * ----------------------------------------------------- */
export async function getGlobalMetrics() {
    if (USE_MOCKS) return mock(mockGlobalMetrics);
    return axios.get(`${API}/metrics`).then(res => res.data);
}

/* -------------------------------------------------------
 * 2. RISK / STATUS DISTRIBUTION
 * ----------------------------------------------------- */
export async function getRiskDistribution() {
    if (USE_MOCKS) return mock(mockRiskDistribution);
    return axios.get(`${API}/risk-distribution`).then(res => res.data);
}

export async function getStatusDistribution() {
    if (USE_MOCKS) return mock(mockStatusDistribution);
    return axios.get(`${API}/status-distribution`).then(res => res.data);
}

/* -------------------------------------------------------
 * 3. DOMAIN ANALYTICS
 * ----------------------------------------------------- */
export async function getDomainCounts() {
    if (USE_MOCKS) return mock(mockDomainCounts);
    return axios.get(`${API}/domains`).then(res => res.data);
}

export async function getTopRiskyDomains(limit = 5) {
    if (USE_MOCKS) return mock(mockTopRiskyDomains.slice(0, limit));
    return axios.get(`${API}/domains/top?limit=${limit}`).then(res => res.data);
}

/* -------------------------------------------------------
 * 4. TIME SERIES
 * ----------------------------------------------------- */
export async function getMonthlyActivity() {
    if (USE_MOCKS) return mock(mockMonthlyActivity);
    return axios.get(`${API}/activity/monthly`).then(res => res.data);
}

export async function getDailyActivity() {
    if (USE_MOCKS) return mock(mockDailyActivity);
    return axios.get(`${API}/activity/daily`).then(res => res.data);
}

/* -------------------------------------------------------
 * 5. TOP LISTS
 * ----------------------------------------------------- */
export async function getTopRiskyUrls(limit = 10) {
    if (USE_MOCKS) return mock(mockTopRiskyUrls.slice(0, limit));
    return axios.get(`${API}/urls/top?limit=${limit}`).then(res => res.data);
}

export async function getMostRecentUrls(limit = 10) {
    if (USE_MOCKS) return mock(mockMostRecentUrls.slice(0, limit));
    return axios.get(`${API}/urls/recent?limit=${limit}`).then(res => res.data);
}

/* -------------------------------------------------------
 * 6. ACTIVITY FEED
 * ----------------------------------------------------- */
export async function getRecentEvents(limit = 20) {
    if (USE_MOCKS) return mock(mockRecentEvents.slice(0, limit));
    return axios.get(`${API}/events?limit=${limit}`).then(res => res.data);
}

/* -------------------------------------------------------
 * 7. SEARCH
 * ----------------------------------------------------- */
export async function searchDashboard(query) {
    if (USE_MOCKS) return mock(mockSearchResults);
    return axios.get(`${API}/search?q=${query}`).then(res => res.data);
}
