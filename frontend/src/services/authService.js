// src/services/authService.js
import axios from "axios";

const TOKEN_KEY = "access_token";
const USERNAME_KEY = "username";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    localStorage.removeItem(TOKEN_KEY);
    delete axios.defaults.headers.common["Authorization"];
  }
}

export function getUsername() {
  return localStorage.getItem(USERNAME_KEY);
}

export function setUsername(username) {
  if (username) {
    localStorage.setItem(USERNAME_KEY, username);
  } else {
    localStorage.removeItem(USERNAME_KEY);
  }
}

export function login(username, password) {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);
  return axios
    .post("/auth/token", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
    .then((res) => {
      const token = res.data && res.data.access_token;
      setToken(token);
      // persist username so header can display it
      setUsername(username);
      // fetch current user profile (get is_admin) but don't block login
      fetchCurrentUser().catch(() => {});
      return res.data;
    });
}

export function logout() {
  setToken(null);
  setUsername(null);
}

export function isAuthenticated() {
  return !!getToken();
}

export function attachAuthHeader() {
  const token = getToken();
  if (token) {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common["Authorization"];
  }
}

// Register global axios interceptors for centralized auth error handling
export function setupInterceptors() {
  // Request interceptor: ensure auth header is present
  axios.interceptors.request.use((cfg) => {
    const t = getToken();
    if (t) cfg.headers = { ...cfg.headers, Authorization: `Bearer ${t}` };
    return cfg;
  });

  // Response interceptor: handle 401 and 403 centrally
  axios.interceptors.response.use(
    (resp) => resp,
    (error) => {
      if (!error || !error.response) return Promise.reject(error);
      const status = error.response.status;
      const reqUrl = error.config && (error.config.url || error.config.baseURL + (error.config.url || ''));
      if (status === 401) {
        // If the 401 originated from the auth endpoints (login/me), don't auto-logout here
        // because that can cause a redirect loop during the login flow. Only perform
        // a global logout when protected endpoints return 401.
        if (reqUrl && reqUrl.includes('/auth')) {
          return Promise.reject(error);
        }
        // Unauthorized: clear token and redirect to login
        setToken(null);
        setUsername(null);
        localStorage.removeItem('is_admin');
        // Use full-page navigation to avoid circular router imports
        window.location.href = '/login';
        return Promise.reject(error);
      }
      if (status === 403) {
        // Forbidden: show an informative message
        try {
          alert('Access denied: you do not have permission to perform this action.');
        } catch (e) {}
        return Promise.reject(error);
      }
      return Promise.reject(error);
    }
  );
}

// When attaching header on app start, also try to populate current user info
export function initAuthOnStartup() {
  attachAuthHeader();
  const t = getToken();
  if (t) {
    // try to fetch current user to populate is_admin flag; failure is non-fatal
    fetchCurrentUser().catch(() => {});
  }
}

export async function fetchCurrentUser() {
  try {
    const res = await axios.get('/auth/me');
    if (res && res.data) {
      setUsername(res.data.username || getUsername());
      // store admin flag
      if (res.data.is_admin) {
        localStorage.setItem('is_admin', '1');
      } else {
        localStorage.removeItem('is_admin');
      }
      return res.data;
    }
  } catch (err) {
    // token might be invalid or network error; clear admin flag
    localStorage.removeItem('is_admin');
    throw err;
  }
}

export function isAdmin() {
  return localStorage.getItem('is_admin') === '1';
}
