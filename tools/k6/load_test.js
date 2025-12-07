import http from 'k6/http';
import { sleep, check } from 'k6';

// Configuration via environment variables:
// BASE_URL - base URL of the backend (default: http://127.0.0.1:8000)
// VUS - number of virtual users (default: 50)
// DURATION - duration string (default: 30s)
// AUTH_USER / AUTH_PASS - optional credentials for authenticated test
// TARGET - which endpoint to hit: 'health' or 'search' (default: health)

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';
const VUS = __ENV.VUS ? parseInt(__ENV.VUS) : 50;
const DURATION = __ENV.DURATION || '30s';
const TARGET = __ENV.TARGET || 'health';

export const options = {
  vus: VUS,
  duration: DURATION,
  // thresholds can be tuned for your expectations
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
  },
};

function loginGetToken(user, pass) {
  const url = `${BASE_URL}/auth/token`;
  const payload = `username=${encodeURIComponent(user)}&password=${encodeURIComponent(pass)}`;
  const params = { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } };
  const res = http.post(url, payload, params);
  if (res.status !== 200) {
    console.error('Login failed status', res.status, 'body', res.body);
    return null;
  }
  try {
    const j = res.json();
    return j.access_token || null;
  } catch (e) {
    console.error('Failed to parse login response', e);
    return null;
  }
}

export function setup() {
  // If credentials are provided, log in once and return token for VUs
  const user = __ENV.AUTH_USER;
  const pass = __ENV.AUTH_PASS;
  if (user && pass && TARGET === 'search') {
    const token = loginGetToken(user, pass);
    if (!token) {
      // If login failed, we still return null and subsequent requests will show failures
      return { token: null };
    }
    return { token };
  }
  return { token: null };
}

export default function (data) {
  if (TARGET === 'health') {
    const res = http.get(`${BASE_URL}/urls/health`);
    check(res, { 'health: status 200': (r) => r.status === 200 });
  } else if (TARGET === 'search') {
    const token = data.token;
    const headers = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    // randomize query a bit to avoid caching the exact same key every request
    const q = Math.random() > 0.5 ? 'phish' : 'example';
    const res = http.get(`${BASE_URL}/urls?query=${encodeURIComponent(q)}&page=1&per_page=25`, headers);
    check(res, { 'search: status 200': (r) => r.status === 200 });
  } else {
    // default to health
    const res = http.get(`${BASE_URL}/urls/health`);
    check(res, { 'health: status 200': (r) => r.status === 200 });
  }

  // small random sleep to avoid perfectly synchronized requests
  sleep(Math.random() * 1.5);
}
