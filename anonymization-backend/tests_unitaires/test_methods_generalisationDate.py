import pandas as pd
import pytest
from app.services.anonymization.anonymization_methods import GeneralisationDate

def test_generalisation_date_apply():
    df = pd.DataFrame({'date_naissance': ['16/10/2003', '02/01/1995']})
    moteur = GeneralisationDate(df, 'date_naissance')
    result_df = moteur.apply()
    assert result_df['date_naissance'].tolist() == ['01/10/2003', '01/01/1995'], \
        "Les dates doivent être généralisées avec '01' comme jour"

def test_generalisation_date_sur_colonne_inexistante():
    df = pd.DataFrame({'prenom': ['Alice', 'Bob']})
    moteur = GeneralisationDate(df, 'date_naissance')
    with pytest.raises(ValueError, match="Colonne 'date_naissance' introuvable"):
        moteur.apply()

def test_generalisation_date_plusieurs_formats():
    df = pd.DataFrame({
        'date_naissance': ['16/10/2003', '02/01/1995', '15-13-2000']  # 15-13-2000 est invalide
    })
    moteur = GeneralisationDate(df, 'date_naissance')
    with pytest.raises(ValueError, match="Format de date non reconnu pour la valeur: 15-13-2000"):
        moteur.apply()

def test_destection_fr_format():
    df = pd.DataFrame({'date_naissance': ['16/10/2003', '02/01/1995']})
    moteur = GeneralisationDate(df, 'date_naissance')
    result_df = moteur.apply()
    assert result_df["date_naissance"].tolist() == ['01/10/2003', '01/01/1995'], \
        "Les dates françaises doivent être généralisées avec 01 comme jour"

def test_generalisation_date_auto_detection_us_format():
    df = pd.DataFrame({'date_naissance': ['03/15/2003', '12/22/1999']})  # Format US : MM/DD/YYYY
    moteur = GeneralisationDate(df, 'date_naissance')
    result_df = moteur.apply()
    assert result_df["date_naissance"].tolist() == ['01/03/2003', '01/12/1999'], \
        "Les dates américaines doivent être généralisées avec 01 comme jour"

def test_generalisation_date_auto_detection_erreur():
    df = pd.DataFrame({'date_naissance': ['texte', 'invalide']})  # Rien de détectable
    moteur = GeneralisationDate(df, 'date_naissance')
    with pytest.raises(ValueError, match="Impossible de déterminer automatiquement le format de date"):
        moteur.apply()
