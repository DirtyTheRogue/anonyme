import os
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_run_extraction(tmp_path):
    test_csv = tmp_path / "test_data.csv"
    test_df = pd.DataFrame({
        "nom": ["Durand", "Martin"],
        "prenom": ["Jean", "Paul"],
        "age": [25, 30]
    })
    test_df.to_csv(test_csv, sep=";", index=False)
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    uploaded_file_path = os.path.join(upload_dir, test_csv.name)
    test_csv.replace(uploaded_file_path)
    payload = {
        "source": test_csv.name,
        "columns": "nom,age",
        "conditions": "age > 26"
    }

    response = client.post("/extraction/run/extraction", json=payload)
    assert response.status_code == 200, "La requête doit réussir"
    data = response.json()
    assert data["status"] == "success", "Le statut doit être 'success'"
    assert any("Résultat sauvegardé dans" in log for log in data["logs"]), "Un log doit indiquer le fichier créé"
    extraction_file = [f for f in os.listdir(upload_dir) if f.startswith("extraction_result_")]
    assert extraction_file, "Un fichier d'extraction doit être créé"
    extracted_df = pd.read_csv(os.path.join(upload_dir, extraction_file[0]), sep=",")
    expected_columns = {"nom", "age"}
    assert set(extracted_df.columns).issubset(expected_columns), "Les colonnes extraites doivent être valides"
    assert all(extracted_df["age"] > 26), "Les conditions doivent être appliquées"

def test_generalisation_date_on_nom_should_fail(tmp_path):
    test_df = pd.DataFrame({
        "nom": ["Alice", "Bob"]
    })
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "data.csv")
    test_df.to_csv(csv_path, sep=";", index=False)
    payload = {
        "table": "data",
        "rules": [
            {"table": "data", "column": "nom", "moteur": "generalisation_date"}
        ]
    }

    response = client.post("/anonymization/run/anonymize", json=payload)
    
    assert response.status_code == 500, "Une erreur doit être renvoyée car la colonne n'est pas une date"
    assert "Erreur serveur" in response.json()["detail"], "Le message d'erreur doit indiquer un problème"