
import json
import subprocess
import sys
import shutil
import os, sys
import pandas as pd
from fastapi.responses import JSONResponse

from fastapi import FastAPI, HTTPException, Depends, status, Request, File, UploadFile, Form,APIRouter
from fastapi.middleware.cors import CORSMiddleware

import glob
print(sys.path)
 

from app.utility import BASE_DIR, DATA_DIR, RESULTS_DIR


print(f"✅ BASE_DIR : {BASE_DIR}")
print(f"✅ DATA_DIR : {DATA_DIR}")
print(f"✅ RESULTS_DIR : {RESULTS_DIR}")



app = FastAPI(debug=True)
# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db  
from app.models import User  
from app.services.evaluator import evaluate
from app.database import engine, Base
from app.services.anonymizer import anonymize
from app.services.utils import make_unique_dir
from app.routes.upload import router as upload_router
app.include_router(upload_router, prefix="/upload")
from app.routes.reidentification import router as reidentification_router
app.include_router(reidentification_router, prefix  = "/reidentification")
from app.routes.anonymization import router as anonymization_router
app.include_router(anonymization_router, prefix="/anonymization")
from app.routes.extraction import router as extraction_router
app.include_router(extraction_router, prefix="/extraction")
from app.routes.evaluation import router as evaluation_router
app.include_router(evaluation_router, prefix="/evaluation")




CSV_FOLDER = "data"





with open("config/config.json", "r") as f:
    config = json.load(f)

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str




@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Nom d'utilisateur déjà pris.",
        )
    
    new_user = User(username=request.username, password=request.password)
    db.add(new_user)
    db.commit()
    return {"message": "Utilisateur créé avec succès"}


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or user.password != request.password:  
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect.",
        )
    return {"message": "Connexion réussie", "user_id": user.id}



Base.metadata.create_all(bind=engine)






def run_command(command):
    print(f"Running command: {command}")
    process = subprocess.Popen(
        command, shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True
    )
    process.communicate()

    if process.returncode != 0:
        return f"Command failed with return code {process.returncode}"
    else:
        return "Command executed successfully!"
    
def anonymize_table(df):
    """
    Applique les règles d'anonymisation sur un DataFrame pandas.
    Pour le momentca masque simplement les données sensibles en les remplaçant par 'XXXXX'.
    """
    columns_to_anonymize = ["Nom", "Prenom", "Date_naissance", "Nir"]  
    
    for col in columns_to_anonymize:
        if col in df.columns:
            df[col] = "Anonymized"  
    
    return df


@app.post("/run/anonymize_all")
async def anonymize_all():
    data_folder = "data"
    tables = [f for f in os.listdir(data_folder) if f.endswith(".csv")]  

    if not tables:
        return {"status": "error", "message": "Aucune table trouvée pour anonymisation."}

    results = []
    for table in tables:
        table_path = os.path.join(data_folder, table)
        
        try:
            df = pd.read_csv(table_path, sep=";")
            df_anonymized = anonymize_table(df)  
            
            df_anonymized.to_csv(table_path, sep=";", index=False)
            results.append(f"Anonymisation réussie pour {table}")
        
        except Exception as e:
            results.append(f"Erreur sur {table}: {str(e)}")

    return {"status": "success", "details": results}




RESULTS_DIR = "results"

""" @app.post("/run/anonymize")
async def apply_anonymization(request: Request):
    try:
        # 🔹 Récupération des données envoyées par le frontend
        data = await request.json()
        tables = data.get("tables", [])
        columns = data.get("columns", [])
        rules = data.get("rules", [])

        if not tables or not columns or not rules:
            raise HTTPException(status_code=400, detail="Tables, colonnes et règles sont requis.")

        logs = []
        table_to_features = {table: [] for table in tables}

        # 🗑️ Supprimer les colonnes qui ont la règle "suppression"
        for table, column, rule in zip(tables, columns, rules):
            if rule == "suppression":
                print(f"🗑️ Suppression de la colonne '{column}' de la table '{table}'")

                file_path = os.path.join("uploads", f"{table}.csv")
                try:
                    df = pd.read_csv(file_path, sep=";")
                    if column in df.columns:
                        df.drop(columns=[column], inplace=True)
                        df.to_csv(file_path, sep=";", index=False)
                        print(f"✅ Colonne '{column}' supprimée de '{table}' et enregistrée.")
                    else:
                        print(f"⚠️ La colonne '{column}' n'existe pas dans '{table}'.")
                except FileNotFoundError:
                    print(f"❌ Erreur : Le fichier '{file_path}' est introuvable.")

        # 🔹 Séparer les colonnes à supprimer des autres transformations
        tables_to_drop_columns = {}

        for table, column, rule in zip(tables, columns, rules):
            if rule == "suppression":
                # Stocker les colonnes à supprimer
                if table not in tables_to_drop_columns:
                    tables_to_drop_columns[table] = []
                tables_to_drop_columns[table].append(column)
            else:
                # Stocker les colonnes à anonymiser
                table_to_features[table].append(column)

        # 🔹 Suppression des colonnes avant l'anonymisation
        for table, columns in tables_to_drop_columns.items():
            file_path = os.path.join("uploads", table)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df.drop(columns=columns, inplace=True, errors="ignore")
                df.to_csv(file_path, index=False)  # Sauvegarde du fichier mis à jour
                logs.append(f"🗑️ Colonnes supprimées pour '{table}' : {columns}")

        # 🔹 Appel de `anonymizer.py` uniquement si des colonnes restent à anonymiser
        if any(table_to_features.values()):
            try:
                anonymize(list(table_to_features.keys()), list(table_to_features.values()), cache=True)
                logs.append(f"✅ Anonymisation réussie pour {tables}")
            except Exception as e:
                logs.append(f"❌ Erreur lors de l'anonymisation : {str(e)}")

        # 🔹 Retourner les logs
        return {"status": "success" if all("✅" in log for log in logs) else "error", "logs": logs}

    except Exception as e:
        print(f"❌ [ERREUR] Erreur serveur globale : {str(e)}")  
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
             """



    
