import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_file(tmp_path):
    csv_content = "nom;prenom\nDurand;Jean\nMartin;Paul\n"
    test_file_path = tmp_path / "test_upload.csv"
    test_file_path.write_text(csv_content)
    with open(test_file_path, "rb") as file:
        response = client.post(
            "/upload/upload",
            files={"file": ("test_upload.csv", file, "text/csv")}
        )
    assert response.status_code == 200, "La requête doit réussir"
    data = response.json()
    assert "message" in data and "uploadé avec succès" in data["message"].lower()
    assert "filepath" in data, "Le chemin du fichier doit être retourné"

    uploaded_path = data["filepath"]
    assert os.path.exists(uploaded_path), f"Le fichier {uploaded_path} doit exister sur le disque"
