// src/services/csvService.js
import axios from "axios";

// Use relative API path so Vite dev server can proxy requests in development
const API = "/urls";

export async function exportCSV() {
    const response = await axios.get(`${API}/export`, {
        responseType: "blob" // important for downloading files
    });
    return response.data;
}

export async function importCSV(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(`${API}/import`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
    return response.data;
}