""" @app.post("/run/extraction")
async def run_extraction(request: Request):
    try:
        # Récupérer les données envoyées par le frontend
        data = await request.json()
        source = data.get("source")
        columns = data.get("columns")
        conditions = data.get("conditions")

        # Logs des données reçues
        print("[LOG] Données reçues :", {"source": source, "columns": columns, "conditions": conditions})

        # Validation des paramètres obligatoires
        if not source or not columns:
            raise HTTPException(status_code=400, detail="Source et colonnes sont requis.")

        # Vérifie si le fichier source existe
        file_path = os.path.join("uploads", os.path.basename(source))
        if not os.path.isfile(file_path):
            print(f"[ERROR] Fichier non trouvé : {file_path}")  # Debug
            raise HTTPException(status_code=400, detail=f"Le fichier source '{file_path}' est introuvable.")

        # Lecture du fichier source
        try:
            df = pd.read_csv(file_path, sep=';')
            df.columns = df.columns.str.strip()  # Supprime les espaces avant/après les noms de colonnes
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur lors de la lecture du fichier source : {str(e)}")

        # Filtrage des colonnes spécifiées
        column_list = [col.strip() for col in columns.split(",")]
        if not all(col in df.columns for col in column_list):
            missing_columns = [col for col in column_list if col not in df.columns]
            raise HTTPException(status_code=400, detail=f"Colonnes manquantes : {', '.join(missing_columns)}")

        df = df[column_list]

        # Application des conditions si fournies
        if conditions:
            try:
                df = df.query(conditions)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur dans les conditions : {str(e)}")

        # Sauvegarde du fichier extrait
        output_file = os.path.join("uploads", "extraction_result.csv")
        df.to_csv(output_file, index=False)

        # Logs de l'opération
        logs = [
            f"Fichier reçu : {source}",
            f"Colonnes extraites : {columns}",
            f"Conditions appliquées : {conditions or 'Aucune'}",
            f"Résultat sauvegardé dans : {output_file}",
        ]
        print("[LOG] Extraction réussie :", logs)

        return {"status": "success", "logs": logs}

    except Exception as e:
        print("[ERREUR] Exception :", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}") """



""" # Fonction utilitaire pour exécuter une commande shell
def run_command(command):
    import subprocess
    try:
        result = subprocess.run(
            command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout  # Retourne la sortie de la commande
    except subprocess.CalledProcessError as e:
        return f"Erreur lors de l'exécution de la commande : {e.stderr}"
    
    
@app.post("/run/evaluation")
async def run_evaluation(request: Request):
    try:
        # Récupérer les données envoyées par le frontend
        data = await request.json()
        original_file = data.get("originalFile", "").strip(' "')
        anonymized_file = data.get("anonymizedFile", "").strip(' "')
        metrics = data.get("metrics", "")

        # Validation des paramètres
        if not original_file or not anonymized_file:
            raise HTTPException(status_code=400, detail="Les fichiers original et anonymisé sont requis.")
        if not metrics:
            raise HTTPException(status_code=400, detail="Les métriques sont requises.")

        # Simuler la logique d'évaluation
        evaluation_command = (
            f'python app/services/evaluator.py --original "{original_file}" --anonymized "{anonymized_file}" --metrics {metrics}'
        )
        result = run_command(evaluation_command)

        # Logs simulés
        logs = [
            f"Évaluation démarrée avec les fichiers : {original_file} et {anonymized_file}",
            f"Métriques utilisées : {metrics}",
            f"Commande exécutée : {evaluation_command}",
            f"Résultat : {result}"
        ]
        # Résultats simulés
        results = ["Précision : 0.95", "Recall : 0.90", "F1-Score : 0.92"]

        return {"status": "success", "results": results, "logs": logs}

    except HTTPException as http_exc:
        raise http_exc  # Erreurs HTTP correctement traitées
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
 """

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
ROOT_DIR = os.path.dirname(BASE_DIR)  

