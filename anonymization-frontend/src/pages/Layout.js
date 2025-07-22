import React from "react";
import { Link } from "react-router-dom";

const layoutStyles = {
  container: {
    fontFamily: "Segoe UI, sans-serif",
    backgroundColor: "#F2F2F2",
    minHeight: "100vh",
  },
  header: {
    backgroundColor: "#002060",
    color: "#fff",
    padding: "10px 20px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  logo: {
    height: "60px",
  },
  navLinks: {
    display: "flex",
    gap: "20px",
  },
  navLink: {
    color: "#fff",
    textDecoration: "none",
    fontWeight: "bold",
  },
  content: {
    maxWidth: "1000px",
    margin: "30px auto",
    backgroundColor: "#fff",
    padding: "30px",
    borderRadius: "10px",
    boxShadow: "0 0 20px rgba(0,0,0,0.1)",
  },
  footer: {
    textAlign: "center",
    padding: "15px",
    fontSize: "12px",
    color: "#595959",
  },
};

function Layout({ children }) {
  return (
    <div style={layoutStyles.container}>
      <header style={layoutStyles.header}>
        <img
          src="https://imgur.com/GSvUvqw.png" 
          alt="Nexialog Logo"
          style={layoutStyles.logo}
        />
        <nav style={layoutStyles.navLinks}>
          <Link to="/dashboard" style={layoutStyles.navLink}>Dashboard</Link>
          <Link to="/anonymization" style={layoutStyles.navLink}>Anonymisation</Link>
          <Link to="/extraction" style={layoutStyles.navLink}>Extraction</Link>
          <Link to="/evaluation" style={layoutStyles.navLink}>Évaluation</Link>
        </nav>
      </header>

      <main style={layoutStyles.content}>
        {children}
      </main>

      <footer style={layoutStyles.footer}>
        © {new Date().getFullYear()} Nexialog Consulting – Projet d’anonymisation
      </footer>
    </div>
  );
}

export default Layout;
