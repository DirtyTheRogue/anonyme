import os
import json
import pandas as pd
from datetime import datetime

BASE_ARTEFACT_DIR = "artefacts"
_current_run_dir = None  
def get_timestamped_dir():
    """
    Crée un nouveau dossier avec un timestamp pour cette session d’anonymisation.
    """
    global _current_run_dir
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    _current_run_dir = os.path.join(BASE_ARTEFACT_DIR, timestamp)
    os.makedirs(_current_run_dir, exist_ok=True)

    latest_symlink = os.path.join(BASE_ARTEFACT_DIR, "latest")
    if os.path.islink(latest_symlink) or os.path.exists(latest_symlink):
        try:
            os.remove(latest_symlink)
        except Exception:
            pass
    try:
        os.symlink(_current_run_dir, latest_symlink)
    except Exception:
        pass  

    return _current_run_dir

def get_current_artefact_dir():
    """
    Retourne le dossier courant d’anonymisation (ou en crée un si non défini).
    """
    global _current_run_dir
    if _current_run_dir is None:
        return get_timestamped_dir()
    return _current_run_dir

def log_message(message: str):
    """
    Enregistre un message dans le fichier log de la session.
    """
    dir_path = get_current_artefact_dir()
    log_file = os.path.join(dir_path, "anonymization.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

def save_json(data: dict, filename: str):
    """
    Sauvegarde un dictionnaire JSON dans le dossier de session.
    """
    path = os.path.join(get_current_artefact_dir(), filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log_message(f"✅ JSON sauvegardé : {filename}")
    except Exception as e:
        log_message(f"❌ Erreur JSON : {e}")

def read_json(filename: str) -> dict:
    """
    Lit un JSON depuis le dossier de session.
    """
    path = os.path.join(get_current_artefact_dir(), filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_message(f"❌ Erreur lecture JSON : {e}")
    return {}

def save_dataframe(df: pd.DataFrame, filename: str):
    """
    Sauvegarde un DataFrame CSV dans le dossier de session.
    """
    path = os.path.join(get_current_artefact_dir(), filename)
    try:
        df.to_csv(path, index=False, sep=";", encoding="utf-8")
        log_message(f"✅ CSV exporté : {filename}")
    except Exception as e:
        log_message(f"❌ Erreur export CSV : {e}")
