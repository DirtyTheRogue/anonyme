import React, { useState } from "react";
import { Link } from "react-router-dom"; 
import API from "../services/api";
import Layout from "./Layout";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    API.post("/login", { username, password })
      .then((response) => {
        console.log("Connexion réussie:", response.data);
        window.location.href = "/dashboard";
      })
      .catch(() => {
        setError("❌ Erreur de connexion. Veuillez vérifier vos identifiants.");
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
          Connexion
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

        <button
          onClick={handleLogin}
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "#B10031",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
            marginBottom: "10px"
          }}
        >
           Se connecter
        </button>

        {error && (
          <p style={{ color: "#B10031", fontWeight: "bold", textAlign: "center" }}>
            {error}
          </p>
        )}

        <p style={{ textAlign: "center", fontSize: "14px", marginTop: "15px" }}>
          Pas de compte ?{" "}
          <Link to="/register" style={{ color: "#002060", fontWeight: "bold" }}>
            Créer un compte
          </Link>
        </p>
      </div>
    </Layout>
  );
}

export default Login;
