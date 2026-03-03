# =============================================================================
# LAYOUT.PY — Interface Utilisateur | Projet Énergie Solaire
# Auteur : SK | Dashboard Parc Photovoltaïque
# =============================================================================

import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def kpi_card(icon, title, value_id, unit, color, subtitle="", gradient_from="", gradient_to=""):
    """Génère une carte KPI animée."""
    return html.Div(
        className="kpi-card",
        style={"borderTop": f"4px solid {color}"},
        children=[
            html.Div(className="kpi-icon", style={"color": color}, children=html.I(className=icon)),
            html.Div(className="kpi-body", children=[
                html.P(title, className="kpi-title"),
                html.Div(className="kpi-value-row", children=[
                    html.Span(id=value_id, className="kpi-value"),
                    html.Span(unit, className="kpi-unit"),
                ]),
                html.P(subtitle, className="kpi-subtitle") if subtitle else None,
            ]),
        ]
    )


def section_header(icon, title, subtitle=""):
    """En-tête de section avec icône et description."""
    return html.Div(className="section-header", children=[
        html.Div(className="section-icon", children=html.I(className=icon)),
        html.Div([
            html.H4(title, className="section-title"),
            html.P(subtitle, className="section-subtitle") if subtitle else None,
        ])
    ])


def chart_card(title, subtitle, chart_id, height=400, extra_controls=None):
    """Carte contenant un graphique Plotly."""
    return html.Div(className="chart-card", children=[
        html.Div(className="chart-header", children=[
            html.Div([
                html.H5(title, className="chart-title"),
                html.P(subtitle, className="chart-subtitle"),
            ]),
            html.Div(extra_controls or [], className="chart-controls"),
        ]),
        dcc.Graph(
            id=chart_id,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                "toImageButtonOptions": {"format": "png", "filename": chart_id, "scale": 2},
            },
            style={"height": f"{height}px"},
        ),
    ])


# ─── NAVBAR ──────────────────────────────────────────────────────────────────

navbar = html.Div(
    id="navbar",
    className="navbar-solar",
    children=[
        # Logo + Titre
        html.Div(className="navbar-brand", children=[
            html.Img(src="/assets/logo.png", className="navbar-logo"),
            html.Div([
                html.Span("Solar", className="brand-solar"),
                html.Span("Dash", className="brand-dash"),
                html.P("Parc Photovoltaïque — Monitoring & Analyse", className="brand-subtitle"),
            ]),
        ]),

        # Navigation tabs
        html.Div(className="navbar-nav", children=[
            html.A([html.I(className="fas fa-chart-line me-2"), "Vue Globale"],
                   href="#overview", className="nav-link-solar active", id="nav-overview"),
            html.A([html.I(className="fas fa-bolt me-2"), "Production"],
                   href="#production", className="nav-link-solar", id="nav-production"),
            html.A([html.I(className="fas fa-thermometer-half me-2"), "Environnement"],
                   href="#environment", className="nav-link-solar", id="nav-env"),
            html.A([html.I(className="fas fa-exclamation-triangle me-2"), "Anomalies"],
                   href="#anomalies", className="nav-link-solar", id="nav-anomalies"),
            html.A([html.I(className="fas fa-file-export me-2"), "Rapport"],
                   href="#rapport", className="nav-link-solar", id="nav-rapport"),
        ]),

        # Badge status
        html.Div(className="navbar-status", children=[
            html.Div(className="status-dot"),
            html.Span("Système actif", className="status-text"),
        ]),
    ]
)


# ─── FILTRES ─────────────────────────────────────────────────────────────────

