import pandas as pd
from app.services.anonymization.anonymization_core import AnonymizerCore
import  pytest

def test_anonymizer_core_masquage():
    df = pd.DataFrame({'nom': ['Alice', 'Bob']})
    instructions = [{"table": "test_table", "column": "nom", "moteur": "masquage"}]
    core = AnonymizerCore(instructions)
    core.dfs = {"test_table": df}
    
    core.run_anonymization()
    df_result = core.get_table("test_table")

    assert df_result["nom"].eq("ANONYME").all(), "La colonne 'nom' doit être totalement masquée"

def test_anonymizer_core_moteur_inconnu():
    df = pd.DataFrame({'nom': ['Alice']})
    instructions = [{"table": "data", "column": "nom", "moteur": "moteur_inconnu"}]
    core = AnonymizerCore(instructions)
    core.dfs = {"data": df}

    with pytest.raises(ValueError, match="Le moteur 'moteur_inconnu' n'existe pas."):
        core.run_anonymization()

