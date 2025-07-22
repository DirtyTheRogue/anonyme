import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000", 
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,  // Ajouté pour s'assurer que les cookies sont bien envoyés
});

export default API;