filters_panel = html.Div(
    id="filters-panel",
    className="filters-panel",
    children=[
        html.Div(className="filters-title", children=[
            html.I(className="fas fa-sliders-h me-2"),
            html.Span("FILTRES & CONTRÔLES"),
        ]),

        html.Div(className="filters-grid", children=[

            # Pays
            html.Div(className="filter-item", children=[
                html.Label([html.I(className="fas fa-globe me-2"), "Pays / Site"], className="filter-label"),
                dcc.Dropdown(
                    id="filter-country",
                    options=[
                        {"label": html.Span([flag]), "value": val}
                        for val, flag in {
                            "Norway": "🇳🇴 Norvège",
                            "Brazil": "🇧🇷 Brésil",
                            "India": "🇮🇳 Inde",
                            "Australia": "🇦🇺 Australie",
                        }.items()
                    ],
                    value=["Norway", "Brazil", "India", "Australia"],
                    multi=True,
                    placeholder="Sélectionner des pays...",
                    className="solar-dropdown",
                ),
            ]),

            # Mois
            html.Div(className="filter-item", children=[
                html.Label([html.I(className="fas fa-calendar me-2"), "Mois"], className="filter-label"),
                dcc.Dropdown(
                    id="filter-month",
                    options=[
                        {"label": name, "value": m}
                        for m, name in {
                            1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
                            5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
                            9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
                        }.items()
                    ],
                    value=list(range(1, 13)),
                    multi=True,
                    placeholder="Tous les mois",
                    className="solar-dropdown",
                ),
            ]),

            # Slider heure
            html.Div(className="filter-item filter-slider", children=[
                html.Label([html.I(className="fas fa-clock me-2"), "Plage horaire : ",
                            html.Span(id="slider-hour-label", className="slider-value")],
                           className="filter-label"),
                dcc.RangeSlider(
                    id="filter-hour",
                    min=0, max=23, step=1,
                    value=[0, 23],
                    marks={h: {"label": f"{h}h", "style": {"fontSize": "10px", "color": "#94A3B8"}}
                           for h in [0, 6, 10, 12, 14, 18, 23]},
                    tooltip={"placement": "bottom", "always_visible": False},
                    className="solar-slider",
                ),
            ]),

            # Bouton reset
            html.Div(className="filter-item filter-btn", children=[
                html.Button(
                    [html.I(className="fas fa-redo me-2"), "Réinitialiser"],
                    id="btn-reset-filters",
                    className="btn-reset",
                    n_clicks=0,
                ),
            ]),
        ]),
    ]
)


# ─── KPI CARDS ───────────────────────────────────────────────────────────────

kpi_section = html.Div(
    id="overview",
    className="kpi-section",
    children=[
        html.Div(className="section-intro", children=[
            html.Div(className="section-intro-icon", children="☀️"),
            html.Div([
                html.H2("Vue Globale du Parc Solaire", className="section-main-title"),
                html.P(
                    "Analyse complète de la production photovoltaïque — DC, AC, rendement, conditions environnementales et détection d'anomalies.",
                    className="section-main-subtitle"
                ),
            ])
        ]),

        html.Div(className="kpi-grid", children=[
            kpi_card("fas fa-solar-panel", "Production DC Totale",    "kpi-dc-total",   "kWh", "#F97316"),
            kpi_card("fas fa-bolt",         "Production AC Totale",    "kpi-ac-total",   "kWh", "#3B82F6"),
            kpi_card("fas fa-percentage",   "Rendement AC/DC Moyen",   "kpi-efficiency", "%",   "#10B981"),
            kpi_card("fas fa-sun",          "Irradiation Moyenne",     "kpi-irradiation","kW/m²","#FBBF24"),
            kpi_card("fas fa-thermometer",  "Temp. Module Moyenne",    "kpi-temp-mod",   "°C",  "#EF4444"),
            kpi_card("fas fa-exclamation",  "Anomalies Détectées",     "kpi-anomalies",  "",    "#EC4899"),
            kpi_card("fas fa-clock",        "Heure de Pic (DC max)",   "kpi-pic-hour",   "h",   "#8B5CF6"),
            kpi_card("fas fa-flag",         "Meilleur Site",           "kpi-best-site",  "",    "#06B6D4"),
        ]),
    ]
)


# ─── SECTION PRODUCTION ──────────────────────────────────────────────────────

