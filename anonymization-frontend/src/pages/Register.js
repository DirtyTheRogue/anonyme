import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import API from "../services/api";
import Layout from "./Layout";

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate(); 

  const handleRegister = () => {
    if (password !== confirmPassword) {
      setError("❗ Les mots de passe ne correspondent pas.");
      setSuccess("");
      return;
    }

    API.post("/register", { username, password })
      .then((response) => {
        setSuccess("✅ Compte créé avec succès !");
        setError("");
        console.log("Compte créé :", response.data);
        setTimeout(() => navigate("/login"), 2000); 
      })
      .catch((error) => {
        setSuccess("");
        setError(error.response?.data?.detail || "❌ Erreur lors de l'inscription.");
        console.error("Erreur lors de l'inscription :", error);
      });
  };

  return (
    <Layout>
      <div style={{
        maxWidth: "400px",
        margin: "40px auto",
        backgroundColor: "#fff",
        padding: "30px",
        borderRadius: "12px",
        boxShadow: "0 0 15px rgba(0,0,0,0.1)",
        fontFamily: "Segoe UI"
      }}>
        <h2 style={{ fontFamily: "Georgia", textAlign: "center", marginBottom: "20px" }}>
          Créer un compte
        </h2>

        <input
          type="text"
          placeholder="Nom d'utilisateur"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{
            width: "100%",
            padding: "10px",
            marginBottom: "15px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />

        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            width: "100%",
            padding: "10px",
            marginBottom: "15px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />

        <input
          type="password"
          placeholder="Confirmer le mot de passe"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          style={{
            width: "100%",
            padding: "10px",
            marginBottom: "15px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />

        <button
          onClick={handleRegister}
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "#4BC4BD",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer"
          }}
        >
           Créer un compte
        </button>

        {error && (
          <p style={{ color: "#B10031", fontWeight: "bold", textAlign: "center", marginTop: "15px" }}>
            {error}
          </p>
        )}
        {success && (
          <p style={{ color: "#4BC4BD", fontWeight: "bold", textAlign: "center", marginTop: "15px" }}>
            {success}
          </p>
        )}
      </div>
    </Layout>
  );
}

export default Register;
