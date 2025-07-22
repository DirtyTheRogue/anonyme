import pandas as pd
from app.services.anonymization.anonymization_core import AnonymizerCore

def test_anonymise_masquage():
    df = pd.DataFrame({'nom': ['Alice', 'Bob']})
    instructions = [{"table": "test", "column": "nom", "moteur": "masquage"}]
    core = AnonymizerCore(instructions)
    result = core.anonymise(df, "nom", "masquage")
    assert result["nom"].eq("ANONYME").all(), "La colonne 'nom' doit être masquée"