section_production = html.Div(
    id="production",
    className="dashboard-section",
    children=[
        section_header(
            "fas fa-bolt",
            "Production Énergétique",
            "Analyse horaire et journalière de la puissance DC et AC générée par le parc PV"
        ),

        # Row 1 : DC/AC par heure + Cumulée journalière
        html.Div(className="charts-row", children=[
            html.Div(className="chart-col-60", children=[
                chart_card(
                    "⚡ Production DC vs AC par Heure",
                    "Tendance : Comparaison puissance directe (DC) et convertie (AC) — détection des pertes de conversion",
                    "chart-dc-ac-hour",
                    height=380,
                    extra_controls=[
                        dcc.Dropdown(
                            id="dd-dc-ac-country",
                            options=[{"label": "Tous les pays", "value": "ALL"},
                                     {"label": "🇳🇴 Norvège", "value": "Norway"},
                                     {"label": "🇧🇷 Brésil",  "value": "Brazil"},
                                     {"label": "🇮🇳 Inde",    "value": "India"},
                                     {"label": "🇦🇺 Australie","value": "Australia"}],
                            value="ALL",
                            clearable=False,
                            className="chart-dropdown",
                        )
                    ]
                ),
            ]),
            html.Div(className="chart-col-40", children=[
                chart_card(
                    "📈 Production Cumulée Journalière",
                    "Tendance : Progression du Daily_Yield au cours de la journée",
                    "chart-daily-cumul",
                    height=380,
                ),
            ]),
        ]),

        # Row 2 : Rendement par jour + Production mensuelle
        html.Div(className="charts-row", children=[
            html.Div(className="chart-col-50", children=[
                chart_card(
                    "🔋 Rendement AC/DC par Mois",
                    "Comparaison : Efficacité de conversion mois par mois — analyse de saisonnalité",
                    "chart-efficiency-month",
                    height=360,
                ),
            ]),
            html.Div(className="chart-col-50", children=[
                chart_card(
                    "🌍 Production Totale par Pays",
                    "Comparaison : Total_Yield cumulé par site — ranking des parcs solaires",
                    "chart-total-by-country",
                    height=360,
                ),
            ]),
        ]),

        # Row 3 : Area chart Total_Yield tendance
        html.Div(className="charts-row", children=[
            html.Div(className="chart-col-100", children=[
                chart_card(
                    "📊 Évolution du Total_Yield — Tendance Annuelle",
                    "Tendance : Croissance cumulative de la production depuis le début de l'année par site",
                    "chart-total-yield-trend",
                    height=350,
                ),
            ]),
        ]),
    ]
)


# ─── SECTION ENVIRONNEMENT ───────────────────────────────────────────────────

section_environment = html.Div(
    id="environment",
    className="dashboard-section",
    children=[
        section_header(
            "fas fa-leaf",
            "Conditions Environnementales",
            "Relation entre irradiation, températures ambiante/module et production — visualiser l'effet du climat"
        ),

        # Row 1 : Heatmap + Scatter température
        html.Div(className="charts-row", children=[
            html.Div(className="chart-col-55", children=[
                chart_card(
                    "🌡️ Heatmap Irradiation × Production (DC)",
                    "Relation : Intensité solaire vs puissance DC — carte de chaleur heure × mois",
                    "chart-heatmap",
                    height=420,
                ),
            ]),
            html.Div(className="chart-col-45", children=[
                chart_card(
                    "🌡️ Température Module vs DC Power",
                    "Relation : Impact de la surchauffe des panneaux sur la production",
                    "chart-temp-dc",
                    height=420,
                    extra_controls=[
                        dcc.Dropdown(
                            id="dd-scatter-country",
                            options=[{"label": "Tous pays", "value": "ALL"},
                                     {"label": "🇳🇴 Norvège", "value": "Norway"},
                                     {"label": "🇧🇷 Brésil",  "value": "Brazil"},
                                     {"label": "🇮🇳 Inde",    "value": "India"},
                                     {"label": "🇦🇺 Australie","value": "Australia"}],
                            value="ALL", clearable=False, className="chart-dropdown",
                        )
                    ]
                ),
            ]),
        ]),

        # Row 2 : Irradiation par heure + Corrélation
        html.Div(className="charts-row", children=[
            html.Div(className="chart-col-50", children=[
                chart_card(
                    "☀️ Profil d'Irradiation Horaire",
                    "Tendance : Ensoleillement moyen par heure — pic solaire et distribution",
                    "chart-irrad-hour",
                    height=340,
                ),
            ]),
            html.Div(className="chart-col-50", children=[
                chart_card(
                    "🌡️ Température Ambiante vs Module",
                    "Comparaison : Différence entre T° ambiante et T° panneau selon l'heure",
                    "chart-temp-compare",
                    height=340,
                ),
            ]),
        ]),
    ]
)


