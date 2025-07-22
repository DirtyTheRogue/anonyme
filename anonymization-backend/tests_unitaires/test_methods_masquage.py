import pandas as pd
from app.services.anonymization.anonymization_methods import Masquage

def test_masquage_apply():
    df = pd.DataFrame({'nom': ['Durand', 'Martin', 'Dupont']})
    masquage = Masquage(df, 'nom')
    df_result = masquage.apply()

    assert all(value == "ANONYME" for value in df_result['nom']), "Tous les noms doivent être masqués"
