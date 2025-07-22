import pandas as pd
import pytest
from app.services.anonymization.anonymization_methods import RemplacementPrenom

def test_remplacement_prenom_apply(tmp_path):
    df = pd.DataFrame({'prenom': ['alice', 'bob', 'charlie']})
    moteur = RemplacementPrenom(df, 'prenom')
    result_df = moteur.apply()

    assert all(isinstance(val, str) and val != "" for val in result_df['prenom']), "Les prénoms doivent être remplacés"
    assert not any(val in ['alice', 'bob', 'charlie'] for val in result_df['prenom']), "Aucun prénom original ne doit rester"

def test_remplacement_prenom_colonne_non_texte():
    df = pd.DataFrame({'age': [25, 30]})
    moteur = RemplacementPrenom(df, 'age')

    with pytest.raises(ValueError, match="ne contient pas de valeurs de type chaîne de caractères valides"):
        moteur.apply()
