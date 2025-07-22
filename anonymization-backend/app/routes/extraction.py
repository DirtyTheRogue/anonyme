import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime


router = APIRouter()

@router.api_route("/run/extraction", methods=["GET", "POST"])
async def run_extraction(request: Request):
    try:
        if request.method == "GET":
            return {"message": "Utilisez POST pour envoyer des données."}

        data = await request.json()
        print("🔹 [LOG Backend] Données reçues :", data)

        source = data.get("source")
        columns = data.get("columns")
        conditions = data.get("conditions")

        if not source or not columns:
            raise HTTPException(status_code=400, detail="Source et colonnes sont requis.")

        file_path = os.path.join("uploads", os.path.basename(source))
        if not os.path.isfile(file_path):
            print(f"[ERROR] Fichier non trouvé : {file_path}")
            raise HTTPException(status_code=400, detail=f"Le fichier source '{file_path}' est introuvable.")

        try:
            df = pd.read_csv(file_path, sep=";")
            df.columns = df.columns.str.replace('\ufeff', '').str.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur lors de la lecture du fichier source : {str(e)}")

        column_list = [col.strip() for col in columns.split(",")]
        if not all(col in df.columns for col in column_list):
            missing_columns = [col for col in column_list if col not in df.columns]
            raise HTTPException(status_code=400, detail=f"Colonnes manquantes : {', '.join(missing_columns)}")

        df = df[column_list]

        if conditions:
            try:
                df = df.query(conditions)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur dans les conditions : {str(e)}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extraction_result_{timestamp}.csv"
        output_file = os.path.join("uploads", filename)
        df.to_csv(output_file, index=False)

        logs = [
            f"Fichier reçu : {source}",
            f"Colonnes extraites : {columns}",
            f"Conditions appliquées : {conditions or 'Aucune'}",
            f"Résultat sauvegardé dans : {filename}",
        ]
        print("[LOG] Extraction réussie :", logs)

        return {"status": "success", "logs": logs}

    except Exception as e:
        print("❌ [ERREUR] Exception :", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@router.post("/preview_rows")
async def preview_rows(request: Request):
    try:
        data = await request.json()
        source = data.get("source")
        if not source:
            raise HTTPException(status_code=400, detail="Chemin source manquant.")

        file_path = os.path.join("uploads", os.path.basename(source))
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Fichier non trouvé.")

        df = pd.read_csv(file_path, sep=";")
        df.columns = df.columns.str.replace('\ufeff', '').str.strip()
        print("colonnes detectées :", df.columns.tolist())
        preview = df.head(3).to_dict(orient="records")  

        return {"preview": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prévisualisation : {str(e)}")

@router.post("/read_csv")
async def read_csv(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file, sep=";")
        print("✅ DEBUG - head(1):", df.head(1).to_dict())
        df.columns = df.columns.str.replace('\ufeff', '').str.strip()
        print("✅ Colonnes lues via /read_csv :", df.columns.tolist())
        return JSONResponse(content={"columns": df.columns.tolist()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lecture CSV : {str(e)}")