# ─── SECTION ANOMALIES ───────────────────────────────────────────────────────

section_anomalies = html.Div(
    id="anomalies",
    className="dashboard-section",
    children=[
        section_header(
            "fas fa-exclamation-triangle",
            "Détection des Anomalies",
            "Identifier les heures de production nulle pendant les plages solaires (8h–18h) — surveillance du parc"
        ),

        # Alerte résumé
        html.Div(id="anomaly-alert", className="anomaly-alert-box"),

        html.Div(className="charts-row", children=[
            html.Div(className="chart-col-65", children=[
                chart_card(
                    "⚠️ Anomalies — Production DC Nulle (8h–18h)",
                    "Anomalie : Points rouges = DC = 0 pendant les heures solaires — risque de panne ou ombrage",
                    "chart-anomalies-scatter",
                    height=400,
                ),
            ]),
            html.Div(className="chart-col-35", children=[
                chart_card(
                    "📊 Anomalies par Pays & Mois",
                    "Comparaison : Distribution des anomalies par site — quels parcs posent problème ?",
                    "chart-anomalies-bar",
                    height=400,
                ),
            ]),
        ]),

        # Tableau des anomalies
        html.Div(className="chart-card", children=[
            html.Div(className="chart-header", children=[
                html.H5("🔍 Détail des Anomalies Détectées", className="chart-title"),
                html.P("Heures avec DC_Power = 0 entre 8h et 18h — analyse détaillée", className="chart-subtitle"),
            ]),
            html.Div(id="table-anomalies-container", className="table-container"),
        ]),
    ]
)


# ─── SECTION RAPPORT ─────────────────────────────────────────────────────────

section_rapport = html.Div(
    id="rapport",
    className="dashboard-section",
    children=[
        section_header(
            "fas fa-file-alt",
            "Rapport & Export",
            "Téléchargez vos données filtrées et générez un rapport complet du parc photovoltaïque"
        ),

        # Boutons export
        html.Div(className="export-grid", children=[

            html.Div(className="export-card", children=[
                html.Div(className="export-icon", children=html.I(className="fas fa-file-excel")),
                html.H5("Export Excel", className="export-title"),
                html.P("Téléchargez les données filtrées au format Excel (.xlsx) directement sur votre PC",
                       className="export-desc"),
                html.Button(
                    [html.I(className="fas fa-download me-2"), "Télécharger Excel"],
                    id="btn-export-excel",
                    className="btn-export btn-excel",
                    n_clicks=0,
                ),
                dcc.Download(id="download-excel"),
            ]),

            html.Div(className="export-card", children=[
                html.Div(className="export-icon export-icon-pdf", children=html.I(className="fas fa-file-pdf")),
                html.H5("Export PDF", className="export-title"),
                html.P("Générez un rapport PDF complet avec KPIs et visualisations du parc solaire",
                       className="export-desc"),
                html.Button(
                    [html.I(className="fas fa-file-pdf me-2"), "Générer PDF"],
                    id="btn-export-pdf",
                    className="btn-export btn-pdf",
                    n_clicks=0,
                ),
                dcc.Download(id="download-pdf"),
            ]),

            html.Div(className="export-card", children=[
                html.Div(className="export-icon export-icon-html", children=html.I(className="fas fa-code")),
                html.H5("Rapport HTML Interactif", className="export-title"),
                html.P("Exportez le dashboard complet en HTML interactif — partageable sans installation",
                       className="export-desc"),
                html.Button(
                    [html.I(className="fas fa-external-link-alt me-2"), "Exporter HTML"],
                    id="btn-export-html",
                    className="btn-export btn-html",
                    n_clicks=0,
                ),
                dcc.Download(id="download-html"),
            ]),

        ]),

        # Prévisualisation du rapport
        html.Div(className="chart-card mt-4", children=[
            html.Div(className="chart-header", children=[
                html.H5("📋 Prévisualisation des Données Filtrées", className="chart-title"),
                html.Div(className="d-flex gap-2", children=[
                    html.Span(id="table-row-count", className="badge-count"),
                ]),
            ]),
            html.Div(id="table-preview-container", className="table-container"),
        ]),

        # Résumé statistique
        html.Div(className="charts-row mt-3", children=[
            html.Div(className="chart-col-100", children=[
                chart_card(
                    "📊 Résumé Statistique par Pays",
                    "Tableau de bord comparatif : production totale, rendement moyen, anomalies, pic horaire",
                    "chart-summary-stats",
                    height=320,
                ),
            ]),
        ]),

        # Toast notification
        html.Div(id="toast-export", className="toast-export"),
    ]
)


