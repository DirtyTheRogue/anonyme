import sys
import os

from app.main import app

from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_anonymization_rules():
    response = client.get("/anonymization/rules")
    assert response.status_code == 200, "La requête doit réussir"
    data = response.json()
    
    assert "rules" in data, "La réponse doit contenir la clé 'rules'"
    assert isinstance(data["rules"], list), "Les règles doivent être une liste"
    
    moteurs_attendus = [
        "masquage",
        "remplacement_nom",
        "remplacement_prenom",
        "arrondit",
        "generalisation_date"
    ]
    for moteur in moteurs_attendus:
        assert moteur in data["rules"], f"Le moteur '{moteur}' doit être présent"
