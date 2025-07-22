import pandas as pd
from app.services.anonymization.anonymization_core import AnonymizerCore

def test_get_table_success():
    df = pd.DataFrame({'prenom': ['Anne', 'Claire']})
    instructions = []
    core = AnonymizerCore(instructions)
    core.dfs = {"clients": df}
    
    result = core.get_table("clients")
    assert result.equals(df), "get_table doit retourner le DataFrame correspondant"

