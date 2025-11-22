// src/services/urlService.js
import axios from "axios";

const API = "http://localhost:8000/urls";

export async function getUrls() {
    const response = await axios.get(API);
    return response.data;
}

export async function addUrl(data) {
    const response = await axios.post(API, data);
    return response.data;
}

export async function updateUrl(id, data) {
    const response = await axios.put(`${API}/${id}`, data);
    return response.data;
}

export async function deleteUrl(id) {
    const response = await axios.delete(`${API}/${id}`);
    return response.data;
}
