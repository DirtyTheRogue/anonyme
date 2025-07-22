import os

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.anonymization.anonymization_core import AnonymizerCore
from app.utility import DATA_DIR, RESULTS_DIR
from app.services.artefact_manager import save_dataframe, get_timestamped_dir


router = APIRouter()

AVAILABLE_MOTEURS = [
    "masquage",
    "remplacement_nom",
    "remplacement_prenom",
    "arrondit",
    "generalisation_date"
]

def load_all_csv_files():
    """
    Charge tous les fichiers CSV présents dans le dossier DATA_DIR.
    Retourne un dictionnaire contenant les DataFrames chargés.
    """
    tables = {}
    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".csv"):
            table_name = os.path.splitext(file_name)[0]  
            file_path = os.path.join(DATA_DIR, file_name)
            print(file_path)
            
            try:
                df = pd.read_csv(file_path, sep=";")
                tables[table_name] = df
                print(f"✅ Chargement réussi de : {file_name}")
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {file_name}: {str(e)}")
    
    if not tables:
        raise HTTPException(status_code=400, detail="Aucun fichier CSV trouvé dans le dossier data.")
    
    return tables

@router.get("/rules")
async def get_anonymization_rules():
    """
    Retourne la liste des règles d'anonymisation disponibles.
    """
    try:
        return {"rules": AVAILABLE_MOTEURS}
    except Exception as e:
        print(f"Erreur lors de la récupération des règles : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@router.post("/run/anonymize")
async def apply_anonymization(request: Request):
    try:
        payload = await request.json()
        get_timestamped_dir()  
        print(" [LOG Backend] Payload reçu :", payload)
        table = payload.get("table")
        rules = payload.get("rules", [])

        if not table or not rules:
            raise HTTPException(status_code=400, detail="Tables, colonnes et règles sont requis.")
        print(os.listdir(DATA_DIR))
        print("✅ Table reçue :", table)
        print("✅ Règles reçues :", rules)

        logs = []
        table_to_features = {table: []}

        for rule in rules:
            table_name= rule.get("table")
            column = rule.get("column",None)
            moteur = rule.get("moteur",None)
            if table_name and column and moteur:
               if table_name not in table_to_features:
                    table_to_features[table_name] = []
               table_to_features[table_name].append({"column": column, "moteur": moteur})
            else:
                raise HTTPException(status_code=400, detail="Erreur dans la structure des règles d'anonymisation.")
            
        all_tables = load_all_csv_files()

        if any(table_to_features.values()):
            print (table_to_features.items())
            try:
                for table_name, features in table_to_features.items():
                
                    if table_name not in all_tables:
                        raise HTTPException(status_code=400, detail=f"Table {table_name} introuvable dans le dossier data.")
                    df= all_tables[table_name]
                    save_dataframe(df, f"{table_name}_original.csv")
                    instructions = [{"table": table_name, "column": feature["column"], "moteur": feature["moteur"]} for feature in features]
                    print(f" [DEBUG] Instructions d'anonymisation : {instructions}")
                    core = AnonymizerCore(instructions)
                    core.load_tables({table_name: df})
                    core.run_anonymization()
                    
                    result_file = os.path.join(RESULTS_DIR, f"{table_name}_anonymized.csv")
                    df_result = core.get_table(table_name)
                    df_result.to_csv(result_file, index=False, sep=";")
                    preview = df_result.head(5).to_dict(orient="records")
                    
                    logs.append(f"✅ Anonymisation réussie pour {table_name} avec moteurs : {features}")
            
            except Exception as e:
                print(os.listdir())
                logs.append(f" Erreur lors de l'anonymisation : {str(e)}")  

        return JSONResponse(
            status_code=200,
            content={"status": "success", "logs": logs, "preview": preview}
        )

    except Exception as e:
        print(f" [ERREUR] Erreur serveur globale : {str(e)}")  
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
