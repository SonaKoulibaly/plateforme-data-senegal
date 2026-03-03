# 🌍 Plateforme Data Sénégal

> Hub centralisé d'analyse de données multi-secteurs — 4 dashboards interactifs orchestrés par Flask

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![Dash](https://img.shields.io/badge/Dash-2.17-blue?logo=plotly)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)
![Render](https://img.shields.io/badge/Deploy-Render-purple?logo=render)

---

## 📋 Présentation

La **Plateforme Data Sénégal** est une application web full-stack développée dans le cadre du **Mastère 2 Big Data & Data Strategy**. Elle orchestre 4 dashboards analytiques sectoriels dans une seule interface Flask, partageant le même socle technique (MongoDB Atlas + Dash + Python).

### 🎯 Objectifs

- Centraliser 4 projets de data visualisation dans une seule plateforme
- Offrir un parcours utilisateur fluide entre les secteurs
- Déployer une solution professionnelle sur le cloud (Render)
- Démontrer la maîtrise de l'intégration multi-applications Flask + Dash

---

## 🏗 Architecture

```
PLATEFORME_DATA/
│
├── run.py                          ← Point d'entrée unique
├── flask_app.py                    ← Factory Flask + orchestration
├── requirements.txt
├── render.yaml                     ← Configuration déploiement Render
├── .gitignore
├── .env.example
│
├── templates/
│   └── landing.html                ← Page d'accueil (landing page)
│
├── static/
│   └── landing.css                 ← Style de la landing page
│
└── dashboards/
    ├── banque/                     ← Secteur Bancaire
    │   ├── app_banque.py           ← Adaptateur Flask→Dash
    │   ├── layout.py
    │   ├── callbacks.py
    │   ├── utils/pdf_generator.py
    │   └── assets/
    │
    ├── energie/                    ← Secteur Énergie Solaire
    │   ├── app_energie.py
    │   ├── layout.py
    │   ├── callbacks.py
    │   └── assets/
    │
    ├── assurance/                  ← Secteur Assurance
    │   ├── app_assurance.py
    │   ├── layout.py
    │   ├── callbacks.py
    │   └── assets/
    │
    └── hospitalier/                ← Secteur Hospitalier
        ├── app_hospitalier.py
        ├── layout.py
        ├── callbacks.py
        └── assets/
```

---

## 🗂 Les 4 Dashboards

### 🏦 Secteur Bancaire — Positionnement des Banques au Sénégal
| Élément | Détail |
|---|---|
| **Source** | BCEAO · Base Sénégal 2015–2022 + PDF BCEAO |
| **Données** | 24 banques · 188 enregistrements · MongoDB Atlas |
| **URL** | `/banque/` |
| **KPIs** | Total Actif · Banques Actives · Effectif · Fonds Propres |
| **Fonctionnalités** | Vue Marché · Comparaison · Performance · Ratios · Carte Dakar · Classement · Rapports PDF |

### ⚡ Secteur Énergie — SolarDash
| Élément | Détail |
|---|---|
| **Source** | Dataset parc photovoltaïque 2024 |
| **Données** | 35 136 mesures horaires · 4 sites internationaux · 14 variables |
| **URL** | `/energie/` |
| **KPIs** | Production AC/DC · Efficacité · Anomalies · Saisons |
| **Fonctionnalités** | Vue Globale · Production · Environnement · Anomalies · Rapport |

### 🛡 Secteur Assurance — AssurAnalytics
| Élément | Détail |
|---|---|
| **Source** | Dataset assurance vie & sinistres |
| **Données** | 1 000 assurés · 4 types d'assurance · Régions du Sénégal |
| **URL** | `/assurance/` |
| **KPIs** | Taux sinistralité · Ratio S/P · Coefficient B/M · Prime moyenne |
| **Fonctionnalités** | Insights clés · Profil assurés · Analyse sinistres · Recommandations tarifaires |

### 🏥 Secteur Hospitalier — DataCare
| Élément | Détail |
|---|---|
| **Source** | Dataset hospitalier patients |
| **Données** | 500 patients · 6 pathologies · Plusieurs départements |
| **URL** | `/hospitalier/` |
| **KPIs** | Patients · Durée moyenne · Coût moyen · Coût total |
| **Fonctionnalités** | Répartition départements · Pathologies · Tranches d'âge · Traitements |

---

## 🚀 Installation locale

### Prérequis
- Python 3.12+
- Compte MongoDB Atlas
- Git

### Étapes

**1. Cloner le repository**
```bash
git clone https://github.com/TON_USERNAME/plateforme-data-senegal.git
cd plateforme-data-senegal
```

**2. Créer l'environnement virtuel**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Installer les dépendances**
```bash
pip install -r requirements.txt
```

**4. Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos vraies valeurs
```

Contenu du `.env` :
```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/banque_senegal?retryWrites=true&w=majority
DB_NAME=banque_senegal
SECRET_KEY=votre_cle_secrete
DEBUG=True
PORT=8090
```

**5. Placer les données dans chaque dashboard**
```
dashboards/energie/data/salar_data.csv
dashboards/assurance/data/assurance_data_1000.csv
dashboards/hospitalier/data/hospital_data.csv
```

**6. Lancer la plateforme**
```bash
python run.py
```

**7. Ouvrir dans le navigateur**
```
http://localhost:8090/              ← Landing page
http://localhost:8090/banque/       ← Dashboard Bancaire
http://localhost:8090/energie/      ← Dashboard Énergie
http://localhost:8090/assurance/    ← Dashboard Assurance
http://localhost:8090/hospitalier/  ← Dashboard Hospitalier
```

---

## ☁️ Déploiement sur Render

### Étape 1 — Pousser sur GitHub
```bash
git add .
git commit -m "Plateforme Data Sénégal v1.0"
git push origin main
```

### Étape 2 — Créer le service sur Render
1. Aller sur [render.com](https://render.com)
2. **New → Web Service**
3. Connecter le repository GitHub
4. Render détecte automatiquement le `render.yaml`

### Étape 3 — Configurer les variables d'environnement
Dans Render → **Environment** → ajouter :

| Variable | Valeur |
|---|---|
| `MONGO_URI` | Votre URI MongoDB Atlas |
| `DB_NAME` | `banque_senegal` |
| `SECRET_KEY` | Clé secrète aléatoire |
| `DEBUG` | `False` |

### Étape 4 — Déployer
Cliquer **"Create Web Service"** → attendre 3–5 minutes.

URL finale : `https://plateforme-data-senegal1.onrender.com`

---

## 🛠 Stack Technique

| Technologie | Usage | Version |
|---|---|---|
| Python | Langage principal | 3.12 |
| Flask | Orchestration web | 3.0+ |
| Dash | Dashboards interactifs | 2.17+ |
| Plotly | Graphiques | 5.22+ |
| MongoDB Atlas | Base de données cloud | - |
| Pandas | Manipulation données | 2.2+ |
| ReportLab | Génération PDF | 4.2+ |
| Gunicorn | Serveur WSGI production | 21.2+ |
| Render | Hébergement cloud | - |

---

## 🔒 Sécurité

- Les secrets (`MONGO_URI`, `SECRET_KEY`) sont dans `.env` → **jamais commité sur GitHub**
- Le `.gitignore` exclut `.env`, `.venv/`, `__pycache__/`
- En production, les variables sont injectées via Render Environment
- Chaque dashboard est isolé via `importlib` pour éviter les conflits de modules

---

## 📁 Variables d'environnement

| Variable | Description | Obligatoire |
|---|---|---|
| `MONGO_URI` | URI de connexion MongoDB Atlas | ✅ Oui |
| `DB_NAME` | Nom de la base de données | ✅ Oui |
| `SECRET_KEY` | Clé secrète Flask | ✅ Oui |
| `DEBUG` | Mode debug (`True`/`False`) | Non |
| `PORT` | Port local (défaut : 8090) | Non |

---

## 👤 Auteur

**Sona KOULIBALY**
Mastère 2 Big Data & Data Strategy

---

## 📄 Licence


Projet académique — Mastère 2 Big Data & Data Strategy · 2025–2026
