import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Extraction from "./pages/Extraction";
import Anonymization from "./pages/Anonymization";
import Evaluation from "./pages/Evaluation";
import Results from "./pages/Results";
import Register from "./pages/Register";
import FileDrop from "./components/FileDrop";



function App() {
  console.log("App component rendered");
  return (
    <Router>
      <Routes>
        {/* Redirection par défaut */}
        <Route path="/" element={<Navigate to="/login" />} />
        {/* Pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/extraction" element={<Extraction />} />
        <Route path="/anonymization" element={<Anonymization />} />
        <Route path="/evaluation" element={<Evaluation />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  );
}

export default App;