# ─── FOOTER ──────────────────────────────────────────────────────────────────

footer = html.Div(
    className="footer-solar",
    children=[
        html.Div(className="footer-content", children=[
            html.Div(className="footer-left", children=[
                html.Img(src="/assets/logo.png", className="footer-logo"),
                html.Div([
                    html.Span("SolarDash", className="footer-brand"),
                    html.P("Parc Photovoltaïque — Monitoring & Analyse de Production", className="footer-tagline"),
                ]),
            ]),
            html.Div(className="footer-center", children=[
                html.P("📊 35 136 mesures horaires | 🌍 4 pays | 📅 Année 2024",
                       className="footer-stats"),
                html.P("Variables : DC_Power · AC_Power · Irradiation · Température · Daily_Yield · Total_Yield",
                       className="footer-vars"),
            ]),
            html.Div(className="footer-right", children=[
                html.P("Réalisé par", className="footer-by"),
                html.Span("SK", className="footer-author"),
                html.P("Python 3.12 · Dash · Plotly · Pandas", className="footer-tech"),
            ]),
        ]),
    ]
)


# ─── LAYOUT PRINCIPAL ────────────────────────────────────────────────────────

layout = html.Div(
    id="main-container",
    className="main-container",
    children=[
        # Composant de téléchargement global
        dcc.Store(id="store-filtered-data"),
        dcc.Store(id="store-anomalies-data"),
        dcc.Interval(id="interval-update", interval=300000, n_intervals=0),  # refresh 5min

        # Navbar
        navbar,

        # Contenu principal
        html.Div(
            className="page-content",
            children=[
                # Bannière hero
                html.Div(className="hero-banner", children=[
                    html.Div(className="hero-content", children=[
                        html.Div(className="hero-badge", children=[
                            html.I(className="fas fa-solar-panel me-2"),
                            "Monitoring Parc Photovoltaïque — Données 2024"
                        ]),
                        html.H1(["Analyse de la ", html.Span("Production Solaire", className="hero-highlight")],
                                className="hero-title"),
                        html.P(
                            "Suivez, analysez et optimisez la performance de votre parc photovoltaïque — "
                            "35 136 mesures horaires · 4 sites internationaux · Détection d'anomalies en temps réel",
                            className="hero-subtitle"
                        ),
                        html.Div(className="hero-metrics", children=[
                            html.Div(className="hero-metric", children=[
                                html.Span("35 136", className="hero-metric-val"),
                                html.Span("mesures", className="hero-metric-lbl"),
                            ]),
                            html.Div(className="hero-sep"),
                            html.Div(className="hero-metric", children=[
                                html.Span("4", className="hero-metric-val"),
                                html.Span("pays", className="hero-metric-lbl"),
                            ]),
                            html.Div(className="hero-sep"),
                            html.Div(className="hero-metric", children=[
                                html.Span("14", className="hero-metric-val"),
                                html.Span("variables", className="hero-metric-lbl"),
                            ]),
                            html.Div(className="hero-sep"),
                            html.Div(className="hero-metric", children=[
                                html.Span("2024", className="hero-metric-val"),
                                html.Span("annuel", className="hero-metric-lbl"),
                            ]),
                        ]),
                    ]),
                    html.Div(className="hero-visual", children=[
                        html.Div(className="solar-animation", children=[
                            html.Div(className="sun-ring sun-ring-1"),
                            html.Div(className="sun-ring sun-ring-2"),
                            html.Div(className="sun-core", children="☀️"),
                        ]),
                    ]),
                ]),

                # Panel de filtres
                filters_panel,

                # Sections du dashboard
                kpi_section,
                html.Hr(className="section-divider"),
                section_production,
                html.Hr(className="section-divider"),
                section_environment,
                html.Hr(className="section-divider"),
                section_anomalies,
                html.Hr(className="section-divider"),
                section_rapport,
            ]
        ),

        # Footer
        footer,
    ]
)