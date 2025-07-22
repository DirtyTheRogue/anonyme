## 📌 **Projet d'Anonymisation de Données**

Ce projet permet d'anonymiser des fichiers CSV contenant des données sensibles. Il inclut une interface web permettant de sélectionner des fichiers et d'exécuter des règles d'anonymisation automatiquement.

---

## 🏰️ **Installation & Configuration**

### ⚙️ **1. Prérequis**
Avant de commencer, assure-toi d’avoir :
- **Python 3.8+** installé
- **Node.js & npm** installés
- **FastAPI** pour le backend
- **React.js** pour le frontend

---

## 🖥️ **Lancer le Backend (API FastAPI)**

### 📂 **1. Accéder au répertoire backend**
```bash
cd anonymization-backend
```

### 📦 **2. Installer les dépendances**
```bash
pip install -r requirements.txt
```

### 🚀 **3. Lancer le serveur FastAPI**
```bash
uvicorn main:app --reload / python -m uvicorn main:app --reload
```
Le backend est maintenant accessible sur **http://127.0.0.1:8000/**.

---

## 🌍 **Lancer le Frontend (React.js)**

### 📂 **1. Accéder au répertoire frontend**
```bash
cd anonymization-frontend
```

### 📦 **2. Installer les dépendances**
```bash
npm install
```

### 🚀 **3. Démarrer l’application React**
```bash
npm start
```
Le frontend est maintenant accessible sur **http://localhost:3000/**.

---

## 🔥 **Fonctionnalités Principales**
### **📁 1. Upload de fichiers**
- Envoie des fichiers CSV vers le dossier `uploads/` via le module d’extraction.
- Utilise l’endpoint **POST** `/upload`.

### **🔍 2. Extraction de colonnes**
- Permet de sélectionner et extraire des colonnes spécifiques des fichiers.
- Utilise l’endpoint **POST** `/run/extraction`.

### **🔒 3. Anonymisation des données**
- Applique des règles d’anonymisation sur les fichiers dans le dossier `data/`.
- Utilise l’endpoint **POST** `/run/anonymize`.

### **♻️ 4. Restauration des données originales**  (à faire)
- Restaure les fichiers originaux avant anonymisation.
- Utilise l’endpoint **POST** `/restore_backup`.

---

## 📌 **Endpoints API**
| Méthode  | Endpoint              | Description |
|----------|-----------------------|-------------|
| **POST** | `/register`            | Créer un compte |
| **POST** | `/login`               | Conncter son compte |
| **POST** | `/run/anonymize_all`   | Anonymise tous les fichiers du dossier `data/` et ses colonnes|
| **POST** | `/restore_backup`      | Restaure les fichiers avant anonymisation |
| **POST** | `/run/evaluation`      | Calcul les métriques |
| **POST** | `/run/extraction`      | Extrait des colonnes d’un fichier CSV |
| **POST** | `/run/anonymize`       | Anonymise les fichiers du dossier `data/` |
| **POST** | `/run/test`            | Test la reidentiication |
| **POST** | `/upload`              | Upload un fichier CSV |
| **POST** | `/get_columns`         | Recupere les colonnes |
| **POST** | `/read_csv`            | Lit un fichier CSV |
| **POST** | `/restore_backup`      | Restaure les fichiers avant anonymisation |

---

## 🎯 **Améliorations futures**
- Ajouter une **interface pour visualiser les données anonymisées**.
- Implémenter une authentification pour restreindre l’accès.
- Améliorer la gestion des erreurs côté frontend.
- Ameliorer l'affichage




