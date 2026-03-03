"""
dashboards/assurance/app_assurance.py
Reproduction exacte du app.py original AssurAnalytics
"""
import os, sys
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import importlib.util

ASSURANCE_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_local(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_data():
    """Reproduction exacte du chargement original AssurAnalytics."""
    data_path = os.path.join(ASSURANCE_DIR, "data", "assurance_data_1000.csv")
    if not os.path.exists(data_path):
        for root, dirs, files in os.walk(ASSURANCE_DIR):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for f in files:
                if f.endswith(".csv"):
                    data_path = os.path.join(root, f)
                    break

    df = pd.read_csv(data_path, sep=';')

    # Conversion dates
    df['date_derniere_sinistre'] = pd.to_datetime(
        df['date_derniere_sinistre'], errors='coerce'
    )

    # Tranches d'âge
    df['tranche_age'] = pd.cut(
        df['age'],
        bins=[17, 25, 35, 45, 55, 65, 79],
        labels=['18-25', '26-35', '36-45', '46-55', '56-65', '66-79'],
        include_lowest=True
    )

    # Ratio sinistre / prime
    df['ratio_SP'] = (df['montant_sinistres'] / df['montant_prime']).round(2)

    # Catégorie bonus/malus
    df['bm_cat'] = pd.cut(
        df['bonus_malus'],
        bins=[0.4, 0.8, 1.0, 1.2, 1.6],
        labels=['Bonus fort', 'Bonus', 'Neutre', 'Malus']
    )

    # Année et mois du sinistre
    df['annee_sinistre'] = df['date_derniere_sinistre'].dt.year
    df['mois_sinistre']  = df['date_derniere_sinistre'].dt.to_period('M').astype(str)

    print(f"  ✅ Assurance — {len(df)} assurés chargés")
    return df


def init_dash(server):
    df = _load_data()

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/assurance/",
        assets_folder=os.path.join(ASSURANCE_DIR, "assets"),
        assets_url_path="/assurance/assets",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        ],
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"charset": "UTF-8"},
        ],
        title="AssurAnalytics — Analyse des Sinistres & Profil des Assurés",
    )

    layout_mod    = _import_local("assurance_layout",    os.path.join(ASSURANCE_DIR, "layout.py"))
    callbacks_mod = _import_local("assurance_callbacks", os.path.join(ASSURANCE_DIR, "callbacks.py"))

    dash_app.layout = layout_mod.create_layout()
    callbacks_mod.register_callbacks(dash_app, df)
    return dash_app