# =============================================================
#  layout.py  —  Interface utilisateur complète
#  Projet : Analyse des Sinistres & Profil des Assurés
#  Auteur : Sona KOULIBALY
# =============================================================

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_layout():
    return dbc.Container([

        # ══════════════════════════════════════════════════════
        # HEADER
        # ══════════════════════════════════════════════════════
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Logo
                    html.Img(src='/assets/logo2.png', className='logo-img'),

                    # Titre & sous-titre
                    html.Div([
                        html.H1("AssurAnalytics", className='app-title'),
                        html.P(
                            "Analyse des Sinistres & Profil des Assurés — Mastère 2 Big Data & Data Stratégie",
                            className='app-subtitle'
                        )
                    ], className='header-text'),

                    # Boutons d'export
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-file-excel me-1"), "Excel"
                        ], id='btn-download-excel', color="success",
                           size="sm", className='export-btn'),

                        dbc.Button([
                            html.I(className="fas fa-file-code me-1"), "HTML"
                        ], id='btn-download-html', color="info",
                           size="sm", className='export-btn ms-2'),

                        dbc.Button([
                            html.I(className="fas fa-file-pdf me-1"), "PDF"
                        ], id='btn-download-pdf', color="danger",
                           size="sm", className='export-btn ms-2'),

                        html.A([
                            html.I(className="fas fa-sync-alt me-1"), "Actualiser"
                        ], href='/', className='btn btn-light btn-sm export-btn ms-3',
                           style={"textDecoration":"none", "fontWeight":"600", "fontSize":"0.76rem"}),

                    ], className='export-buttons'),

                    # Composants de téléchargement
                    dcc.Download(id="download-excel"),
                    dcc.Download(id="download-html"),
                    dcc.Download(id="download-pdf"),

                ], className='header-container')
            ], width=12)
        ], className='header-row'),

        # ══════════════════════════════════════════════════════
        # INSIGHTS CLÉS — STORYTELLING AUTOMATIQUE
        # ══════════════════════════════════════════════════════
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-lightbulb me-2"),
                        "🎯 INSIGHTS CLÉS — Les données parlent"
                    ], className='insights-header'),
                    dbc.CardBody([
                        html.Div(id='insights-content', children=[
                            html.P(
                                "⏳ Chargement des insights...",
                                className='text-muted text-center py-1'
                            )
                        ])
                    ], style={"padding": "12px 16px"})
                ], className='insights-card')
            ], width=12)
        ], className='insights-row mb-3'),

        # ══════════════════════════════════════════════════════
        # FILTRES (col 3) + CONTENU PRINCIPAL (col 9)
        # ══════════════════════════════════════════════════════
        dbc.Row([

            # ── COLONNE FILTRES ────────────────────────────────
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([

                        html.H5([
                            html.I(className="fas fa-sliders me-2"),
                            "Filtres d'Analyse"
                        ], className='filter-title'),

                        # Compteur actif
                        html.Div(id='filter-counter', className='filter-counter mb-3'),

                        # — Type d'assurance —
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-shield-halved me-1"),
                                "TYPE D'ASSURANCE"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='type-filter',
                                options=[
                                    {'label': '🚗 Auto',        'value': 'Auto'},
                                    {'label': '🏥 Santé',       'value': 'Santé'},
                                    {'label': '🏠 Habitation',  'value': 'Habitation'},
                                    {'label': '❤️ Vie',         'value': 'Vie'},
                                ],
                                multi=True,
                                placeholder="Tous les types",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),

                        # — Sexe —
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-venus-mars me-1"),
                                "SEXE"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='sexe-filter',
                                options=[
                                    {'label': '👨 Masculin', 'value': 'masculin'},
                                    {'label': '👩 Féminin',  'value': 'feminin'},
                                ],
                                multi=True,
                                placeholder="Tous",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),

                        # — Région —
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-map-location-dot me-1"),
                                "RÉGION"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='region-filter',
                                options=[
                                    {'label': '🏙️ Dakar',        'value': 'Dakar'},
                                    {'label': '🌿 Kaolack',      'value': 'Kaolack'},
                                    {'label': '🌊 Saint-Louis',  'value': 'Saint-Louis'},
                                    {'label': '🌳 Thiès',        'value': 'Thiès'},
                                ],
                                multi=True,
                                placeholder="Toutes les régions",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),

                        # — Nb sinistres —
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-exclamation-triangle me-1"),
                                "NB SINISTRES"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='sinistres-filter',
                                options=[
                                    {'label': '0 sinistre',   'value': '0'},
                                    {'label': '1 sinistre',   'value': '1'},
                                    {'label': '2 sinistres',  'value': '2'},
                                    {'label': '3 sinistres',  'value': '3'},
                                    {'label': '4+ sinistres', 'value': '4'},
                                ],
                                multi=True,
                                placeholder="Tous",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),

                        # — Tranche d'âge slider —
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-user me-1"),
                                "TRANCHE D'ÂGE"
                            ], className='filter-label'),
                            dcc.RangeSlider(
                                id='age-filter',
                                min=18, max=79, step=1,
                                value=[18, 79],
                                marks={18: '18', 35: '35', 50: '50', 65: '65', 79: '79'},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], className='filter-group'),

                        # — Bonus/Malus slider —
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-gauge me-1"),
                                "BONUS / MALUS"
                            ], className='filter-label'),
                            dcc.RangeSlider(
                                id='bm-filter',
                                min=0.5, max=1.5, step=0.05,
                                value=[0.5, 1.5],
                                marks={0.5: '0.5', 1.0: '1.0', 1.5: '1.5'},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], className='filter-group'),

                        # — Bouton reset —
                        dbc.Button([
                            html.I(className="fas fa-rotate-left me-2"),
                            "Réinitialiser les filtres"
                        ],
                            id='reset-filters',
                            color="secondary",
                            className='reset-btn w-100 mt-2',
                            n_clicks=0
                        ),

                        # Séparateur
                        html.Hr(style={"margin": "18px 0", "borderColor": "#e2e8f0"}),

                        # — Légende types —
                        html.Div([
                            html.P("Légende types", className='filter-label'),
                            html.Div([
                                html.Span("🚗 Auto",       style={"color":"#00C6FF","fontWeight":"600","fontSize":"0.78rem","display":"block"}),
                                html.Span("🏥 Santé",      style={"color":"#FFB300","fontWeight":"600","fontSize":"0.78rem","display":"block"}),
                                html.Span("🏠 Habitation", style={"color":"#00E676","fontWeight":"600","fontSize":"0.78rem","display":"block"}),
                                html.Span("❤️ Vie",        style={"color":"#FF5252","fontWeight":"600","fontSize":"0.78rem","display":"block"}),
                            ])
                        ])

                    ])
                ], className='filter-card')
            ], md=3),

            # ── COLONNE CONTENU PRINCIPAL ──────────────────────
            dbc.Col([

                # ── KPIs (4 cartes) ────────────────────────────
                dbc.Row([
                    # KPI 1 — Total Assurés
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div(html.I(className="fas fa-users"), className='kpi-icon-wrap'),
                                    html.Div([
                                        html.H3("—", id='kpi-total-assures', className='kpi-value'),
                                        html.P("Total Assurés", className='kpi-label'),
                                        html.Small("", id='trend-assures', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-blue', id='kpi-c-assures')
                    ], md=3),
                    dbc.Tooltip("Nombre total d'assurés dans la sélection courante",
                                target="kpi-c-assures", placement="top"),

                    # KPI 2 — Total Sinistres
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div(html.I(className="fas fa-triangle-exclamation"), className='kpi-icon-wrap'),
                                    html.Div([
                                        html.H3("—", id='kpi-total-sinistres', className='kpi-value'),
                                        html.P("Total Sinistres", className='kpi-label'),
                                        html.Small("", id='trend-sinistres', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-orange', id='kpi-c-sinistres')
                    ], md=3),
                    dbc.Tooltip("Nombre total de sinistres déclarés",
                                target="kpi-c-sinistres", placement="top"),

                    # KPI 3 — Coût moyen sinistre
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div(html.I(className="fas fa-euro-sign"), className='kpi-icon-wrap'),
                                    html.Div([
                                        html.H3("—", id='kpi-cout-moyen', className='kpi-value'),
                                        html.P("Coût Moyen Sinistre", className='kpi-label'),
                                        html.Small("", id='trend-cout', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-red', id='kpi-c-cout')
                    ], md=3),
                    dbc.Tooltip("Montant moyen des sinistres (assurés sinistrés uniquement)",
                                target="kpi-c-cout", placement="top"),

                    # KPI 4 — Prime Moyenne
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div(html.I(className="fas fa-chart-line"), className='kpi-icon-wrap'),
                                    html.Div([
                                        html.H3("—", id='kpi-prime-moy', className='kpi-value'),
                                        html.P("Prime Moyenne", className='kpi-label'),
                                        html.Small("", id='trend-prime', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-green', id='kpi-c-prime')
                    ], md=3),
                    dbc.Tooltip("Prime annuelle moyenne des assurés sélectionnés",
                                target="kpi-c-prime", placement="top"),

                ], className='mb-3 g-3'),

                # ── LIGNE KPI SECONDAIRES ──────────────────────
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Span("", id='kpi-taux-sinistralite', className='kpi-mini-value'),
                                    html.Span("Taux sinistralité", className='kpi-mini-label'),
                                ])
                            ])
                        ], className='kpi-mini kpi-mini-orange')
                    ], md=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Span("", id='kpi-ratio-sp', className='kpi-mini-value'),
                                    html.Span("Ratio S/P médian", className='kpi-mini-label'),
                                ])
                            ])
                        ], className='kpi-mini kpi-mini-red')
                    ], md=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Span("", id='kpi-bm-moyen', className='kpi-mini-value'),
                                    html.Span("B/M moyen", className='kpi-mini-label'),
                                ])
                            ])
                        ], className='kpi-mini kpi-mini-blue')
                    ], md=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Span("", id='kpi-pct-deficit', className='kpi-mini-value'),
                                    html.Span("% assurés déficitaires", className='kpi-mini-label'),
                                ])
                            ])
                        ], className='kpi-mini kpi-mini-purple')
                    ], md=3),
                ], className='mb-3 g-3'),

                # ══════════════════════════════════════════════
                # SECTION 1 — PROFIL DES ASSURÉS
                # ══════════════════════════════════════════════
                html.Div([
                    html.H6([
                        html.I(className="fas fa-users me-2"),
                        "SECTION 1 — PROFIL DES ASSURÉS"
                    ], className='section-title')
                ], className='section-header mb-2'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-pie me-2"),
                                "Répartition par Type d'Assurance"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-type-pie', config={'displayModeBar': False}),
                                html.P(
                                    "📊 Comparaison — Équilibre entre les 4 types (Auto, Santé, Habitation, Vie)",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-bar me-2"),
                                "Distribution des Âges par Type"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-age-dist', config={'displayModeBar': False}),
                                html.P(
                                    "📈 Tendance — Distribution étalée de 18 à 79 ans. Âge moyen : 49,8 ans",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),
                ], className='mb-3 g-3'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-venus-mars me-2"),
                                "Profil Démographique — Âge & Sexe"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-age-sexe', config={'displayModeBar': False}),
                                html.P(
                                    "👥 Comparaison — Prime moyenne par tranche d'âge & sexe",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-pie-chart me-2"),
                                "Répartition par Région"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-region-pie', config={'displayModeBar': False}),
                                html.P(
                                    "🗺️ Comparaison — Distribution des assurés par région sénégalaise",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),
                ], className='mb-3 g-3'),

                # ══════════════════════════════════════════════
                # SECTION 2 — ANALYSE DES SINISTRES
                # ══════════════════════════════════════════════
                html.Div([
                    html.H6([
                        html.I(className="fas fa-triangle-exclamation me-2"),
                        "SECTION 2 — ANALYSE DES SINISTRES"
                    ], className='section-title')
                ], className='section-header mb-2'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-map-marker-alt me-2"),
                                "Sinistres & Montants par Région"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-region-bar', config={'displayModeBar': False}),
                                html.P(
                                    "🗺️ Comparaison — Montants totaux sinistres par région",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-column me-2"),
                                "Fréquence des Sinistres Déclarés"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-sinistres-hist', config={'displayModeBar': False}),
                                html.P(
                                    "⚠️ Anomalie — Part importante d'assurés sans sinistre",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),
                ], className='mb-3 g-3'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-calendar-alt me-2"),
                                "Évolution Temporelle des Sinistres"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-time-series', config={'displayModeBar': False}),
                                html.P(
                                    "📅 Tendance — Suivi mensuel nb sinistres & montants sur 5 ans",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=12),
                ], className='mb-3 g-3'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-table-cells me-2"),
                                "Sinistres Moyens par Tranche d'Âge & Type"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-sinistres-age', config={'displayModeBar': False}),
                                html.P(
                                    "📊 Relation — Identifier les tranches d'âge les plus sinistrées par type",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=12),
                ], className='mb-3 g-3'),

                # ══════════════════════════════════════════════
                # SECTION 3 — RENTABILITÉ & TARIFICATION
                # ══════════════════════════════════════════════
                html.Div([
                    html.H6([
                        html.I(className="fas fa-euro-sign me-2"),
                        "SECTION 3 — RENTABILITÉ & TARIFICATION"
                    ], className='section-title')
                ], className='section-header mb-2'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-scatter me-2"),
                                "Prime vs Montant Sinistre (Rentabilité)"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-scatter-prime', config={'displayModeBar': False}),
                                html.P(
                                    "💰 Relation — Points au-dessus de la diagonale = assurés déficitaires",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-shield-halved me-2"),
                                "Coût Moyen Sinistre vs Prime par Type"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-cout-type', config={'displayModeBar': False}),
                                html.P(
                                    "💊 Comparaison — Coût moyen vs prime moyenne par type d'assurance",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),
                ], className='mb-3 g-3'),

                # ══════════════════════════════════════════════
                # SECTION 4 — PROFILS À RISQUE & BONUS/MALUS
                # ══════════════════════════════════════════════
                html.Div([
                    html.H6([
                        html.I(className="fas fa-fire me-2"),
                        "SECTION 4 — PROFILS À RISQUE & BONUS/MALUS"
                    ], className='section-title')
                ], className='section-header mb-2'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-fire me-2"),
                                "Heatmap Risque — Âge × Type d'Assurance"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-heatmap-risque', config={'displayModeBar': False}),
                                html.P(
                                    "🔥 Anomalie — Identification des profils à haut risque par tranche d'âge",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-gauge me-2"),
                                "Distribution du Bonus/Malus"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-bm-dist', config={'displayModeBar': False}),
                                html.P(
                                    "⚖️ Tendance — B/M moyen proche de l'équilibre (1.0)",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=6),
                ], className='mb-3 g-3'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-circle-dot me-2"),
                                "Nuage de Points — Bonus/Malus × Nb Sinistres × Montant"
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                dcc.Graph(id='chart-bm-scatter', config={'displayModeBar': False}),
                                html.P(
                                    "🔴 Relation — Corrélation B/M et fréquence/coût des sinistres. Détection profils extrêmes",
                                    className='chart-description'
                                )
                            ])
                        ], className='chart-card')
                    ], md=12),
                ], className='mb-3 g-3'),

                # ══════════════════════════════════════════════
                # SECTION 5 — TABLEAU DE DONNÉES
                # ══════════════════════════════════════════════
                html.Div([
                    html.H6([
                        html.I(className="fas fa-table me-2"),
                        "SECTION 5 — TABLEAU DES DONNÉES FILTRÉES"
                    ], className='section-title')
                ], className='section-header mb-2'),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.Div([
                                    html.Span([
                                        html.I(className="fas fa-database me-2"),
                                        "Données Détaillées des Assurés"
                                    ]),
                                    html.Small(id='table-count', className='ms-3 text-muted')
                                ], className='d-flex align-items-center justify-content-between')
                            ], className='card-header-custom'),
                            dbc.CardBody([
                                html.Div(id='data-table-container', style={"overflowX": "auto"})
                            ])
                        ], className='chart-card')
                    ], md=12)
                ], className='mb-4 g-3'),

            ], md=9)
        ], className='main-row'),

        # ══════════════════════════════════════════════════════
        # FOOTER
        # ══════════════════════════════════════════════════════
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P([
                        html.I(className="fas fa-shield-halved me-2"),
                        "© 2025 AssurAnalytics — Analyse des Sinistres & Profil des Assurés | ",
                        html.Span("Mastère 2 Big Data & Data Stratégie", style={"fontWeight": "700"}),
                        html.Span(" | Sona KOULIBALY", style={"opacity": "0.7"})
                    ], className='footer-text')
                ], className='footer')
            ], width=12)
        ])

    ], fluid=True, className='main-container')