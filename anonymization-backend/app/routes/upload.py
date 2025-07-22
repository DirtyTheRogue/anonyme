import os
from fastapi import APIRouter, HTTPException, UploadFile, File

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        print(f"Tentative d'enregistrement du fichier : {file_path}")

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Fichier non enregistré sur le disque.")

        print(f"✅ Fichier enregistré avec succès : {file_path}")
        return {"message": "Fichier uploadé avec succès", "filepath": file_path}

    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement du fichier : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload : {str(e)}")
