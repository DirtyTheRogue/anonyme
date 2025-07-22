import React, { useState } from "react";
import API from "../services/api";
import FileDrop from "../components/FileDrop";
import Layout from "./Layout";

function Extraction() {
  const [source, setSource] = useState("");
  const [columns, setColumns] = useState([]);
  const [selectedColumn, setSelectedColumn] = useState("");
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [conditions, setConditions] = useState("");
  const [status, setStatus] = useState("");
  const [logs, setLogs] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadedFilePath, setUploadedFilePath] = useState(null);
  const [previewRows, setPreviewRows] = useState([]);

  const fetchColumns = (file) => {
    const formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:8000/read_csv", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        let cols = data.columns
        if (cols.length == 1 && typeof cols[0] === "string" && cols[0].includes(";")) {
          cols = cols[0].split(";").map((col) => col.trim());}
        console.log("Colonnes normale :", cols);
        console.log("Colonnes récupérées :", data);
        if (data.columns) {
          setColumns(cols);
          setStatus("✅ Colonnes récupérées avec succès !");
        } else {
          setStatus("❌ Erreur lors de la lecture des colonnes.");
        }
      })
      .catch((err) => {
        console.error("Erreur colonnes :", err);
        setStatus("❌ Erreur lors de la récupération des colonnes.");
      });
  };

  const fetchPreviewRows = () => {
    if (!uploadedFilePath) {
      setStatus("❗Veuillez d'abord uploader un fichier.");
      return;
    }

    const fileName = uploadedFilePath.split("/").pop();

    fetch("http://127.0.0.1:8000/extraction/preview_rows", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: fileName.includes("uploads/") ? fileName : `uploads/${fileName}`,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.preview) {
          setPreviewRows(data.preview);
          setStatus("✅ Aperçu des données chargé !");
        } else {
          setStatus("❌ Erreur lors du chargement de l’aperçu.");
        }
      })
      .catch((err) => {
        console.error("Erreur preview :", err);
        setStatus("❌ Erreur lors de la récupération de l’aperçu.");
      });
  };

  const handleFileSelect = (files) => {
    const file = files[0];
    setSelectedFiles(files);
    const formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:8000/upload/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((uploadResponse) => {
        if (uploadResponse.filepath) {
          setSource(uploadResponse.filepath);
          setUploadedFilePath(uploadResponse.filepath);
          setStatus("✅ Fichier uploadé avec succès !");
        } else {
          setStatus("❌ Erreur : filepath manquant.");
        }
      })
      .catch(() => {
        setStatus("❌ Erreur lors de l'upload.");
      });
  };

  const handlePreviewColumns = () => {
    if (!uploadedFilePath) {
      setStatus("❗Veuillez d'abord uploader un fichier.");
      return;
    }

    const file = selectedFiles[0];
    if (!file) {
      setStatus("❌ Fichier manquant pour la prévisualisation.");
      return;
    }

    fetchColumns(file);
    fetchPreviewRows();
  };

  const handleAddColumn = () => {
    if (selectedColumn && !selectedColumns.includes(selectedColumn)) {
      console.log("👉 Colonne ajoutée :", selectedColumn);
      setSelectedColumns([...selectedColumns, selectedColumn]);
    }
    setSelectedColumn("");
  };

  const handleExtraction = async () => {
    if (!uploadedFilePath) {
      setStatus("❗Veuillez charger un fichier avant de lancer l'extraction.");
      return;
    }

    const fileName = uploadedFilePath.split("/").pop();
    if (!fileName) {
      setStatus("❌ Nom de fichier invalide.");
      return;
    }

    try {
      setStatus("⏳ Extraction en cours...");

      const filePath = fileName.includes("uploads/") ? fileName : `uploads/${fileName}`;
      console.log("✅ Colonnes envoyées au backend :", selectedColumns);
      const payload = {
        source: filePath,
        columns: selectedColumns.join(","),
        conditions,
      };

      const response = await fetch("http://127.0.0.1:8000/extraction/run/extraction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erreur lors de l'extraction.");
      }

      const result = await response.json();
      setLogs(result.logs || []);
      setStatus("✅ Extraction terminée avec succès !");
    } catch (error) {
      console.error("Erreur :", error);
      setStatus("❌ Erreur lors de l'extraction.");
    }
  };

  const getStatusStyle = () => {
    if (status.includes("✅")) return { color: "#4BC4BD" };
    if (status.includes("❌") || status.includes("❗")) return { color: "#B10031" };
    if (status.includes("⏳")) return { color: "#223E55" };
    return {};
  };

  const inputStyle = {
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    width: "100%",
    marginTop: "5px",
    marginBottom: "15px",
    fontFamily: "Segoe UI",
  };

  const labelStyle = {
    fontWeight: "bold",
    fontFamily: "Segoe UI",
  };

  const buttonStyle = {
    padding: "12px 20px",
    backgroundColor: "#B10031",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "bold",
    marginTop: "10px",
  };

  return (
    <Layout>
      <h1 style={{ fontFamily: "Georgia", fontSize: "24px", marginBottom: "20px" }}>
        Module d’Extraction
      </h1>

      <FileDrop onFileSelect={handleFileSelect} />

      <button
        type="button"
        onClick={handlePreviewColumns}
        style={{ ...buttonStyle, backgroundColor: "#002060", marginTop: "20px" }}
      >
         Prévisualiser les Colonnes Disponibles
      </button>

      {previewRows.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3 style={{ fontFamily: "Georgia" }}> Aperçu du Fichier (3 premières lignes)</h3>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                {Object.keys(previewRows[0]).map((col, index) => (
                  <th key={index} style={{ border: "1px solid #ccc", padding: "8px", backgroundColor: "#f2f2f2" }}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewRows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {Object.values(row).map((val, colIndex) => (
                    <td key={colIndex} style={{ border: "1px solid #ccc", padding: "8px" }}>
                      {val}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginTop: "30px" }}>
        <label style={labelStyle}>Source de données :</label>
        <input
          type="text"
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="Chemin du fichier"
          style={inputStyle}
        />

        <label style={labelStyle}>Colonnes à extraire :</label>
        <select
          value={selectedColumn}
          onChange={(e) => setSelectedColumn(e.target.value)}
          style={inputStyle}
        >
          <option value="">-- Sélectionner une colonne --</option>
          {columns.map((col) => (
            <option key={col} value={col}>
              {col}
            </option>
          ))}
        </select>

        {selectedColumn && (
          <button
            onClick={handleAddColumn}
            style={{ ...buttonStyle, backgroundColor: "#4BC4BD" }}
          >
            ➕ Ajouter cette colonne
          </button>
        )}

        {selectedColumns.length > 0 && (
          <ul style={{ paddingLeft: "20px", marginTop: "10px" }}>
            {selectedColumns.map((col, index) => (
              <li key={index}>{col}</li>
            ))}
          </ul>
        )}

        <label style={labelStyle}>Conditions :</label>
        <input
          type="text"
          value={conditions}
          onChange={(e) => setConditions(e.target.value)}
          placeholder="ex: age > 30"
          style={inputStyle}
        />

        <button
          type="button"
          style={buttonStyle}
          onClick={handleExtraction}
          disabled={!source}
        >
           Lancer l'Extraction
        </button>

        <p style={{ ...getStatusStyle(), marginTop: "15px", fontWeight: "bold" }}>
          {status}
        </p>
      </div>

      {logs.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3 style={{ fontFamily: "Georgia" }}> Logs :</h3>
          <ul style={{ paddingLeft: "20px" }}>
            {logs.map((log, index) => (
              <li key={index}>{log}</li>
            ))}
          </ul>
        </div>
      )}
    </Layout>
  );
}

export default Extraction;
