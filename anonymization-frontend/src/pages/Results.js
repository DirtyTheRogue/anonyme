import React, { useState, useEffect } from "react";
import API from "../services/api";
import Layout from "./Layout";

function Results() {
  const [results, setResults] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    API.get("/results")
      .then((response) => {
        setResults(response.data.results || []);
        setLogs(response.data.logs || []);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des résultats :", error);
      });
  }, []);

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
           Résultats
        </h1>

        <div style={{ marginBottom: "30px" }}>
          <h2 style={{ fontFamily: "Georgia", fontSize: "20px", color: "#002060" }}>
             Fichiers disponibles :
          </h2>
          {results.length > 0 ? (
            <ul style={{ paddingLeft: "20px" }}>
              {results.map((file, index) => (
                <li key={index} style={{ marginBottom: "10px" }}>
                  <span style={{ fontWeight: "bold" }}>{file.name}</span> –{" "}
                  <a href={file.url} download style={{ color: "#4BC4BD", fontWeight: "bold" }}>
                    Télécharger
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ fontStyle: "italic", color: "#595959" }}>
              Aucun résultat disponible pour le moment.
            </p>
          )}
        </div>

        <div>
          <h2 style={{ fontFamily: "Georgia", fontSize: "20px", color: "#B10031" }}>
             Logs :
          </h2>
          {logs.length > 0 ? (
            <ul style={{ paddingLeft: "20px" }}>
              {logs.map((log, index) => (
                <li key={index} style={{ marginBottom: "8px" }}>{log}</li>
              ))}
            </ul>
          ) : (
            <p style={{ fontStyle: "italic", color: "#595959" }}>
              Aucun log disponible.
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default Results;