#ANCIEN ENDPOINT, TRANSFERE VERS ROUTES/REIDENTIFICATION

""" @app.post("/run/test")
async def run_test():
    try:
        # ✅ Récupération de la configuration du test
        test_config = config.get("test", {})
        if not test_config:
            raise HTTPException(status_code=400, detail="Test configuration not found.")

        # 📂 Trouver le dernier dossier anonymisé
        results_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "results"))

        print(f"[DEBUG] results_dir: {results_dir}")

        if not os.path.exists(results_dir):
            raise HTTPException(status_code=400, detail=f"Dossier results introuvable: {results_dir}")

        anon_folders = sorted(
            [d for d in os.listdir(results_dir) if d.startswith("anon_data_") and d.split("_")[-1].isdigit()],
            key=lambda x: int(x.split("_")[-1]),
            reverse=True
        )

        if not anon_folders:
            raise HTTPException(status_code=400, detail="Aucun dossier anonymisé trouvé.")

        latest_anon_dir = os.path.join(results_dir, anon_folders[0])  # 📌 Dossier le plus récent
        print(f"🟢 [DEBUG] Dossier anonymisé trouvé : {latest_anon_dir}")
        # 🔍 Récupérer les fichiers .parquet récents
        anon_files = glob.glob(os.path.join(latest_anon_dir, "*.parquet"))
        if not anon_files:
            raise HTTPException(status_code=400, detail=f"Aucun fichier Parquet anonymisé trouvé dans {latest_anon_dir}")
        print(f"🟢 [DEBUG] Fichiers Parquet détectés : {anon_files}")
        # 🔹 Mise à jour des fichiers anonymisés dans la config
        test_config["anon_tables"] = anon_files
        # 🔎 Vérification des paramètres nécessaires
        required_keys = ["og_tables", "anon_tables", "ids", "count_cols", "group_cols", "group_var", "target", "exp_features", "viz"]
        missing_keys = [key for key in required_keys if key not in test_config]
        if missing_keys:
            raise HTTPException(status_code=400, detail=f"Clés manquantes dans la configuration du test : {missing_keys}")
        print(f"🟢 [INFO] Lancement du test avec la configuration suivante :\n{test_config}")

        # 🚀 Lancer le test de réidentification avec evaluate()
        result = evaluate(
            og_tables=test_config["og_tables"],
            anon_tables=test_config["anon_tables"],
            ids=test_config["ids"],
            count_cols=test_config["count_cols"],
            group_cols=test_config["group_cols"],
            group_var=test_config["group_var"],
            target=test_config["target"],
            exp_features=test_config["exp_features"],
            viz=test_config["viz"]
        )

        return {"status": "success", "message": result}

    except Exception as e:
        print(f"❌ [ERREUR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}") """




@app.get("/health")
def health_check():
    return {"status": "API is running"}

@app.get("/tables")
def get_tables():
    try:
        tables = os.listdir("data")  
        return {"tables": [table.replace(".csv", "") for table in tables]}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.get("/tables/{table_name}/columns")
def get_columns(table_name: str):
    file_path = os.path.join("data", f"{table_name}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Table non trouvée")

    df = pd.read_csv(file_path, sep=";")  
    return {"columns": df.columns.tolist()}

@app.get("/extraction/tables")
def get_extraction_tables():
    """Retourne la liste des fichiers CSV disponibles pour l'extraction (dossier uploads)."""
    try:
        tables = [file.replace(".csv", "") for file in os.listdir("uploads") if file.endswith(".csv")]
        return {"tables": tables}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/extraction/{table_name}/columns")
def get_extraction_columns(table_name: str):
    """Retourne la liste des colonnes du fichier CSV sélectionné (dossier uploads)."""
    file_path = os.path.join("uploads", f"{table_name}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Table non trouvée dans uploads.")

    df = pd.read_csv(file_path, sep=";")
    return {"columns": df.columns.tolist()}




@app.get("/results")
def get_results():
    try:
        results = [
            {"name": "anonymized_data.csv", "url": "/downloads/anonymized_data.csv"},
            {"name": "extraction_report.json", "url": "/downloads/extraction_report.json"},
        ]

        logs = [
            "Anonymisation terminée avec succès pour 3 tables.",
            "Extraction complétée avec 5000 enregistrements extraits.",
            "Évaluation terminée : précision = 0.95, recall = 0.90."
        ]

        return {"results": results, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")




""" @app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        print(f"Tentative d'enregistrement du fichier : {file_path}")

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Vérifiez si le fichier existe après l'enregistrement
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Fichier non enregistré sur le disque.")

        print(f"Fichier enregistré avec succès : {file_path}")
        return {"message": "Fichier uploadé avec succès", "filepath": file_path}

    except Exception as e:
        print(f"Erreur lors de l'enregistrement du fichier : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload : {str(e)}") """





@app.post("/read_csv")
async def read_csv(file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        return {"error": str(e)}
    
