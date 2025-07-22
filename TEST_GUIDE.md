# 🧪 Guide de Test de l'API de Réidentification

## Étape 1 : Installation des Dépendances

### Option A : Environnement Virtuel (Recommandé)
```bash
cd /root/repo/anonymization-backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r tests/requirements.txt
```

### Option B : Installation Système (si autorisé)
```bash
pip3 install --break-system-packages -r tests/requirements.txt
```

### Option C : Installation Sélective
```bash
pip3 install --break-system-packages pandas fastapi pydantic sqlalchemy
```

## Étape 2 : Tests de Base

### Test 1 : Vérification des Imports
```bash
cd /root/repo/anonymization-backend
python3 -c "
import sys
sys.path.append('.')

# Test modèle Pydantic
from app.models.reidentification_model import ReidentificationParams
print('✅ Modèle Pydantic OK')

# Test service de pont
from app.services.reidentification_test import run_test, run_test_with_params
print('✅ Service de test OK')

# Test runner principal
from app.services.runner_test import run_reidentification_tests
print('✅ Runner principal OK')

print('🎉 Tous les imports fonctionnent!')
"
```

### Test 2 : Validation du Modèle Pydantic
```bash
python3 -c "
import sys
sys.path.append('.')
from app.models.reidentification_model import ReidentificationParams

# Créer un exemple de paramètres
params = ReidentificationParams(
    og_tables=['./data/test.csv'],
    anon_tables=['./results/test_anon.parquet'],
    ids=['id'],
    count_cols=[['col1']],
    group_cols=[['group1']],
    target=['target1'],
    exp_features=[['feature1']],
    group_var=['var1'],
    og_fusion_table=['./data/fusion.csv'],
    anon_fusion_table=['./results/fusion_anon.parquet'],
    fusion_columns_to_combine=[['col1', 'col2']],
    viz=True
)

print('✅ Modèle Pydantic validé avec succès')
print(f'📝 Paramètres: {params.dict()}')
"
```

## Étape 3 : Test de l'API (Serveur)

### Test 3 : Démarrage du Serveur
```bash
cd /root/repo/anonymization-backend

# Démarrer le serveur FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Le serveur devrait démarrer sur http://localhost:8000
```

### Test 4 : Vérification de l'API avec curl

#### Test du Health Check
```bash
curl http://localhost:8000/health
# Réponse attendue: {"status":"API is running"}
```

#### Test de l'Endpoint de Test avec Config
```bash
curl -X POST http://localhost:8000/reidentification/run \
  -H "Content-Type: application/json"

# Devrait utiliser config.json et lancer les tests
```

#### Test de l'Endpoint avec Paramètres Personnalisés
```bash
curl -X POST http://localhost:8000/reidentification/run/params \
  -H "Content-Type: application/json" \
  -d '{
    "og_tables": ["./data/data.csv"],
    "anon_tables": ["./results/data_anon.parquet"],
    "ids": ["id"],
    "count_cols": [["Nir"]],
    "group_cols": [["Nom", "Prenom"]],
    "target": ["Birth_rank"],
    "exp_features": [["Date_naissance"]],
    "group_var": ["Nom"],
    "og_fusion_table": ["./data/fusion.csv"],
    "anon_fusion_table": ["./results/fusion_anon.parquet"],
    "fusion_columns_to_combine": [["col1", "col2"]],
    "viz": true
  }'
```

#### Test des Exports
```bash
# Export résumé JSON
curl -X GET http://localhost:8000/reidentification/export/summary \
  --output test_results_summary.json

# Export artefacts ZIP
curl -X GET http://localhost:8000/reidentification/export/artifacts \
  --output test_artifacts.zip
```

## Étape 4 : Test avec Interface Web

### Test 5 : Documentation Interactive
```bash
# Ouvrir dans le navigateur
http://localhost:8000/docs

# Tester directement les endpoints depuis l'interface Swagger
```

