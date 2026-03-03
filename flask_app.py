"""
flask_app.py — Factory Flask · Plateforme Data Sénégal
=======================================================
Orchestre les 4 dashboards Dash dans une seule application Flask.
Chaque dashboard est monté sur son propre préfixe URL.
"""

import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()


def create_app():
    """
    Crée et configure l'application Flask avec les 4 dashboards Dash montés.
    Pattern : server Flask partagé par tous les dashboards.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("SECRET_KEY", "plateforme_data_senegal_2024")

    # ── Route Landing Page ─────────────────────────────────────────
    @app.route("/")
    def home():
        return render_template("landing.html")

    @app.route("/health")
    def health():
        return {"status": "ok", "plateforme": "Data Sénégal", "version": "1.0.0"}

    # ── Montage des dashboards Dash ────────────────────────────────
    _mount_dashboards(app)

    return app


def _mount_dashboards(server):
    """Monte les 4 dashboards Dash sur le serveur Flask."""

    # ── 1. Dashboard Bancaire ──────────────────────────────────────
    try:
        from dashboards.banque.app_banque import init_dash as init_banque
        init_banque(server)
        print("✅ Dashboard Banque monté sur /banque/")
    except Exception as e:
        print(f"⚠️  Dashboard Banque non disponible : {e}")

    # ── 2. Dashboard Énergie ───────────────────────────────────────
    try:
        from dashboards.energie.app_energie import init_dash as init_energie
        init_energie(server)
        print("✅ Dashboard Énergie monté sur /energie/")
    except Exception as e:
        print(f"⚠️  Dashboard Énergie non disponible : {e}")

    # ── 3. Dashboard Assurance ─────────────────────────────────────
    try:
        from dashboards.assurance.app_assurance import init_dash as init_assurance
        init_assurance(server)
        print("✅ Dashboard Assurance monté sur /assurance/")
    except Exception as e:
        print(f"⚠️  Dashboard Assurance non disponible : {e}")

    # ── 4. Dashboard Hospitalier ───────────────────────────────────
    try:
        from dashboards.hospitalier.app_hospitalier import init_dash as init_hospitalier
        init_hospitalier(server)
        print("✅ Dashboard Hospitalier monté sur /hospitalier/")
    except Exception as e:
        print(f"⚠️  Dashboard Hospitalier non disponible : {e}")