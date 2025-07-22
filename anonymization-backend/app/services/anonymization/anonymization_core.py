from app.services.anonymization.anonymization_methods import Masquage, RemplacementNom, RemplacementPrenom, Arrondit, GeneralisationDate
import os
import pandas as pd
from app.utility import DATA_DIR
from app.services.artefact_manager import log_message, save_dataframe


class AnonymizerCore:
    def __init__(self, instructions: list[dict]):
        """
        Initialise l'anonymiseur avec une liste d'instructions :
        [{"table": "data", "column": "nom", "moteur": "masquage"}, ...]
        """
        self.instructions = instructions
        self.dfs = {}  # { "data": DataFrame }
        self.moteurs = {
            "masquage": Masquage,
            "remplacement_prenom": RemplacementPrenom,
            "remplacement_nom": RemplacementNom,
            "arrondit": Arrondit,
            "generalisation_date": GeneralisationDate,
        }

    def load_tables(self, tables: dict):
        """
        Charge les fichiers nécessaires à partir d'instructions.
        Les fichiers doivent être présents dans le dossier data.
        """
        tables = {instr["table"] for instr in self.instructions}
        log_message(f"📥 Instructions reçues : {self.instructions}")
        for table in tables:
            file_path = os.path.join(DATA_DIR, f"{table}.csv")
            log_message(f"📁 Chargement du fichier : {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")
            df = pd.read_csv(file_path, sep=";")
            df.columns = [str(col).strip().lower() for col in df.columns]
            self.dfs[table] = df
            log_message(f" Table '{table}' chargée avec succès.")

    def anonymise(self, df: pd.DataFrame, column: str, moteur: str) -> pd.DataFrame:
        """
        Applique une méthode d'anonymisation sur une colonne d'un DataFrame.
        """
        if moteur not in self.moteurs:
            raise ValueError(f"Le moteur '{moteur}' n'existe pas.")
        moteur_class = self.moteurs[moteur]
        log_message(f"🔧 Application de '{moteur}' sur la colonne '{column}'")
        if moteur == "remplacement":
            df_modifie = moteur_class(df, column, moteur).apply()
        else:
            df_modifie = moteur_class(df, column).apply()
        return df_modifie

    def run_anonymization(self):
        for idx, instr in enumerate(self.instructions):
            table = instr["table"]
            column = instr["column"]
            moteur = instr["moteur"]

            if table not in self.dfs:
                raise ValueError(f"La table '{table}' n'a pas été chargée.")

            df = self.dfs[table]
            df_modifie = self.anonymise(df, column, moteur)
            self.dfs[table] = df_modifie

            filename = f"{moteur}_{column}.csv"
            save_dataframe(df_modifie, filename)
            log_message(f" Instruction {idx+1}/{len(self.instructions)} appliquée avec succès.")

    def get_results(self) -> dict:
        """
        Retourne les DataFrames anonymisés sous forme de dictionnaire.
        """
        return {table: df for table, df in self.dfs.items()}

    def get_table(self, name: str) -> pd.DataFrame:
        """
        Retourne le DataFrame anonymisé correspondant à la table donnée.
        """
        if name not in self.dfs:
            raise ValueError(f"La table '{name}' n'a pas été trouvée.")
        return self.dfs.get(name)
