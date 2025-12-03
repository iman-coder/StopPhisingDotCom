// src/services/urlService.js
import axios from "axios";
import { attachAuthHeader } from "./authService";

// Ensure Authorization header is attached if token present
attachAuthHeader();

// Use relative path with trailing slash to avoid 307 redirects from FastAPI
const API = "/urls/";

export async function getUrls() {
    const response = await axios.get(API);
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
