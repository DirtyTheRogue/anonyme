import pandas as pd
import pytest
from app.services.anonymization.anonymization_methods import Arrondit

def test_arrondit_apply():
    df = pd.DataFrame({'montant': [23, 150, 2030]})
    moteur = Arrondit(df, 'montant')
    result_df = moteur.apply()

    assert result_df['montant'].tolist() == [30, 200, 3000], "Les montants doivent être arrondis au bon multiple"

def test_arrondit_colonne_non_numerique():
    df = pd.DataFrame({'nom': ['Alice', 'Bob']})
    moteur = Arrondit(df, 'nom')

    with pytest.raises(ValueError, match="ne contient pas de valeurs numériques valides"):
        moteur.apply()