### Test 6 : Interface Simple
```html
<!-- Créer un fichier test.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Test API Réidentification</title>
</head>
<body>
    <h1>Test API Réidentification</h1>
    
    <button onclick="testHealth()">Test Health</button>
    <button onclick="testParams()">Test avec Paramètres</button>
    
    <pre id="results"></pre>
    
    <script>
        async function testHealth() {
            const response = await fetch('http://localhost:8000/health');
            const data = await response.json();
            document.getElementById('results').textContent = JSON.stringify(data, null, 2);
        }
        
        async function testParams() {
            const params = {
                og_tables: ["./data/test.csv"],
                anon_tables: ["./results/test_anon.parquet"],
                ids: ["id"],
                count_cols: [["col1"]],
                group_cols: [["group1"]],
                target: ["target1"],
                exp_features: [["feature1"]],
                group_var: ["var1"],
                og_fusion_table: ["./data/fusion.csv"],
                anon_fusion_table: ["./results/fusion_anon.parquet"],
                fusion_columns_to_combine: [["col1", "col2"]],
                viz: true
            };
            
            const response = await fetch('http://localhost:8000/reidentification/run/params', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(params)
            });
            
            const data = await response.json();
            document.getElementById('results').textContent = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
```

## Étape 5 : Tests Avancés

### Test 7 : Vérification des Fichiers Générés
```bash
# Après avoir lancé un test, vérifier les fichiers créés
ls -la /root/repo/anonymization-backend/app/test_results/
cat /root/repo/anonymization-backend/app/test_results/test_results.json

# Vérifier si les artefacts sont créés
ls -la ./results/
```

### Test 8 : Test avec Données Réelles
```bash
# Créer des fichiers de test simples
mkdir -p ./data ./results

echo "id,nom,prenom
1,Dupont,Jean
2,Martin,Marie" > ./data/test.csv

echo "id,nom,prenom
1,XXXX,XXXX
2,XXXX,XXXX" > ./results/test_anon.csv
```

## 🐛 Résolution de Problèmes Courants

### Erreur "ModuleNotFoundError"
```bash
# Installer les dépendances manquantes
pip3 install pandas fastapi pydantic sqlalchemy uvicorn
```

### Erreur "config.json not found"
```bash
# Vérifier que config.json existe
ls -la /root/repo/anonymization-backend/config/config.json

# Créer un config.json minimal si absent
mkdir -p config
echo '{
  "test": {
    "og_tables": ["./data/data.csv"],
    "anon_tables": ["./results/data_anon.parquet"],
    "ids": ["id"],
    "count_cols": [["col1"]],
    "group_cols": [["group1"]],
    "target": ["target1"],
    "exp_features": [["feature1"]],
    "group_var": ["var1"],
    "og_fusion_table": ["./data/fusion.csv"],
    "anon_fusion_table": ["./results/fusion_anon.parquet"],
    "fusion_columns_to_combine": [["col1", "col2"]],
    "viz": true
  }
}' > config/config.json
```

### Erreur de CORS (depuis le frontend)
Le serveur est déjà configuré pour accepter les requêtes depuis `http://localhost:3000`.

## ✅ Checklist de Validation

- [ ] Dépendances installées
- [ ] Imports Python fonctionnent
- [ ] Serveur FastAPI démarre
- [ ] Health check répond
- [ ] Endpoints de test répondent
- [ ] Validation Pydantic fonctionne
- [ ] Export JSON fonctionne
- [ ] Export ZIP fonctionne
- [ ] Fichiers de résultats créés
- [ ] Interface Swagger accessible

## 🎯 Test Rapide (1 minute)

```bash
# Installation rapide
cd /root/repo/anonymization-backend
pip3 install --break-system-packages fastapi uvicorn pydantic

# Test rapide
python3 -c "import sys; sys.path.append('.'); from app.models.reidentification_model import ReidentificationParams; print('✅ OK')"

# Démarrer le serveur
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Test health
sleep 2
curl http://localhost:8000/health
```

Si le test rapide fonctionne, l'implémentation est opérationnelle ! 🎉