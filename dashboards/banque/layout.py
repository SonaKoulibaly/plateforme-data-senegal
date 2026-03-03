"""
layout.py — Interface utilisateur du Dashboard Bancaire Sénégal
================================================================
Design : Luxe financier africain — Marine profond + Or sénégalais + Blanc cassé
Typographie : Syne (titres) + DM Sans (corps)
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

# ─── Palette ──────────────────────────────────────────────────────────────────
COLORS = {
    "navy"    : "#0A1628",
    "navy2"   : "#0F2040",
    "gold"    : "#D4A843",
    "gold2"   : "#F0C060",
    "cream"   : "#F8F4EE",
    "white"   : "#FFFFFF",
    "success" : "#2ECC71",
    "danger"  : "#E74C3C",
    "muted"   : "#8899AA",
    "card_bg" : "#111E35",
    "border"  : "#1E3050",
}

def kpi_card(title, value, icon, color=COLORS["gold"], subtitle=""):
    return dbc.Col(
        html.Div([
            html.Div([
                html.Span(icon, style={"fontSize":"28px"}),
                html.Div([
                    html.P(title, className="kpi-label"),
                    html.H3(value, className="kpi-value", style={"color": color}),
                    html.P(subtitle, className="kpi-sub") if subtitle else None,
                ]),
            ], className="kpi-inner"),
        ], className="kpi-card"),
        xs=12, sm=6, md=3,
    )


def create_layout(app, df, annees, banques, groupes):

    # Valeurs initiales pour les KPI du header
    last_year = max(annees)
    df_last   = df[df['annee'] == last_year]
    total_bilan   = df_last['bilan'].sum() / 1_000_000
    nb_banques    = df_last['sigle'].nunique()
    total_effectif = df_last['effectif'].sum()
    moy_fonds_propres = df_last['fonds_propres'].mean() / 1000

    return html.Div([

        # ── Store pour les données filtrées (partagé entre callbacks) ──
        dcc.Store(id="store-filtered"),

        # ══════════════════════════════════════════════════════════════
        # HEADER / NAVBAR
        # ══════════════════════════════════════════════════════════════
        html.Header([
            html.Div([
                # Logo
                html.Div([
                    html.Div([
                        html.Img(src="/assets/logo.png", style={"height":"46px","width":"46px","borderRadius":"8px","objectFit":"contain"}),
                        html.Div([
                            html.Span("BANQUE", className="logo-top"),
                            html.Span("SÉNÉGAL", className="logo-bottom"),
                        ], className="logo-text"),
                    ], className="logo-wrap"),
                ], className="header-logo"),

                # Titre central
                html.Div([
                    html.H1("Positionnement des Banques au Sénégal", className="header-title"),
                    html.P("Analyse & Data Visualisation · BCEAO · 2015–2022", className="header-sub"),
                ], className="header-center"),

                # Boutons téléchargement
                html.Div([
                    html.Button([html.Span("⬇"), " Excel"],
                        id="btn-download-excel", className="btn-dl btn-excel", n_clicks=0),
                    html.Button([html.Span("⬇"), " HTML"],
                        id="btn-download-html", className="btn-dl btn-html", n_clicks=0),
                    html.Button([html.Span("📄"), " Rapport PDF"],
                        id="btn-download-pdf", className="btn-dl btn-pdf", n_clicks=0),
                    dcc.Download(id="download-excel"),
                    dcc.Download(id="download-html"),
                    dcc.Download(id="download-pdf"),
                ], className="header-actions"),
            ], className="header-inner"),
        ], className="main-header"),

        # ══════════════════════════════════════════════════════════════
        # BANDEAU KPI GLOBAUX — dynamiques via callbacks
        # ══════════════════════════════════════════════════════════════
        html.Section([
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div([
                        html.Span("💰", style={"fontSize":"28px"}),
                        html.Div([
                            html.P("Total Actif Bancaire", className="kpi-label"),
                            html.H3(id="kpi-bilan", className="kpi-value", style={"color": COLORS["gold"]}),
                            html.P(id="kpi-bilan-sub", className="kpi-sub"),
                        ]),
                    ], className="kpi-inner"),
                ], className="kpi-card"), xs=12, sm=6, md=3),

                dbc.Col(html.Div([
                    html.Div([
                        html.Span("🏦", style={"fontSize":"28px"}),
                        html.Div([
                            html.P("Banques Actives", className="kpi-label"),
                            html.H3(id="kpi-banques", className="kpi-value", style={"color": "#5BC8F5"}),
                            html.P("Sur le marché sénégalais", className="kpi-sub"),
                        ]),
                    ], className="kpi-inner"),
                ], className="kpi-card"), xs=12, sm=6, md=3),

                dbc.Col(html.Div([
                    html.Div([
                        html.Span("👥", style={"fontSize":"28px"}),
                        html.Div([
                            html.P("Effectif Total", className="kpi-label"),
                            html.H3(id="kpi-effectif", className="kpi-value", style={"color": COLORS["success"]}),
                            html.P(id="kpi-effectif-sub", className="kpi-sub"),
                        ]),
                    ], className="kpi-inner"),
                ], className="kpi-card"), xs=12, sm=6, md=3),

                dbc.Col(html.Div([
                    html.Div([
                        html.Span("📊", style={"fontSize":"28px"}),
                        html.Div([
                            html.P("Fonds Propres Moy.", className="kpi-label"),
                            html.H3(id="kpi-fonds", className="kpi-value", style={"color": "#B87BFF"}),
                            html.P("Moyenne par banque", className="kpi-sub"),
                        ]),
                    ], className="kpi-inner"),
                ], className="kpi-card"), xs=12, sm=6, md=3),
            ], className="g-3"),
        ], className="kpi-section"),

        # ══════════════════════════════════════════════════════════════
        # PANNEAU DE FILTRES + BOUTON RESET
        # ══════════════════════════════════════════════════════════════
        html.Section([
            html.Div([
                html.Div([
                    html.Label("📅 PÉRIODE", className="filter-label"),
                    dcc.RangeSlider(
                        id="filter-annee",
                        min=min(annees), max=max(annees),
                        value=[min(annees), max(annees)],
                        marks={y: {"label": str(y), "style":{"color":COLORS["cream"],"fontSize":"11px"}} for y in annees},
                        step=1,
                        tooltip={"placement":"bottom","always_visible":False},
                        className="slider-custom",
                    ),
                ], className="filter-block filter-slider"),

                html.Div([
                    html.Label("🏦 BANQUES", className="filter-label"),
                    dcc.Dropdown(
                        id="filter-banque",
                        options=[{"label": b, "value": b} for b in banques],
                        value=None,
                        placeholder="Toutes les banques...",
                        multi=True,
                        className="dropdown-custom",
                        clearable=True,
                    ),
                ], className="filter-block"),

                html.Div([
                    html.Label("🌍 GROUPE", className="filter-label"),
                    dcc.Dropdown(
                        id="filter-groupe",
                        options=[{"label": g, "value": g} for g in groupes],
                        value=None,
                        placeholder="Tous les groupes...",
                        multi=True,
                        className="dropdown-custom",
                    ),
                ], className="filter-block"),

                html.Div([
                    html.Label("📊 INDICATEUR", className="filter-label"),
                    dcc.Dropdown(
                        id="filter-indicateur",
                        options=[
                            {"label": "🏛 Bilan (Total Actif)",      "value": "bilan"},
                            {"label": "💼 Emplois (Crédits)",         "value": "emploi"},
                            {"label": "💵 Ressources (Dépôts)",       "value": "ressources"},
                            {"label": "🏗 Fonds Propres",             "value": "fonds_propres"},
                            {"label": "📈 Produit Net Bancaire",      "value": "pnb"},
                            {"label": "💰 Résultat Net",              "value": "resultat_net"},
                            {"label": "⚖️ ROA (%)",                   "value": "roa"},
                            {"label": "📉 ROE (%)",                   "value": "roe"},
                            {"label": "🔄 Coefficient Exploitation",  "value": "cir"},
                        ],
                        value="bilan",
                        clearable=False,
                        className="dropdown-custom",
                    ),
                ], className="filter-block"),

                # ── Bouton Reset ──────────────────────────────────────
                html.Div([
                    html.Label("↺ RESET", className="filter-label"),
                    html.Button("🔄 Réinitialiser",
                        id="btn-reset-filters",
                        className="btn-reset",
                        n_clicks=0,
                    ),
                ], className="filter-block filter-reset"),

            ], className="filters-inner"),
        ], className="filters-section"),

        # ══════════════════════════════════════════════════════════════
        # ONGLETS PRINCIPAUX
        # ══════════════════════════════════════════════════════════════
        html.Section([
            dcc.Tabs(id="main-tabs", value="tab-marche", className="main-tabs", children=[

                # ── ONGLET 1 : VUE MARCHÉ ──────────────────────────
                dcc.Tab(label="🏛 Vue Marché", value="tab-marche", className="tab-item", selected_className="tab-selected"),

                # ── ONGLET 2 : COMPARAISON ─────────────────────────
                dcc.Tab(label="⚖️ Comparaison", value="tab-comparaison", className="tab-item", selected_className="tab-selected"),

                # ── ONGLET 3 : PERFORMANCE ─────────────────────────
                dcc.Tab(label="📈 Performance", value="tab-performance", className="tab-item", selected_className="tab-selected"),

                # ── ONGLET 4 : RATIOS FINANCIERS ───────────────────
                dcc.Tab(label="⚙️ Ratios Financiers", value="tab-ratios", className="tab-item", selected_className="tab-selected"),

                # ── ONGLET 5 : CARTE SÉNÉGAL ───────────────────────
                dcc.Tab(label="🗺 Carte Sénégal", value="tab-carte", className="tab-item", selected_className="tab-selected"),

                # ── ONGLET 6 : CLASSEMENT ──────────────────────────
                dcc.Tab(label="🏆 Classement", value="tab-classement", className="tab-item", selected_className="tab-selected"),
            ]),

            # Contenu dynamique des onglets
            html.Div(id="tabs-content", className="tabs-content"),

        ], className="main-tabs-section"),

        # ══════════════════════════════════════════════════════════════
        # SECTION ANALYSE BANQUE INDIVIDUELLE
        # ══════════════════════════════════════════════════════════════
        html.Section([
            html.Div([
                html.H2("🔍 Analyse Individuelle d'une Banque", className="section-title"),
                html.P("Sélectionnez une banque pour générer son profil complet et télécharger son rapport",
                       className="section-sub"),
            ], className="section-header"),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="select-banque-profil",
                        options=[{"label": b, "value": b} for b in banques],
                        value=banques[0] if banques else None,
                        clearable=False,
                        className="dropdown-custom dropdown-lg",
                        placeholder="Choisir une banque...",
                    ),
                ], md=4),
                dbc.Col([
                    dcc.Dropdown(
                        id="select-annee-profil",
                        options=[{"label": str(a), "value": a} for a in annees],
                        value=max(annees),
                        clearable=False,
                        className="dropdown-custom dropdown-lg",
                    ),
                ], md=2),
                dbc.Col([
                    html.Button("📄 Générer & Télécharger le Rapport PDF",
                        id="btn-generer-rapport", className="btn-primary-action", n_clicks=0),
                    dcc.Download(id="download-rapport-individuel"),
                ], md=3),
            ], className="g-3 mb-4"),

            # KPIs de la banque sélectionnée
            html.Div(id="profil-banque-kpi"),

            # Graphiques du profil
            dbc.Row([
                dbc.Col(dcc.Graph(id="graph-profil-evolution"), md=8),
                dbc.Col(dcc.Graph(id="graph-profil-radar"),     md=4),
            ], className="g-3"),

        ], className="individual-section"),

        # ══════════════════════════════════════════════════════════════
        # FOOTER
        # ══════════════════════════════════════════════════════════════
        html.Footer([
            html.Div([
                html.Span("🏦 Dashboard Banques Sénégal"),
                html.Span("·"),
                html.Span("Source : BCEAO · Base Sénégal 2015–2022"),
                html.Span("·"),
                html.Span("Python · Dash · MongoDB Atlas"),
            ], className="footer-inner"),
        ], className="main-footer"),

    ], className="app-wrapper")