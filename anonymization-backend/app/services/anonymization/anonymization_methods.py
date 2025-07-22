import pandas as pd
import os
import csv
from app.services.artefact_manager import save_json, read_json
from app.services.regex_colonne import normalize_column_name


class Masquage:
    """
    Applique un masquage simple sur une colonne (remplace les valeurs par 'ANONYME').
    """
    def __init__(self, df: pd.DataFrame, column: str, replacement_value: str = "ANONYME"):
        self.df = df
        self.column = normalize_column_name(column.strip().lower())
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.replacement_value = replacement_value

    def apply(self) -> pd.DataFrame:
        print("\n DEBUG - Colonnes du DataFrame :", list(self.df.columns))
        print(" DEBUG - Colonne recherchée :", self.column)

        if self.column not in self.df.columns:
            raise ValueError(f" La colonne '{self.column}' est introuvable dans le DataFrame.")

        print(f" [Masquage] Masquage de la colonne '{self.column}' avec la valeur '{self.replacement_value}'")
        self.df[self.column] = self.replacement_value
        return self.df



from datetime import datetime

class GeneralisationDate:
    """
    Moteur d'anonymisation qui généralise une date en remplaçant le jour par '01'.
    Exemple : '16/10/2003' devient '01/10/2003'
    """

    def __init__(self, df: pd.DataFrame, column: str):
        self.df = df.copy()
        self.column = column.strip().lower()
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.date_formats = None

    def _detect_date_format(self):
        """
        Détecte le format de date dans la colonne.
        Retourne un format de date ou None si aucun format valide n'est trouvé.
        """
        sample = self.df[self.column].dropna().astype(str).head()[:10]
        for valeur in sample:
            parts = valeur.replace('-', '/').split('/')
            if len(parts) != 3:
                continue
            try :
                part1, part2 = int (parts[0]), int(parts[1])
                if part1 > 12 or part2 <=12:
                    return "%d/%m/%Y" #fr
                elif part2>12 and part1 <= 12:
                    return "%m/%d/%Y" #usa
            except ValueError:
                continue
        raise ValueError(f"Impossible de déterminer automatiquement le format de date dans la colonne '{self.column}'")


    def _try_parse_date(self, valeur, fmt):
            """
            Essaie de parser une date avec un format donné.
            Retourne True si la date est valide, sinon False.
            """
            try:
                return datetime.strptime(str(valeur), fmt)
            except ValueError:
                return None
            
    def _generaliser_date(self, valeur):
        for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                date = datetime.strptime(str(valeur), fmt)
                return date.replace(day=1).strftime("%d/%m/%Y")  
            except ValueError:
                continue
        print(f" Format de date non reconnu pour la valeur: {valeur}")
        raise ValueError(f" Format de date non reconnu pour la valeur: {valeur}")
            

    def apply(self) -> pd.DataFrame:
        if self.column not in self.df.columns:
            raise ValueError(f" Colonne '{self.column}' introuvable dans le DataFrame.")
        print(f" [GeneralisationDate] Généralisation de la colonne '{self.column}'")
        sample_values=self.df[self.column].dropna().astype(str).unique()[:10]
        has_valid_date = any(
            any(
                self._try_parse_date(valeur, fmt) for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"))
                for valeur in sample_values
            )
        if not has_valid_date:
            raise ValueError(f"Impossible de déterminer automatiquement le format de date dans la colonne '{self.column}'")
        self.df[self.column] = self.df[self.column].apply(self._generaliser_date)
        return self.df
    


    


import random
import json

class RemplacementPrenom:
    """
    Classe permettant de remplacer les prénoms/noms dans un DataFrame
    en utilisant un annuaire et un système de cache.
    """

    def __init__(self, df: pd.DataFrame, column: str, moteur: str = "remplacement", cache_path=None):
        self.df = df.copy()
        self.column = column.strip().lower()
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.moteur = "prenom"
        self.cache_filename = f"cache_{self.moteur}.json"



    def _load_annuaire(self):
        """
        Charge les valeurs de remplacement depuis l’annuaire CSV.
        """
        annuaire_path = os.path.join(".", "config", f"Annuaire_{self.moteur.capitalize()}s.csv")
        try:
            with open(annuaire_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None) 
                return [row[0].strip().lower() for row in reader if row] ###############################
        except FileNotFoundError:
            print(f" ERREUR : Fichier annuaire introuvable -> {annuaire_path}")
            return []

    def _load_cache(self):
        """
        Charge le cache si le fichier existe.
        """
        return read_json(self.cache_filename)


    def _save_cache(self, cache):
        """
        Sauvegarde le cache dans un fichier JSON.
        """
        save_json(cache, self.cache_filename)

    def apply(self) -> pd.DataFrame:
        """
        Applique le remplacement et retourne un DataFrame modifié.
        """
        annuaire_values = self._load_annuaire()
        print(" Annuaire chargé :", annuaire_values[:10])

        cache = self._load_cache()

        if self.column not in self.df.columns:
            raise ValueError(f" La colonne '{self.column}' est introuvable dans le DataFrame.")
        if not self.df[self.column].apply(lambda x: isinstance(x, str)).all():
            raise ValueError(f" La colonne '{self.column}' ne contient pas de valeurs de type chaîne de caractères valides.")
        for index, row in self.df.iterrows():
            original_value = str(row[self.column]).strip().lower() ###############################
            if original_value not in cache:
                replacement = random.choice(annuaire_values) if annuaire_values else original_value
                cache[original_value] = replacement
            else:
                replacement = cache[original_value]

            print(f" [Remplacement] {original_value} -> {replacement}")
            self.df.at[index, self.column] = replacement

        self._save_cache(cache)
        return self.df

class RemplacementNom:
    """
    Classe permettant de remplacer les prénoms/noms dans un DataFrame
    en utilisant un annuaire et un système de cache.
    """

    def __init__(self, df: pd.DataFrame, column: str, moteur: str = "remplacement", cache_path=None):
        self.df = df.copy()
        self.column = column.strip().lower()
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.moteur = "nom"
        self.cache_filename = f"cache_{self.moteur}.json"

    def _load_annuaire(self):
        """
        Charge les valeurs de remplacement depuis l’annuaire CSV.
        """
        annuaire_path = os.path.join(".", "config", f"Annuaire_{self.moteur.capitalize()}s.csv")
        try:
            with open(annuaire_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None) 
                return [row[0].strip().lower() for row in reader if row] ###############################
        except FileNotFoundError:
            print(f" ERREUR : Fichier annuaire introuvable -> {annuaire_path}")
            return []

    def _load_cache(self):
        """
        Charge le cache si le fichier existe.
        """
        return read_json(self.cache_filename)


    def _save_cache(self, cache):
        """
        Sauvegarde le cache dans un fichier JSON.
        """
        save_json(cache, self.cache_filename)

    def apply(self) -> pd.DataFrame:
        """
        Applique le remplacement et retourne un DataFrame modifié.
        """
        annuaire_values = self._load_annuaire()
        print(" Annuaire chargé :", annuaire_values[:10])

        cache = self._load_cache()

        if self.column not in self.df.columns:
            raise ValueError(f" La colonne '{self.column}' est introuvable dans le DataFrame.")
        if not self.df[self.column].apply(lambda x: isinstance(x, str)).all():
            raise ValueError(f" La colonne '{self.column}' ne contient pas de valeurs de type chaîne de caractères valides.")

        for index, row in self.df.iterrows():
            original_value = str(row[self.column]).strip().lower() ###############################
            if original_value not in cache:
                replacement = random.choice(annuaire_values) if annuaire_values else original_value
                cache[original_value] = replacement
            else:
                replacement = cache[original_value]

            print(f" [Remplacement] {original_value} -> {replacement}")
            self.df.at[index, self.column] = replacement

        self._save_cache(cache)
        return self.df


import math

import pandas as pd
import numpy as np
import math

class Arrondit:
    """
    Moteur d'anonymisation qui arrondit les montants au multiple supérieur
    de leur ordre de grandeur.
    """

    def __init__(self, df: pd.DataFrame, column: str = "montant"):
        self.df = df.copy()
        self.column = column.strip().lower()
        self.df.columns = self.df.columns.str.strip().str.lower()

    def is_numeric(self, valeur):
        """
        Vérifie si une valeur est numérique (int ou float).
        """
        try:
            float(valeur)
            return True
        except (ValueError, TypeError):
            return False


    def _arrondir(self, valeur):
        if not self.is_numeric(valeur):
            raise ValueError(f" La valeur '{valeur}' n'est pas numérique et ne peut pas être arrondie.")
        try:
            valeur = float(valeur)
            if valeur == 0:
                return 0
            ordre_grandeur = 10 ** int(math.floor(math.log10(valeur)))
            arrondi = math.ceil(valeur / ordre_grandeur) * ordre_grandeur
            return arrondi
        except Exception as e:
            print(f" Valeur non valide pour l'arrondi : {valeur} -> erreur : {e}")
            return valeur  

    def apply(self) -> pd.DataFrame:
        if self.column not in self.df.columns:
            raise ValueError(f" La colonne '{self.column}' est introuvable dans le DataFrame.")
        if not pd.to_numeric(self.df[self.column], errors='coerce').notna().any():
            raise ValueError(f" La colonne '{self.column}' ne contient pas de valeurs numériques valides.")

        print(f" [Arrondit] Arrondi des valeurs dans la colonne '{self.column}'")
        self.df[self.column] = self.df[self.column].apply(self._arrondir)
        return self.df


