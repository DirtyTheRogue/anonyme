import os
import json
import zipfile
import tempfile
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.reidentification_test import run_test, run_test_with_params
from app.models.reidentification_model import ReidentificationParams

router = APIRouter()

TEST_RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_results"))

os.makedirs(TEST_RESULTS_DIR, exist_ok=True)

@router.post("/run")
async def run_test_endpoint():
    """ Lance un test de réidentification depuis config.json et stocke les résultats. """
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.json")
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)

        if "test" not in config:
            raise HTTPException(status_code=400, detail="Clé 'test' introuvable dans config.json")

        if "og_tables" not in config["test"]:
            raise HTTPException(status_code=400, detail="Clé 'og_tables' manquante dans la configuration des tests")

        test_config = config["test"]

        result = run_test(test_config)  

        results_file = os.path.join(TEST_RESULTS_DIR, "test_results.json")
        with open(results_file, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        print(f"✅ [INFO] Résultats sauvegardés dans {results_file}")

        return {"status": "success", "message": "Test terminé avec succès", "results": result}

    except Exception as e:
        print(f"❌ [ERREUR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


@router.post("/run/params")
async def run_test_with_parameters(params: ReidentificationParams):
    """ Lance un test de réidentification avec des paramètres personnalisés. """
    try:
        # Convertir le modèle Pydantic en dictionnaire
        params_dict = params.dict()
        
        # Lancer le test avec les paramètres fournis
        result = run_test_with_params(params_dict)

        # Sauvegarder les résultats
        results_file = os.path.join(TEST_RESULTS_DIR, "test_results.json")
        with open(results_file, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        print(f"✅ [INFO] Test avec paramètres personnalisés terminé, résultats sauvegardés dans {results_file}")

        return {"status": "success", "message": "Test avec paramètres personnalisés terminé avec succès", "results": result}

    except Exception as e:
        print(f"❌ [ERREUR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


@router.get("/results")
async def get_test_results():
    """ Récupère les résultats du dernier test de réidentification. """
    try:
        results_file = os.path.join(TEST_RESULTS_DIR, "test_results.json")

        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail="Aucun fichier de résultats trouvé.")

        with open(results_file, "r", encoding="utf-8") as file:
            results = json.load(file)

        return {"status": "success", "results": results}

    except Exception as e:
        print(f"❌ [ERREUR BACKEND] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


@router.get("/export/summary")
async def export_results_summary():
    """ Exporte un résumé des résultats au format JSON. """
    try:
        results_file = os.path.join(TEST_RESULTS_DIR, "test_results.json")
        
        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail="Aucun fichier de résultats trouvé.")
        
        return FileResponse(
            results_file,
            media_type="application/json",
            filename="test_results_summary.json",
            headers={"Content-Disposition": "attachment; filename=test_results_summary.json"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export : {str(e)}")


@router.get("/export/artifacts")
async def export_results_artifacts():
    """ Exporte tous les artefacts générés par les tests au format ZIP. """
    try:
        results_file = os.path.join(TEST_RESULTS_DIR, "test_results.json")
        
        if not os.path.exists(results_file):
            raise HTTPException(status_code=404, detail="Aucun fichier de résultats trouvé.")
        
        # Charger les résultats pour obtenir les chemins des artefacts
        with open(results_file, "r", encoding="utf-8") as file:
            results = json.load(file)
        
        # Créer un fichier ZIP temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # Ajouter le résumé JSON
                zipf.write(results_file, "summary/test_results.json")
                
                # Parcourir les résultats et ajouter les artefacts
                if "summary" in results:
                    for table_name, table_results in results["summary"].items():
                        if isinstance(table_results, dict) and "path" in table_results:
                            artifact_path = table_results["path"]
                            
                            # Vérifier si le dossier existe
                            if os.path.exists(artifact_path):
                                # Ajouter tous les fichiers du dossier d'artefacts
                                for root, dirs, files in os.walk(artifact_path):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        # Créer un chemin relatif dans le ZIP
                                        relative_path = os.path.relpath(file_path, os.path.dirname(artifact_path))
                                        zipf.write(file_path, f"artifacts/{table_name}/{relative_path}")
            
            return FileResponse(
                temp_zip.name,
                media_type="application/zip",
                filename="test_artifacts.zip",
                headers={"Content-Disposition": "attachment; filename=test_artifacts.zip"}
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export des artefacts : {str(e)}")
