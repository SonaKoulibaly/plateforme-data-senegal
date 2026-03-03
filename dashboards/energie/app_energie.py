"""
dashboards/energie/app_energie.py
Reproduction exacte du app.py original SolarDash
"""
import os, sys
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import importlib.util

ENERGIE_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_local(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_data():
    """Reproduction exacte du load_data() original de SolarDash."""
    # Chercher le CSV dans le dossier data/
    data_path = os.path.join(ENERGIE_DIR, "data", "salar_data.csv")
    if not os.path.exists(data_path):
        # Fallback : chercher partout
        for root, dirs, files in os.walk(ENERGIE_DIR):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for f in files:
                if f.endswith(".csv"):
                    data_path = os.path.join(root, f)
                    break

    df = pd.read_csv(data_path, sep=";")

    # Conversion datetime — exactement comme l'original
    df["DateTime"] = pd.to_datetime(df["DateTime"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["Date"]     = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

    df = df.dropna(subset=["DateTime"])
    df = df.sort_values("DateTime").reset_index(drop=True)

    # Rendement AC/DC
    df["Efficiency"] = np.where(
        df["DC_Power"] > 0,
        (df["AC_Power"] / df["DC_Power"] * 100).round(2),
        np.nan
    )

    # Perte de conversion
    df["Conversion_Loss"] = (df["DC_Power"] - df["AC_Power"]).round(3)

    # Tranche horaire
    def get_tranche(h):
        if   0 <= h < 6:  return "🌙 Nuit (0h–6h)"
        elif 6 <= h < 10: return "🌅 Matin (6h–10h)"
        elif 10<= h < 14: return "☀️ Midi (10h–14h)"
        elif 14<= h < 18: return "🌤️ Après-midi (14h–18h)"
        else:              return "🌆 Soir (18h–24h)"
    df["Tranche_Horaire"] = df["Hour"].apply(get_tranche)

    # Anomalie
    df["Anomalie"] = (
        (df["Hour"] >= 8) & (df["Hour"] <= 18) & (df["DC_Power"] == 0)
    )

    # Saison
    def get_saison(m):
        if   m in [12, 1, 2]: return "❄️ Hiver"
        elif m in [3, 4, 5]:  return "🌸 Printemps"
        elif m in [6, 7, 8]:  return "☀️ Été"
        else:                  return "🍂 Automne"
    df["Saison"] = df["Month"].apply(get_saison)

    df["Week"]    = df["DateTime"].dt.isocalendar().week.astype(int)
    df["DateStr"] = df["Date"].dt.strftime("%d/%m/%Y")

    print(f"  ✅ Énergie — {len(df)} lignes chargées")
    return df


def init_dash(server):
    df = _load_data()

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/energie/",
        assets_folder=os.path.join(ENERGIE_DIR, "assets"),
        assets_url_path="/energie/assets",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        ],
        suppress_callback_exceptions=True,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        title="☀️ SolarDash — Parc Photovoltaïque",
    )

    layout_mod    = _import_local("energie_layout",    os.path.join(ENERGIE_DIR, "layout.py"))
    callbacks_mod = _import_local("energie_callbacks", os.path.join(ENERGIE_DIR, "callbacks.py"))

    dash_app.layout = layout_mod.layout
    callbacks_mod.register_callbacks(dash_app, df)
    return dash_app