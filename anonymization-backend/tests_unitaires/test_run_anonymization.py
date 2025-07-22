import pandas as pd
from app.services.anonymization.anonymization_core import AnonymizerCore

def test_run_anonymization_with_masquage(tmp_path):
    df = pd.DataFrame({'nom': ['Jean', 'Paul']})
    instructions = [{"table": "data", "column": "nom", "moteur": "masquage"}]
    core = AnonymizerCore(instructions)
    core.dfs = {"data": df}
    core.run_anonymization()
    
    result = core.get_table("data")
    assert result["nom"].eq("ANONYME").all(), "Les noms doivent être masqués dans run_anonymization"
