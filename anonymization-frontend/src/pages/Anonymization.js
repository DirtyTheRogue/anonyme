import React, { useState, useEffect } from "react";
import API from "../services/api";
import Layout from "./Layout";

function Anonymization() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [availableColumns, setAvailableColumns] = useState([]);
  const [selectedColumn, setSelectedColumn] = useState("");
  const [rules, setRules] = useState([]);
  const [selectedRule, setSelectedRule] = useState("");
  const [selections, setSelections] = useState([]);
  const [status, setStatus] = useState("");
  const [logs, setLogs] = useState([]);
  const [previewRows, setPreviewRows] = useState([]);


  useEffect(() => {
    API.get("/tables")
      .then((response) => {
        if (response.data.tables && Array.isArray(response.data.tables)) {
          setTables(response.data.tables);
        } else {
          setTables([]);
        }
      })
      .catch(() => setTables([]));

    API.get("/anonymization/rules")
      .then((response) => {
        if (response.data.rules && Array.isArray(response.data.rules)) {
          setRules(response.data.rules);
        } else {
          setRules([]);
        }
      })
      .catch(() => setRules([]));
  }, []);

  useEffect(() => {
    if (!selectedTable) return setAvailableColumns([]);

    API.get(`/tables/${selectedTable}/columns`)
      .then((response) => {
        if (response.data.columns && Array.isArray(response.data.columns)) {
          setAvailableColumns(response.data.columns);
        } else {
          setAvailableColumns([]);
        }
      })
      .catch(() => setAvailableColumns([]));
  }, [selectedTable]);

  const handleAddSelection = () => {
    if (!selectedTable || !selectedColumn || !selectedRule) {
      setStatus("❗Veuillez sélectionner une table, une colonne et une règle.");
      return;
    }

    setSelections([...selections, { table: selectedTable, column: selectedColumn, rule: selectedRule }]);
    setSelectedColumn("");
    setSelectedRule("");
  };

  const handleAnonymization = () => {
    if (selections.length === 0) {
      setStatus("❗Veuillez ajouter au moins une sélection.");
      return;
    }

    setStatus("⏳ Anonymisation en cours...");

    const payload = {
      table: selectedTable,
      rules: selections.map((s) => ({
        table: s.table,
        column: s.column,
        moteur: s.rule,
      })),
    };

    API.post("/anonymization/run/anonymize", payload, {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    })
      .then((response) => {
        if (response.data.status === "success") {
          setStatus("✅ Anonymisation terminée avec succès !");
          setLogs(response.data.logs || []);
          setPreviewRows(response.data.preview || []);
          setSelections([]);
          setSelectedTable("");
          setSelectedColumn("");
          setSelectedRule("");
        } else {
          setStatus("❌ Une erreur est survenue.");
        }
      })
      .catch(() => {
        setStatus("❌ Erreur lors de l'anonymisation.");
      });
  };

  const selectStyle = {
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    width: "100%",
    fontFamily: "Segoe UI",
  };

  const buttonStyle = {
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    fontWeight: "bold",
    cursor: "pointer",
    marginTop: "10px",
  };

  const statusStyle = {
    marginTop: "15px",
    fontWeight: "bold",
    color: status.includes("✅")
      ? "#4BC4BD"
      : status.includes("❌") || status.includes("❗")
      ? "#B10031"
      : "#223E55",
  };

  return (
    <Layout>
      <h1 style={{ fontFamily: "Georgia", fontSize: "24px", marginBottom: "20px" }}>
        Module d'Anonymisation
      </h1>

      {/* Table */}
      <div>
        <label style={{ fontWeight: "bold" }}>Choisir une Table :</label>
        <select
          style={selectStyle}
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
        >
          <option value="">-- Sélectionner une table --</option>
          {tables.map((table) => (
            <option key={table} value={table}>
              {table}
            </option>
          ))}
        </select>
      </div>

      {/* Colonne */}
      {selectedTable && (
        <div>
          <label style={{ fontWeight: "bold" }}>Choisir une Colonne :</label>
          <select
            style={selectStyle}
            value={selectedColumn}
            onChange={(e) => setSelectedColumn(e.target.value)}
          >
            <option value="">-- Sélectionner une colonne --</option>
            {availableColumns.map((col) => (
              <option key={col} value={col}>
                {col}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Règle */}
      {selectedColumn && (
        <div>
          <label style={{ fontWeight: "bold" }}>Choisir une Règle :</label>
          <select
            style={selectStyle}
            value={selectedRule}
            onChange={(e) => setSelectedRule(e.target.value)}
          >
            <option value="">-- Sélectionner une règle --</option>
            {rules.map((rule) => (
              <option key={rule} value={rule}>
                {rule}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Ajouter */}
      {selectedRule && (
        <button
          style={{ ...buttonStyle, backgroundColor: "#002060", color: "#fff" }}
          onClick={handleAddSelection}
        >
          ➕ Ajouter la règle
        </button>
      )}

      {/* Sélections */}
      {selections.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3 style={{ fontFamily: "Georgia" }}> Sélections :</h3>
          <ul style={{ paddingLeft: "20px" }}>
            {selections.map((sel, index) => (
              <li key={index}>
                {sel.table} - {sel.column} - {sel.rule}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Lancer anonymisation */}
      <button
        style={{ ...buttonStyle, backgroundColor: "#B10031", color: "#fff" }}
        onClick={handleAnonymization}
      >
         Lancer l'anonymisation
      </button>

      {/* Status */}
      <p style={statusStyle}>{status}</p>

      {/* Logs */}
      {logs.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3 style={{ fontFamily: "Georgia" }}> Logs :</h3>
          <ul style={{ paddingLeft: "20px" }}>
            {logs.map((log, index) => (
              <li key={index}>{log}</li>
            ))}
          </ul>
        </div>
      )}
      {/* Preview Rows */}
      {previewRows.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3 style={{ fontFamily: "Georgia" }}> Apercu des Colonnes :</h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                {Object.keys(previewRows[0]).map((col,index) => (
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
      )
}
    </Layout>
  );
}

export default Anonymization;
