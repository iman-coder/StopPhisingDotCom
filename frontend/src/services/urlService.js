// src/services/urlService.js
import axios from "axios";
import { attachAuthHeader } from "./authService";

// Ensure Authorization header is attached if token present
attachAuthHeader();

// Use API prefix to avoid SPA route collisions; keep trailing slash to avoid 307 redirects
const API = "/api/urls/";

export async function getUrls() {
    // Accept parameters object: { query, page, per_page }
    // If called with no args, simply fetch default list (server returns paginated response)
    const response = await axios.get(API, { params: arguments[0] || {} });
    return response.data;
}

export async function addUrl(data) {
    const response = await axios.post(API, data);
    return response.data;
}

export async function updateUrl(id, data) {
    const response = await axios.put(`${API}${id}`, data);
    return response.data;
}

export async function deleteUrl(id) {
    const response = await axios.delete(`${API}${id}`);
    return response.data;
}

export async function deleteAll() {
    const response = await axios.delete(API);
    return response.data;
}
