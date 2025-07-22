import os
import json
from fastapi import APIRouter, HTTPException
from app.services.reidentification_test import run_test  

router = APIRouter()

TEST_RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_results"))

os.makedirs(TEST_RESULTS_DIR, exist_ok=True)

@router.post("/run")
async def run_test_endpoint():
    """ Lance un test de réidentification et stocke les résultats. """
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
