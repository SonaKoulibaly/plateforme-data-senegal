"""
dashboards/hospitalier/app_hospitalier.py
Reproduction exacte du app.py original DataCare
"""
import os, sys
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import importlib.util

HOSPITALIER_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_local(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_data():
    """Reproduction exacte du chargement original DataCare."""
    data_path = os.path.join(HOSPITALIER_DIR, "data", "hospital_data.csv")
    if not os.path.exists(data_path):
        for root, dirs, files in os.walk(HOSPITALIER_DIR):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for f in files:
                if f.endswith(".csv"):
                    data_path = os.path.join(root, f)
                    break

    # Reproduction exacte : tester encodages et séparateurs
    encodings  = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
    separators = [';', ',', '\t']
    df = None

    for encoding in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(data_path, encoding=encoding, sep=sep)
                if len(df.columns) > 1:
                    print(f"  ✅ Hospitalier — encodage {encoding}, sep='{sep}'")
                    break
            except:
                continue
        if df is not None and len(df.columns) > 1:
            break

    if df is None or len(df.columns) == 1:
        raise Exception("Impossible de charger hospital_data.csv")

    # Nettoyer noms de colonnes
    df.columns = df.columns.str.strip()

    # Convertir dates
    df['DateAdmission'] = pd.to_datetime(df['DateAdmission'], format='%d/%m/%Y', dayfirst=True)
    df['DateSortie']    = pd.to_datetime(df['DateSortie'],    format='%d/%m/%Y', dayfirst=True)

    print(f"  ✅ Hospitalier — {len(df)} patients chargés")
    return df


def init_dash(server):
    df = _load_data()

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/hospitalier/",
        assets_folder=os.path.join(HOSPITALIER_DIR, "assets"),
        assets_url_path="/hospitalier/assets",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
        ],
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        title="DATA CARE - Optimisation des Soins Hospitaliers",
    )

    layout_mod    = _import_local("hospitalier_layout",    os.path.join(HOSPITALIER_DIR, "layout.py"))
    callbacks_mod = _import_local("hospitalier_callbacks", os.path.join(HOSPITALIER_DIR, "callbacks.py"))

    dash_app.layout = layout_mod.create_layout()
    callbacks_mod.register_callbacks(dash_app, df)
    return dash_app