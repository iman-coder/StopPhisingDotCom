// src/services/csvService.js
import axios from "axios";

const API = "http://localhost:8000/urls";

export async function exportCSV() {
    const response = await axios.get(`${API}/export`, {
        responseType: "blob" // important for downloading files
    });
    return response.data;
}

export async function importCSV(file) {
    const formData = new FormData();
    formData.append("file", file);

    return axios.post(`${API}/import`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
}
