import React, { useState } from "react";
import API from "../services/api";
import Layout from "./Layout";

function Dashboard() {
  const [anonymizeStatus, setAnonymizeStatus] = useState("");
  const [testStatus, setTestStatus] = useState("");

  // const handleAnonymize = () => {
  //   setAnonymizeStatus("⏳ Anonymisation en cours...");
  //   API.post("/run/anonymize_all")
  //     .then((response) => {
  //       setAnonymizeStatus("✅ Anonymisation terminée !");
  //       console.log("Anonymization response:", response.data);
  //     })
  //     .catch((error) => {
  //       setAnonymizeStatus("❌ Erreur lors de l'anonymisation.");
  //       console.error("Erreur lors de l'anonymisation :", error);
  //     });
  // };

  const handleTest = () => {
    setTestStatus("⏳ Test en cours...");
    API.post("/reidentification/run")
      .then((response) => {
        setTestStatus("✅ Test terminé !");
        console.log("Test response:", response.data);
      })
      .catch((error) => {
        setTestStatus("❌ Erreur lors du test.");
        console.error("Erreur lors du test :", error);
      });
  };

  const getStatusStyle = (status) => {
    if (status.includes("⏳")) return { color: "#223E55" };
    if (status.includes("✅")) return { color: "#4BC4BD" };
    if (status.includes("❌")) return { color: "#B10031" };
    return {};
  };

  const buttonStyle = {
    padding: "12px 20px",
    borderRadius: "8px",
    fontWeight: "bold",
    border: "none",
    cursor: "pointer",
    transition: "all 0.3s",
  };

  return (
    <Layout>
  <h1 style={{ fontFamily: "Georgia", fontSize: "24px", marginBottom: "30px" }}>
    Tableau de Bord
  </h1>

  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>
    {/* Module Anonymisation */}
    <div style={{
      backgroundColor: "#fff",
      borderRadius: "10px",
      padding: "20px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      borderTop: "5px solid #B10031"
    }}>
      <h2 style={{ fontFamily: "Georgia", fontSize: "18px" }}>Anonymisation</h2>
      <p style={{ fontFamily: "Segoe UI", fontSize: "14px" }}>
        Sélectionner les colonnes sensibles et appliquer des règles d’anonymisation adaptées.
      </p>
      <a
      href="/anonymization"
        style={{
          display: "inline-block",
          marginTop: "10px",
          color: "#B10031",
          fontWeight: "bold",
          textDecoration: "none"
        }}
      >
         Acceder au module d'anonymisation
      </a>
      <p style={{ ...getStatusStyle(anonymizeStatus), marginTop: "10px" }}>{anonymizeStatus}</p>
    </div>

    {/* Module Extraction */}
    <div style={{
      backgroundColor: "#fff",
      borderRadius: "10px",
      padding: "20px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      borderTop: "5px solid #002060"
    }}>
      <h2 style={{ fontFamily: "Georgia", fontSize: "18px" }}>Extraction</h2>
      <p style={{ fontFamily: "Segoe UI", fontSize: "14px" }}>
        Extraire des sous-ensembles de données selon des règles métiers.
      </p>
      <a
        href="/extraction"
        style={{
          display: "inline-block",
          marginTop: "10px",
          color: "#002060",
          fontWeight: "bold",
          textDecoration: "none"
        }}
      >
         Accéder au module
      </a>
    </div>

    {/* Module Évaluation */}
    <div style={{
      backgroundColor: "#fff",
      borderRadius: "10px",
      padding: "20px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      borderTop: "5px solid #4BC4BD"
    }}>
      <h2 style={{ fontFamily: "Georgia", fontSize: "18px" }}>Évaluation</h2>
      <p style={{ fontFamily: "Segoe UI", fontSize: "14px" }}>
        Tester les risques de réidentification sur les données anonymisées.
      </p>
      <a
        href ="/evaluation"
        style={{
          display: "inline-block",
          marginTop: "10px",
          textDecoration: "none",
          color: "#4BC4BD",
          fontWeight: "bold",
        }}
      >
         Acceder au module d'evaluation
      </a>
      <p style={{ ...getStatusStyle(testStatus), marginTop: "10px" }}>{testStatus}</p>
    </div>

    {/* Résultats */}
    <div style={{
      backgroundColor: "#fff",
      borderRadius: "10px",
      padding: "20px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      borderTop: "5px solid #595959"
    }}>
      <h2 style={{ fontFamily: "Georgia", fontSize: "18px" }}>Résultats</h2>
      <p style={{ fontFamily: "Segoe UI", fontSize: "14px" }}>
        Consulter les fichiers anonymisés, extraits ou les journaux des opérations.
      </p>
      <a
        href="/results"
        style={{
          display: "inline-block",
          marginTop: "10px",
          color: "#595959",
          fontWeight: "bold",
          textDecoration: "none"
        }}
      >
         Voir les résultats
      </a>
    </div>
  </div>
</Layout>

  );
}

export default Dashboard;
