import pandas as pd
import pytest
from app.services.anonymization.anonymization_methods import RemplacementNom

def test_remplacement_nom_apply(tmp_path):
    df = pd.DataFrame({'nom': ['dupont', 'durand', 'leclerc']})
    moteur = RemplacementNom(df, 'nom')
    result_df = moteur.apply()

    assert all(isinstance(val, str) and val != "" for val in result_df['nom']), "Les noms doivent être remplacés"
    assert not any(val in ['dupont', 'durand', 'leclerc'] for val in result_df['nom']), "Aucun nom original ne doit rester"

def test_remplacement_nom_colonne_non_texte():
    df = pd.DataFrame({'age': [25, 30]})
    moteur = RemplacementNom(df, 'age')

    with pytest.raises(ValueError, match="ne contient pas de valeurs de type chaîne de caractères valides"):
        moteur.apply()
