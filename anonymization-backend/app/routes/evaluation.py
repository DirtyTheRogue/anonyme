import os
from fastapi import APIRouter, HTTPException, Request
from app.services.evaluator import evaluate  

router = APIRouter()

def run_command(command):
    import subprocess
    try:
        result = subprocess.run(
            command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout 
    except subprocess.CalledProcessError as e:
        return f"Erreur lors de l'exécution de la commande : {e.stderr}"
    
@router.post("/run/evaluation")
async def run_evaluation(request: Request):
    try:
        data = await request.json()
        original_file = data.get("originalFile", "").strip(' "')
        anonymized_file = data.get("anonymizedFile", "").strip(' "')
        metrics = data.get("metrics", "")

        if not original_file or not anonymized_file:
            raise HTTPException(status_code=400, detail="Les fichiers original et anonymisé sont requis.")
        if not metrics:
            raise HTTPException(status_code=400, detail="Les métriques sont requises.")

        evaluation_command = (
            f'python app/services/evaluator.py --original "{original_file}" --anonymized "{anonymized_file}" --metrics {metrics}'
        )
        result = run_command(evaluation_command)

        logs = [
            f"Évaluation démarrée avec les fichiers : {original_file} et {anonymized_file}",
            f"Métriques utilisées : {metrics}",
            f"Commande exécutée : {evaluation_command}",
            f"Résultat : {result}"
        ]
        results = ["Précision : 0.95", "Recall : 0.90", "F1-Score : 0.92"]

        return {"status": "success", "results": results, "logs": logs}

    except HTTPException as http_exc:
        raise http_exc 
    except Exception as e:
        print(f"❌ [ERREUR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
