import dash_bootstrap_components as dbc
from dash import html, dcc

def create_layout():
    return dbc.Container([
        # Header avec logo et boutons d'export
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(
                        src='/assets/logo.png',
                        className='logo-img'
                    ),
                    html.Div([
                        html.H1("DATA CARE", className='app-title'),
                        html.P("Optimizing Patient Care with Data Intelligence", className='app-subtitle')
                    ], className='header-text'),
                    # NOUVEAU : Boutons d'export
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-file-excel me-2"),
                            "Excel"
                        ], id='btn-download-excel', color="success", size="sm", className='export-btn'),
                        dbc.Button([
                            html.I(className="fas fa-file-code me-2"),
                            "HTML"
                        ], id='btn-download-html', color="info", size="sm", className='export-btn ms-2'),
                        dbc.Button([
                            html.I(className="fas fa-file-pdf me-2"),
                            "PDF"
                        ], id='btn-download-pdf', color="danger", size="sm", className='export-btn ms-2'),
                    ], className='export-buttons'),
                    # Downloads invisibles
                    dcc.Download(id="download-excel"),
                    dcc.Download(id="download-html"),
                    dcc.Download(id="download-pdf")
                ], className='header-container')
            ], width=12)
        ], className='header-row'),
        
        # NOUVEAU : Section Insights Clés
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-lightbulb me-2"),
                        "🎯 INSIGHTS CLÉS"
                    ], className='insights-header'),
                    dbc.CardBody([
                        html.Div(id='insights-content', children=[
                            html.P("Appliquez des filtres pour voir les insights spécifiques...", 
                                   className='text-muted text-center')
                        ])
                    ])
                ], className='insights-card')
            ], width=12)
        ], className='insights-row mb-3'),
        
        # Section des filtres
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🔍 Filtres d'Analyse", className='filter-title'),
                        
                        # Filtre Département
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-hospital me-2"),
                                "Département"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='dept-filter',
                                multi=True,
                                placeholder="Tous les départements",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),
                        
                        # Filtre Maladie
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-notes-medical me-2"),
                                "Pathologie"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='disease-filter',
                                multi=True,
                                placeholder="Toutes les pathologies",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),
                        
                        # Filtre Traitement
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-pills me-2"),
                                "Traitement"
                            ], className='filter-label'),
                            dcc.Dropdown(
                                id='treatment-filter',
                                multi=True,
                                placeholder="Tous les traitements",
                                className='custom-dropdown'
                            )
                        ], className='filter-group'),
                        
                        # Filtre Âge
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-user me-2"),
                                "Tranche d'âge"
                            ], className='filter-label'),
                            dcc.RangeSlider(
                                id='age-filter',
                                min=0,
                                max=100,
                                step=5,
                                value=[0, 100],
                                marks={i: f"{i}" for i in range(0, 101, 20)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], className='filter-group'),
                        
                        # Bouton Reset
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-redo me-2"),
                                "Réinitialiser"
                            ],
                                id='reset-filters',
                                color="secondary",
                                className='reset-btn w-100',
                                n_clicks=0
                            )
                        ], className='mt-3')
                    ])
                ], className='filter-card')
            ], md=3),
            
            # KPIs et graphiques
            dbc.Col([
                # KPIs avec tooltips
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-users kpi-icon"),
                                    html.Div([
                                        html.H3(id='total-patients', className='kpi-value'),
                                        html.P("Patients Total", className='kpi-label'),
                                        html.Small(id='trend-patients', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-blue', id='kpi-patients')
                    ], md=3),
                    dbc.Tooltip("Nombre total de patients analysés", target="kpi-patients", placement="top"),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-calendar-alt kpi-icon"),
                                    html.Div([
                                        html.H3(id='avg-duration', className='kpi-value'),
                                        html.P("Durée Moyenne (jours)", className='kpi-label'),
                                        html.Small(id='trend-duration', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-green', id='kpi-duration')
                    ], md=3),
                    dbc.Tooltip("Durée moyenne d'hospitalisation en jours", target="kpi-duration", placement="top"),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-euro-sign kpi-icon"),
                                    html.Div([
                                        html.H3(id='avg-cost', className='kpi-value'),
                                        html.P("Coût Moyen (€)", className='kpi-label'),
                                        html.Small(id='trend-cost', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-orange', id='kpi-cost')
                    ], md=3),
                    dbc.Tooltip("Coût moyen par patient en euros", target="kpi-cost", placement="top"),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="fas fa-chart-line kpi-icon"),
                                    html.Div([
                                        html.H3(id='total-cost', className='kpi-value'),
                                        html.P("Coût Total (€)", className='kpi-label'),
                                        html.Small(id='trend-total', className='kpi-trend')
                                    ])
                                ], className='kpi-content')
                            ])
                        ], className='kpi-card kpi-purple', id='kpi-total')
                    ], md=3),
                    dbc.Tooltip("Coût total de tous les patients", target="kpi-total", placement="top"),
                ], className='kpi-row'),
                
                # Graphiques - Ligne 1
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-bar me-2"),
                                "Répartition par Département"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='dept-chart', config={'displayModeBar': False}),
                                html.P("📊 Identifie la charge de travail par service médical", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-disease me-2"),
                                "Répartition par Pathologie"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='disease-chart', config={'displayModeBar': False}),
                                html.P("🏥 Montre les maladies les plus fréquentes nécessitant une hospitalisation", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6)
                ], className='chart-row'),
                
                # Graphiques - Ligne 2
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-money-bill-wave me-2"),
                                "Coût Moyen par Traitement"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='treatment-cost-chart', config={'displayModeBar': False}),
                                html.P("💊 Compare l'efficacité économique des différents traitements", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-clock me-2"),
                                "Durée de Séjour par Pathologie"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='duration-disease-chart', config={'displayModeBar': False}),
                                html.P("⏱️ Identifie les pathologies nécessitant les hospitalisations les plus longues", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6)
                ], className='chart-row'),
                
                # Graphiques - Ligne 3
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-users me-2"),
                                "Distribution par Âge et Sexe (Profil Patients)"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='age-gender-chart', config={'displayModeBar': False}),
                                html.P("👥 Analyse démographique : profil des patients par âge et sexe", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-calendar-week me-2"),
                                "Évolution Mensuelle des Admissions"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='monthly-admissions-chart', config={'displayModeBar': False}),
                                html.P("📈 Détecte les tendances saisonnières et aide à la planification", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6)
                ], className='chart-row'),
                
                # Graphiques - Ligne 4
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-exchange-alt me-2"),
                                "Flux Patients : Admissions vs Sorties"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='admission-vs-sortie-chart', config={'displayModeBar': False}),
                                html.P("🔄 Suit l'équilibre entre entrées et sorties pour anticiper la saturation", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-calendar-day me-2"),
                                "Jours de Sortie Préférés"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='sortie-weekday-chart', config={'displayModeBar': False}),
                                html.P("📅 Optimise les ressources en identifiant les jours de forte activité", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=6)
                ], className='chart-row'),
                
                # Graphiques - Ligne 5
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-scatter me-2"),
                                "Analyse Coût vs Durée de Séjour (Relation)"
                            ], className='card-header'),
                            dbc.CardBody([
                                dcc.Graph(id='cost-duration-scatter', config={'displayModeBar': False}),
                                html.P("💰 Révèle la corrélation entre durée d'hospitalisation et coûts - Détecte les anomalies", 
                                       className='chart-description')
                            ])
                        ], className='chart-card')
                    ], md=12)
                ], className='chart-row')
                
            ], md=9)
        ], className='main-row'),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P("© 2025 DATA CARE - Optimizing Patient Care with Data Intelligence", 
                           className='footer-text')
                ], className='footer')
            ], width=12)
        ])
        
    ], fluid=True, className='main-container')
