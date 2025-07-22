import os
import glob
from typing import Dict, Any
from .runner_test import run_reidentification_tests


def run_test(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction pont entre l'API et le test runner.
    Adapte la configuration JSON pour l'utilisation avec run_reidentification_tests.
    
    Args:
        config (Dict): Configuration des tests depuis config.json
        
    Returns:
        Dict: Résultats des tests de réidentification
    """
    
    # Préparer les paramètres pour run_reidentification_tests
    params = {
        "og_tables": config.get("og_tables", []),
        "anon_tables": config.get("anon_tables", []),
        "group_cols": config.get("group_cols", []),
        "count_cols": config.get("count_cols", []),
        "exp_features": config.get("exp_features", []),
        "target": config.get("target", []),
        "ids": config.get("ids", []),
        "group_var": config.get("group_var", []),
        "og_fusion_table": config.get("og_fusion_table", []),
        "anon_fusion_table": config.get("anon_fusion_table", []),
        "fusion_columns_to_combine": config.get("fusion_columns_to_combine", []),
        "viz": config.get("viz", False)
    }
    
    # Si viz est une string "True", la convertir en boolean
    if isinstance(params["viz"], str):
        params["viz"] = params["viz"].lower() == "true"
    
    # Auto-détection des tables anonymisées si nécessaire
    if not params["anon_tables"]:
        params["anon_tables"] = _find_latest_anon_tables()
    
    # Lancer les tests de réidentification
    results = run_reidentification_tests(params)
    
    return {
        "summary": results,
        "config_used": params,
        "status": "completed"
    }


def run_test_with_params(params_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction pour lancer les tests directement avec des paramètres.
    Utilisée pour les endpoints qui acceptent des paramètres Pydantic.
    
    Args:
        params_dict (Dict): Paramètres du test (compatible avec ReidentificationParams)
        
    Returns:
        Dict: Résultats des tests
    """
    results = run_reidentification_tests(params_dict)
    
    return {
        "summary": results,
        "config_used": params_dict,
        "status": "completed"
    }


def _find_latest_anon_tables() -> list:
    """
    Trouve automatiquement les derniers fichiers anonymisés.
    
    Returns:
        list: Liste des chemins vers les fichiers anonymisés
    """
    # Chercher dans le dossier results
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    results_dir = os.path.join(base_dir, "results")
    
    if not os.path.exists(results_dir):
        return []
    
    # Chercher les dossiers anon_data_*
    anon_folders = sorted(
        [d for d in os.listdir(results_dir) if d.startswith("anon_data_") and d.split("_")[-1].isdigit()],
        key=lambda x: int(x.split("_")[-1]),
        reverse=True
    )
    
    if not anon_folders:
        return []
    
    # Récupérer les fichiers du dossier le plus récent
    latest_folder = os.path.join(results_dir, anon_folders[0])
    anon_files = glob.glob(os.path.join(latest_folder, "*.parquet"))
    
    return anon_files