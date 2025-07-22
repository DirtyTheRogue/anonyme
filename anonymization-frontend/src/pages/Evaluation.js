import React, { useState } from "react";
import API from "../services/api";
import Layout from "./Layout";

function Evaluation() {
  const [originalFile, setOriginalFile] = useState("");
  const [anonymizedFile, setAnonymizedFile] = useState("");
  const [metrics, setMetrics] = useState("");
  const [status, setStatus] = useState("");
  const [results, setResults] = useState([]);
  const [logs, setLogs] = useState([]);
  const [showChart, setShowChart] = useState(false);

  const handleEvaluation = () => {
    if (!originalFile || !anonymizedFile || !metrics) {
      setStatus("❗ Veuillez remplir tous les champs avant de lancer l'évaluation.");
      return;
    }

    setStatus("⏳ Évaluation en cours...");
    setShowChart(false);

    const payload = {
      originalFile: originalFile.trim(),
      anonymizedFile: anonymizedFile.trim(),
      metrics: metrics.trim(),
    };

    API.post("/evaluation/run/evaluation", payload)
      .then((response) => {
        setStatus("✅ Évaluation terminée avec succès !");
        setResults(response.data.results || []);
        setLogs(response.data.logs || []);
        setShowChart(true);
      })
      .catch((error) => {
        setStatus("❌ Erreur lors de l'évaluation.");
        console.error("Erreur :", error);
      });
  };

  return (
    <Layout>
      <div style={{
        maxWidth: "900px",
        margin: "40px auto",
        backgroundColor: "#fff",
        padding: "30px",
        borderRadius: "12px",
        boxShadow: "0 0 20px rgba(0,0,0,0.1)",
        fontFamily: "Segoe UI"
      }}>
        <h1 style={{ fontFamily: "Georgia", fontSize: "26px", marginBottom: "25px" }}>
           Module d'Évaluation
        </h1>

        <form>
          <label style={{ fontWeight: "bold" }}>Fichier original :</label>
          <input
            type="text"
            value={originalFile}
            onChange={(e) => setOriginalFile(e.target.value)}
            placeholder="Nom du fichier original"
            style={{
              width: "100%", padding: "10px", marginBottom: "15px", borderRadius: "6px", border: "1px solid #ccc"
            }}
          />

          <label style={{ fontWeight: "bold" }}>Fichier anonymisé :</label>
          <input
            type="text"
            value={anonymizedFile}
            onChange={(e) => setAnonymizedFile(e.target.value)}
            placeholder="Nom du fichier anonymisé"
            style={{
              width: "100%", padding: "10px", marginBottom: "15px", borderRadius: "6px", border: "1px solid #ccc"
            }}
          />

          <label style={{ fontWeight: "bold" }}>Métriques à utiliser :</label>
          <input
            type="text"
            value={metrics}
            onChange={(e) => setMetrics(e.target.value)}
            placeholder="ex: précision, recall"
            style={{
              width: "100%", padding: "10px", marginBottom: "20px", borderRadius: "6px", border: "1px solid #ccc"
            }}
          />

          <button
            type="button"
            onClick={handleEvaluation}
            style={{
              padding: "12px 20px",
              backgroundColor: "#4BC4BD",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              fontWeight: "bold",
              cursor: "pointer",
              width: "100%"
            }}
          >
             Lancer l'Évaluation
          </button>
        </form>

        <p style={{ marginTop: "20px", fontWeight: "bold", color: status.includes("✅") ? "#4BC4BD" : status.includes("❌") || status.includes("❗") ? "#B10031" : "#223E55" }}>
          {status}
        </p>

        {showChart && (
          <div style={{ marginTop: "30px" }}>
            <h3 style={{ fontFamily: "Georgia" }}> Résumé visuel (fictif)</h3>
            <div style={{
              height: "200px",
              background: "linear-gradient(to right, #4BC4BD 70%, #B10031 30%)",
              borderRadius: "8px",
              boxShadow: "inset 0 0 10px rgba(0,0,0,0.1)",
              marginTop: "10px"
            }}>
              {/* Faux graphique de répartition */}
            </div>
          </div>
        )}

        {results.length > 0 && (
          <div style={{ marginTop: "30px" }}>
            <h3 style={{ fontFamily: "Georgia" }}> Résultats</h3>
            <ul style={{ paddingLeft: "20px" }}>
              {results.map((result, index) => (
                <li key={index}>{result}</li>
              ))}
            </ul>
          </div>
        )}

        {logs.length > 0 && (
          <div style={{ marginTop: "30px" }}>
            <h3 style={{ fontFamily: "Georgia" }}> Logs</h3>
            <ul style={{ paddingLeft: "20px" }}>
              {logs.map((log, index) => (
                <li key={index}>{log}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default Evaluation;
