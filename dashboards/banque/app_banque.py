"""
dashboards/banque/app_banque.py
Mise à jour v2.0 — Données 2015–2023 · 27 banques · Module ML
"""
import os, sys
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import importlib.util
from dotenv import load_dotenv

load_dotenv()

BANQUE_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_local(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_data():
    """Charge depuis MongoDB Atlas (banques_production) — fallback CSV."""
    mongo_uri = os.getenv("MONGO_URI", "")
    db_name   = os.getenv("DB_NAME", "banque_senegal")

    if mongo_uri and "<password>" not in mongo_uri:
        try:
            from pymongo import MongoClient
            client  = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            db      = client[db_name]
            records = list(db["banques_production"].find({}, {"_id": 0}))
            client.close()
            if records:
                df = pd.DataFrame(records)
                print(f"  ✅ Banque — MongoDB : {len(df)} enregistrements")
                return df
        except Exception as e:
            print(f"  ⚠️  Banque — MongoDB ({e}), fallback CSV")

    # Fallback CSV local
    for root, dirs, files in os.walk(BANQUE_DIR):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if f.endswith(".csv"):
                path = os.path.join(root, f)
                try:
                    df = pd.read_csv(path)
                    print(f"  ✅ Banque — {f} : {len(df)} lignes")
                    return df
                except:
                    pass

    print("  ❌ Banque — Aucune donnée disponible")
    return pd.DataFrame()


def init_dash(server):
    df      = _load_data()
    annees  = sorted(df['annee'].dropna().unique().astype(int).tolist()) if not df.empty else [2015, 2023]
    banques = sorted(df['sigle'].dropna().unique().tolist()) if not df.empty else []
    groupes = sorted(df['groupe_bancaire'].dropna().unique().tolist()) if not df.empty else []

    # S'assurer que ml_predictions est accessible depuis ce dossier
    ml_path = os.path.join(BANQUE_DIR, "ml_predictions.py")
    if os.path.exists(ml_path) and "ml_predictions" not in sys.modules:
        _import_local("ml_predictions", ml_path)

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/banque/",
        assets_folder=os.path.join(BANQUE_DIR, "assets"),
        assets_url_path="/banque/assets",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap",
        ],
        suppress_callback_exceptions=True,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        title="Banques Sénégal · Positionnement 2015–2023",
    )

    layout_mod    = _import_local("banque_layout",    os.path.join(BANQUE_DIR, "layout.py"))
    callbacks_mod = _import_local("banque_callbacks", os.path.join(BANQUE_DIR, "callbacks.py"))

    dash_app.layout = layout_mod.create_layout(dash_app, df, annees, banques, groupes)
    callbacks_mod.register_callbacks(dash_app, df)
    return dash_app
