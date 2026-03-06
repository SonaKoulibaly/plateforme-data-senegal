# =============================================================
#  callbacks.py  —  Logique & Interactivité
#  Projet : Analyse des Sinistres & Profil des Assurés
#  Auteur : Sona KOULIBALY
# =============================================================

from dash import Input, Output, State, dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import io


# ════════════════════════════════════════════════════════════════
# PALETTES & HELPERS VISUELS
# ════════════════════════════════════════════════════════════════
TYPE_COLORS = {
    'Auto':       '#00C6FF',
    'Santé':      '#FFB300',
    'Habitation': '#00E676',
    'Vie':        '#FF5252',
}
REGION_COLORS = {
    'Dakar':       '#1565C0',
    'Thiès':       '#FFB300',
    'Kaolack':     '#00E676',
    'Saint-Louis': '#FF5252',
}
BM_COLORS = {
    'Bonus fort': '#00E676',
    'Bonus':      '#00C6FF',
    'Neutre':     '#FFB300',
    'Malus':      '#FF5252',
}

def base_layout(height=320):
    return dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#2d3748', size=11),
        margin=dict(l=30, r=30, t=25, b=25),
        height=height,
        hoverlabel=dict(
            bgcolor='white',
            bordercolor='#e2e8f0',
            font_size=12,
            font_family='Inter, sans-serif'
        )
    )


def register_callbacks(app, df):

    # ════════════════════════════════════════════════════════
    # FONCTION FILTRE CENTRAL
    # ════════════════════════════════════════════════════════
    def filter_data(type_vals, sexe_vals, region_vals, sinistres_vals, age_range, bm_range):
        f = df.copy()
        if type_vals:
            f = f[f['type_assurance'].isin(type_vals)]
        if sexe_vals:
            f = f[f['sexe'].isin(sexe_vals)]
        if region_vals:
            f = f[f['region'].isin(region_vals)]
        if sinistres_vals:
            nb_list = []
            for v in sinistres_vals:
                if v == '4':
                    nb_list += list(range(4, 100))
                else:
                    nb_list.append(int(v))
            f = f[f['nb_sinistres'].isin(nb_list)]
        if age_range:
            f = f[(f['age'] >= age_range[0]) & (f['age'] <= age_range[1])]
        if bm_range:
            f = f[(f['bonus_malus'] >= bm_range[0]) & (f['bonus_malus'] <= bm_range[1])]
        return f

    # ════════════════════════════════════════════════════════
    # INSIGHTS AUTOMATIQUES (STORYTELLING)
    # ════════════════════════════════════════════════════════
    def generate_insights(fdf, full_df):
        insights = []

        if len(fdf) == 0:
            return [html.P("⚠️ Aucun assuré ne correspond à ces filtres.", className='text-muted text-center')]

        # Sélection active
        if len(fdf) < len(full_df):
            pct = len(fdf) / len(full_df) * 100
            insights.append(('info', 'fas fa-filter',
                f'Sélection active',
                f'{len(fdf):,} assurés analysés ({pct:.1f}% du portefeuille total de {len(full_df):,})'))

        # Taux de sinistralité
        taux = (fdf['nb_sinistres'] > 0).mean() * 100
        taux_full = (full_df['nb_sinistres'] > 0).mean() * 100
        diff = taux - taux_full
        level = 'warning' if diff > 3 else ('success' if diff < -3 else 'info')
        arrow = '↗️ +' if diff > 0 else '↘️ '
        insights.append((level, 'fas fa-triangle-exclamation',
            f'Taux de sinistralité : {taux:.1f}%',
            f'{arrow}{diff:.1f}% vs moyenne globale ({taux_full:.1f}%) — '
            f'{(fdf["nb_sinistres"] == 0).mean()*100:.1f}% des assurés n\'ont aucun sinistre'))

        # Coût moyen
        df_sin = fdf[fdf['nb_sinistres'] > 0]
        if len(df_sin) > 0:
            cout = df_sin['montant_sinistres'].mean()
            cout_full = full_df[full_df['nb_sinistres'] > 0]['montant_sinistres'].mean()
            diff_c = (cout - cout_full) / cout_full * 100
            level_c = 'warning' if diff_c > 10 else ('success' if diff_c < -10 else 'info')
            insights.append((level_c, 'fas fa-euro-sign',
                f'Coût moyen sinistre : {cout:,.0f} €',
                f'{"↗️ +" if diff_c > 0 else "↘️ "}{diff_c:.1f}% vs moyenne globale ({cout_full:,.0f} €)'))

        # Ratio S/P
        ratio = fdf['ratio_SP'].median()
        pct_def = (fdf['ratio_SP'] > 1).mean() * 100
        level_r = 'warning' if pct_def > 85 else ('success' if pct_def < 70 else 'info')
        insights.append((level_r, 'fas fa-chart-line',
            f'Ratio Sinistre/Prime médian : {ratio:.1f}x',
            f'{pct_def:.1f}% des assurés génèrent plus de sinistres que leur prime ne couvre — '
            f'{"🚨 Alerte rentabilité" if pct_def > 85 else "✅ Rentabilité acceptable"}'))

        # Région la plus sinistrée
        reg_sin = fdf.groupby('region')['montant_sinistres'].sum()
        if len(reg_sin) > 0:
            top_r = reg_sin.idxmax()
            insights.append(('info', 'fas fa-map-location-dot',
                f'Région la plus coûteuse : {top_r}',
                f'{reg_sin[top_r]:,.0f} € de sinistres — '
                f'{reg_sin[top_r]/reg_sin.sum()*100:.1f}% du montant total de la sélection'))

        # Tranche d'âge à risque
        if 'tranche_age' in fdf.columns:
            age_r = fdf.groupby('tranche_age', observed=True)['nb_sinistres'].mean()
            if len(age_r) > 0:
                top_a = age_r.idxmax()
                insights.append(('warning', 'fas fa-user-shield',
                    f'Tranche à risque : {top_a} ans',
                    f'Moyenne de {age_r[top_a]:.3f} sinistre/assuré — profil prioritaire pour la tarification'))

        # Bonus/Malus
        pct_malus = (fdf['bonus_malus'] > 1.0).mean() * 100
        level_bm = 'warning' if pct_malus > 45 else 'success'
        insights.append((level_bm, 'fas fa-gauge-high',
            f'Coefficient B/M : {fdf["bonus_malus"].mean():.3f} moyen',
            f'{pct_malus:.1f}% des assurés en malus (B/M > 1.0) — '
            f'B/M moyen : {fdf["bonus_malus"].mean():.3f}'))

        # Recommandation tarifaire
        prime_m = fdf['montant_prime'].mean()
        cout_m  = fdf['montant_sinistres'].mean()
        if cout_m > prime_m * 3:
            insights.append(('danger', 'fas fa-lightbulb',
                '💡 RECOMMANDATION TARIFAIRE',
                f'Le coût moyen ({cout_m:,.0f} €) dépasse la prime de {cout_m/prime_m:.1f}x. '
                f'Révision des grilles tarifaires fortement recommandée.'))

        # Rendu HTML - CORRECTION : iterer sur insights (pas result)
        color_map = {'success': 'success', 'warning': 'warning',
                     'info': 'info', 'primary': 'primary', 'danger': 'danger'}
        result = []
        pairs = [insights[i:i+2] for i in range(0, len(insights), 2)]
        for pair in pairs:
            row_items = []
            for (level, icon, title, text) in pair:
                row_items.append(
                    html.Div([
                        html.I(className=f"{icon} me-2"),
                        html.Strong(title + " — "),
                        html.Span(text)
                    ], className=f'alert alert-{color_map.get(level,"secondary")} mb-2 py-2 px-3',
                       style={"fontSize": "0.79rem", "borderRadius": "8px",
                              "flex": "1", "border": "none", "marginBottom": "0"})
                )
            result.append(
                html.Div(row_items, style={"display": "flex", "gap": "8px", "marginBottom": "6px"})
            )
        return result if result else [html.P("OK aucun insight.", className='text-muted text-center')]

    # ════════════════════════════════════════════════════════
    # CALLBACK 0 — RESET FILTRES
    # ════════════════════════════════════════════════════════
    @app.callback(
        [Output('type-filter',      'value'),
         Output('sexe-filter',      'value'),
         Output('region-filter',    'value'),
         Output('sinistres-filter', 'value'),
         Output('age-filter',       'value'),
         Output('bm-filter',        'value')],
        Input('reset-filters', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_filters(n):
        return None, None, None, None, [18, 79], [0.5, 1.5]

    # ════════════════════════════════════════════════════════
    # CALLBACK PRINCIPAL — DASHBOARD COMPLET
    # ════════════════════════════════════════════════════════
    @app.callback(
        [
            # KPIs principaux
            Output('kpi-total-assures',    'children'),
            Output('kpi-total-sinistres',  'children'),
            Output('kpi-cout-moyen',       'children'),
            Output('kpi-prime-moy',        'children'),
            Output('trend-assures',        'children'),
            Output('trend-sinistres',      'children'),
            Output('trend-cout',           'children'),
            Output('trend-prime',          'children'),
            # KPIs secondaires
            Output('kpi-taux-sinistralite','children'),
            Output('kpi-ratio-sp',         'children'),
            Output('kpi-bm-moyen',         'children'),
            Output('kpi-pct-deficit',      'children'),
            # Compteur filtre
            Output('filter-counter',       'children'),
            # Insights
            Output('insights-content',     'children'),
            # Graphiques section 1
            Output('chart-type-pie',       'figure'),
            Output('chart-age-dist',       'figure'),
            Output('chart-age-sexe',       'figure'),
            Output('chart-region-pie',     'figure'),
            # Graphiques section 2
            Output('chart-region-bar',     'figure'),
            Output('chart-sinistres-hist', 'figure'),
            Output('chart-time-series',    'figure'),
            Output('chart-sinistres-age',  'figure'),
            # Graphiques section 3
            Output('chart-scatter-prime',  'figure'),
            Output('chart-cout-type',      'figure'),
            # Graphiques section 4
            Output('chart-heatmap-risque', 'figure'),
            Output('chart-bm-dist',        'figure'),
            Output('chart-bm-scatter',     'figure'),
            # Tableau
            Output('data-table-container', 'children'),
            Output('table-count',          'children'),
        ],
        [
            Input('type-filter',      'value'),
            Input('sexe-filter',      'value'),
            Input('region-filter',    'value'),
            Input('sinistres-filter', 'value'),
            Input('age-filter',       'value'),
            Input('bm-filter',        'value'),
        ]
    )
    def update_all(type_v, sexe_v, region_v, sin_v, age_v, bm_v):

        fdf = filter_data(type_v, sexe_v, region_v, sin_v, age_v, bm_v)
        n   = len(fdf)

        # ── Figure vide utilitaire ──
        def empty_fig(msg="Aucune donnée"):
            fig = go.Figure()
            fig.add_annotation(text=msg, xref="paper", yref="paper",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(size=13, color="#a0aec0"))
            fig.update_layout(**base_layout())
            return fig

        # ── KPIs principaux ────────────────────────────────
        df_sin = fdf[fdf['nb_sinistres'] > 0]
        kpi_assures   = f"{n:,}".replace(',', ' ')
        kpi_sinistres = f"{fdf['nb_sinistres'].sum():,}".replace(',', ' ')
        kpi_cout      = f"{df_sin['montant_sinistres'].mean():,.0f} €" if len(df_sin) else "— €"
        kpi_prime     = f"{fdf['montant_prime'].mean():,.0f} €" if n else "— €"

        # ── Tendances ──────────────────────────────────────
        def pct_vs(val, ref):
            if ref == 0: return ""
            d = (val - ref) / ref * 100
            return f"{'↗️ +' if d > 0 else '↘️ '}{d:.1f}% vs total"

        t_assures   = f"📊 {n/len(df)*100:.0f}% du portefeuille" if n < len(df) else "📊 Portefeuille complet"
        t_sinistres = pct_vs(fdf['nb_sinistres'].sum(), df['nb_sinistres'].sum())
        t_cout      = pct_vs(df_sin['montant_sinistres'].mean() if len(df_sin) else 0,
                             df[df['nb_sinistres'] > 0]['montant_sinistres'].mean())
        t_prime     = pct_vs(fdf['montant_prime'].mean() if n else 0, df['montant_prime'].mean())

        # ── KPIs secondaires ───────────────────────────────
        taux_sin  = f"{(fdf['nb_sinistres']>0).mean()*100:.1f}%" if n else "—"
        ratio_sp  = f"{fdf['ratio_SP'].median():.2f}x" if n else "—"
        bm_moyen  = f"{fdf['bonus_malus'].mean():.3f}" if n else "—"
        pct_def   = f"{(fdf['ratio_SP']>1).mean()*100:.1f}%" if n else "—"

        # ── Compteur filtre ────────────────────────────────
        if n == len(df):
            counter = html.Span(f"✅ {n:,} assurés — Aucun filtre actif",
                                style={"color":"#38a169","fontSize":"0.78rem","fontWeight":"600"})
        else:
            counter = html.Span(f"🔍 {n:,} assurés filtrés / {len(df):,}",
                                style={"color":"#1565C0","fontSize":"0.78rem","fontWeight":"600"})

        # ── Insights ───────────────────────────────────────
        insights_html = generate_insights(fdf, df)

        if n == 0:
            empty = empty_fig()
            return (kpi_assures, kpi_sinistres, kpi_cout, kpi_prime,
                    t_assures, t_sinistres, t_cout, t_prime,
                    taux_sin, ratio_sp, bm_moyen, pct_def,
                    counter, insights_html,
                    *[empty]*14,
                    html.P("Aucune donnée", className='text-muted'), "")

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 1 — PIE TYPE D'ASSURANCE
        # ══════════════════════════════════════════════════
        counts_t = fdf['type_assurance'].value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=counts_t.index,
            values=counts_t.values,
            hole=0.52,
            marker=dict(
                colors=[TYPE_COLORS.get(t, '#888') for t in counts_t.index],
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont_size=11,
            hovertemplate='<b>%{label}</b><br>%{value} assurés (%{percent})<extra></extra>'
        ))
        fig_pie.update_layout(
            showlegend=False,
            **{k: v for k, v in base_layout().items()},
            annotations=[dict(text=f"<b>{n}</b><br>assurés",
                              x=0.5, y=0.5, font_size=13, showarrow=False,
                              font_color='#2d3748')]
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 2 — HISTOGRAMME ÂGES PAR TYPE
        # ══════════════════════════════════════════════════
        fig_age = go.Figure()
        for t in ['Auto', 'Santé', 'Habitation', 'Vie']:
            sub = fdf[fdf['type_assurance'] == t]
            if sub.empty: continue
            fig_age.add_trace(go.Histogram(
                x=sub['age'], name=t, opacity=0.75, nbinsx=15,
                marker_color=TYPE_COLORS[t],
                hovertemplate=f'<b>{t}</b><br>Âge: %{{x}}<br>Nb: %{{y}}<extra></extra>'
            ))
        fig_age.update_layout(
            barmode='overlay', showlegend=True,
            **base_layout(),
            xaxis=dict(title='Âge', showgrid=False),
            yaxis=dict(title="Nb d'assurés", showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10)
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 3 — ÂGE & SEXE (prime moy par tranche/sexe)
        # ══════════════════════════════════════════════════
        grp_as = fdf.groupby(['tranche_age', 'sexe'], observed=True).agg(
            prime_moy=('montant_prime', 'mean'),
            nb=('id_assure', 'count')
        ).reset_index()

        fig_as = go.Figure()
        for sexe, color, label in [('masculin', '#1565C0', '👨 Masculin'),
                                    ('feminin', '#FF5252', '👩 Féminin')]:
            sub = grp_as[grp_as['sexe'] == sexe]
            fig_as.add_trace(go.Bar(
                x=sub['tranche_age'].astype(str),
                y=sub['prime_moy'],
                name=label,
                marker_color=color,
                text=[f"{v:,.0f}€" for v in sub['prime_moy']],
                textposition='outside',
                textfont_size=9,
                hovertemplate=f'<b>{label}</b><br>Tranche: %{{x}}<br>Prime moy: %{{y:,.0f}} €<extra></extra>'
            ))
        fig_as.update_layout(
            barmode='group', showlegend=True,
            **base_layout(),
            xaxis=dict(title="Tranche d'âge", showgrid=False),
            yaxis=dict(title="Prime moyenne (€)", showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10)
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 4 — PIE RÉGION
        # ══════════════════════════════════════════════════
        counts_r = fdf['region'].value_counts()
        fig_reg_pie = go.Figure(go.Pie(
            labels=counts_r.index,
            values=counts_r.values,
            hole=0.45,
            marker=dict(
                colors=[REGION_COLORS.get(r, '#888') for r in counts_r.index],
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont_size=11,
            hovertemplate='<b>%{label}</b><br>%{value} assurés (%{percent})<extra></extra>'
        ))
        fig_reg_pie.update_layout(showlegend=False, **base_layout())

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 5 — BAR SINISTRES PAR RÉGION
        # ══════════════════════════════════════════════════
        agg_reg = fdf.groupby('region').agg(
            nb_sin=('nb_sinistres', 'sum'),
            montant=('montant_sinistres', 'sum'),
            assures=('id_assure', 'count')
        ).reset_index().sort_values('montant', ascending=True)

        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            x=agg_reg['montant'], y=agg_reg['region'],
            orientation='h',
            marker_color=[REGION_COLORS.get(r, '#888') for r in agg_reg['region']],
            marker=dict(
                color=[REGION_COLORS.get(r, '#888') for r in agg_reg['region']],
                line=dict(color='white', width=1)
            ),
            text=[f"{v/1e6:.2f}M €" for v in agg_reg['montant']],
            textposition='outside',
            textfont_size=10,
            customdata=agg_reg[['nb_sin', 'assures']].values,
            hovertemplate='<b>%{y}</b><br>Montant: %{x:,.0f} €<br>Sinistres: %{customdata[0]}<br>Assurés: %{customdata[1]}<extra></extra>'
        ))
        if len(agg_reg) > 0:
            mean_m = agg_reg['montant'].mean()
            fig_reg.add_vline(x=mean_m, line_dash='dot', line_color='#FFB300',
                              annotation_text=f"Moy. {mean_m/1e6:.2f}M€",
                              annotation_font_color='#FFB300', annotation_font_size=9)
        fig_reg.update_layout(
            showlegend=False, **base_layout(),
            xaxis=dict(title='Montant total sinistres (€)', showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(showgrid=False)
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 6 — HISTOGRAMME NB SINISTRES
        # ══════════════════════════════════════════════════
        counts_sin = fdf['nb_sinistres'].value_counts().sort_index()
        pct_sin    = (counts_sin / n * 100).round(1)
        bar_cols   = {0: '#00E676', 1: '#00C6FF', 2: '#FFB300', 3: '#FF7043', 4: '#FF5252'}
        labels_sin = {0: '0 sinistre', 1: '1 sinistre', 2: '2 sinistres',
                      3: '3 sinistres', 4: '4 sinistres'}

        fig_hist = go.Figure(go.Bar(
            x=[labels_sin.get(i, f'{i} sin.') for i in counts_sin.index],
            y=counts_sin.values,
            marker_color=[bar_cols.get(i, '#FF5252') for i in counts_sin.index],
            marker=dict(line=dict(color='white', width=1.5)),
            text=[f'{v}<br>({p}%)' for v, p in zip(counts_sin.values, pct_sin)],
            textposition='outside', textfont_size=10,
            hovertemplate='<b>%{x}</b><br>%{y} assurés<extra></extra>'
        ))
        fig_hist.update_layout(
            showlegend=False, **base_layout(),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title="Nb d'assurés")
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 7 — SÉRIE TEMPORELLE
        # ══════════════════════════════════════════════════
        df_t = fdf[fdf['nb_sinistres'] > 0].dropna(subset=['date_derniere_sinistre']).copy()
        df_t['mois'] = df_t['date_derniere_sinistre'].dt.to_period('M').astype(str)
        agg_t = (df_t.groupby('mois')
                 .agg(nb=('id_assure', 'count'), montant=('montant_sinistres', 'sum'))
                 .reset_index().sort_values('mois'))

        fig_time = make_subplots(specs=[[{"secondary_y": True}]])
        if len(agg_t) > 0:
            fig_time.add_trace(go.Bar(
                x=agg_t['mois'], y=agg_t['nb'], name='Nb sinistres',
                marker_color='rgba(21,101,192,0.6)',
                hovertemplate='%{x}<br><b>%{y} sinistres</b><extra></extra>'
            ), secondary_y=False)
            fig_time.add_trace(go.Scatter(
                x=agg_t['mois'], y=agg_t['montant'],
                name='Montant (€)', mode='lines+markers',
                line=dict(color='#00C6FF', width=2.5),
                marker=dict(size=5, color='#00C6FF'),
                hovertemplate='%{x}<br><b>%{y:,.0f} €</b><extra></extra>'
            ), secondary_y=True)
        fig_time.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif', color='#2d3748', size=10),
            xaxis=dict(showgrid=False, tickangle=45, nticks=18, tickfont_size=8),
            yaxis=dict(title='Nb sinistres', showgrid=True, gridcolor='#e2e8f0'),
            yaxis2=dict(title='Montant (€)', showgrid=False),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10),
            margin=dict(l=30, r=50, t=30, b=60), height=320
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 8 — SINISTRES PAR ÂGE & TYPE (heatmap)
        # ══════════════════════════════════════════════════
        if 'tranche_age' in fdf.columns:
            piv = fdf.groupby(['tranche_age', 'type_assurance'], observed=True)['nb_sinistres'].mean().unstack(fill_value=0)
        else:
            piv = pd.DataFrame()

        if piv.empty:
            fig_sin_age = empty_fig()
        else:
            fig_sin_age = go.Figure()
            for t in piv.columns:
                fig_sin_age.add_trace(go.Bar(
                    x=piv.index.astype(str), y=piv[t],
                    name=t, marker_color=TYPE_COLORS.get(t, '#888'),
                    text=[f"{v:.2f}" for v in piv[t]],
                    textposition='outside', textfont_size=9,
                    hovertemplate=f'<b>{t}</b><br>Tranche: %{{x}}<br>Moy: %{{y:.3f}}<extra></extra>'
                ))
            fig_sin_age.update_layout(
                barmode='group', showlegend=True,
                **base_layout(),
                xaxis=dict(title="Tranche d'âge", showgrid=False),
                yaxis=dict(title="Sinistres moyens/assuré", showgrid=True, gridcolor='#e2e8f0'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10)
            )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 9 — SCATTER PRIME vs SINISTRE
        # ══════════════════════════════════════════════════
        fig_sc = go.Figure()
        for t in ['Auto', 'Santé', 'Habitation', 'Vie']:
            sub = fdf[fdf['type_assurance'] == t]
            if sub.empty: continue
            fig_sc.add_trace(go.Scatter(
                x=sub['montant_prime'], y=sub['montant_sinistres'],
                mode='markers', name=t,
                marker=dict(color=TYPE_COLORS[t], size=5, opacity=0.6,
                            line=dict(color='white', width=0.5)),
                customdata=sub[['age', 'region', 'nb_sinistres']].values,
                hovertemplate=(f'<b>{t}</b><br>Prime: %{{x:,.0f}} €<br>'
                               'Sinistre: %{y:,.0f} €<br>Âge: %{customdata[0]}<br>'
                               'Région: %{customdata[1]}<extra></extra>')
            ))
        max_p = fdf['montant_prime'].max() if n else 600
        fig_sc.add_trace(go.Scatter(
            x=[0, max_p], y=[0, max_p], mode='lines', name='Équilibre S=P',
            line=dict(dash='dot', color='#FFB300', width=2),
            hoverinfo='skip'
        ))
        fig_sc.update_layout(
            showlegend=True, **base_layout(),
            xaxis=dict(title='Prime annuelle (€)', showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(title='Montant sinistre (€)', showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10)
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 10 — COUT TYPE (barres groupées)
        # ══════════════════════════════════════════════════
        agg_ct = fdf.groupby('type_assurance').agg(
            cout_moy=('montant_sinistres', 'mean'),
            prime_moy=('montant_prime', 'mean')
        ).reset_index()

        fig_ct = go.Figure()
        fig_ct.add_trace(go.Bar(
            x=agg_ct['type_assurance'], y=agg_ct['cout_moy'],
            name='Coût moyen sinistre',
            marker_color='#FF5252',
            text=[f"{v:,.0f}€" for v in agg_ct['cout_moy']],
            textposition='outside', textfont_size=9,
            hovertemplate='<b>%{x}</b><br>Coût: %{y:,.0f} €<extra></extra>'
        ))
        fig_ct.add_trace(go.Bar(
            x=agg_ct['type_assurance'], y=agg_ct['prime_moy'],
            name='Prime moyenne',
            marker_color='#00C6FF',
            text=[f"{v:,.0f}€" for v in agg_ct['prime_moy']],
            textposition='outside', textfont_size=9,
            hovertemplate='<b>%{x}</b><br>Prime: %{y:,.0f} €<extra></extra>'
        ))
        fig_ct.update_layout(
            barmode='group', showlegend=True,
            **base_layout(),
            xaxis=dict(showgrid=False),
            yaxis=dict(title='Montant (€)', showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10)
        )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 11 — HEATMAP RISQUE ÂGE × TYPE
        # ══════════════════════════════════════════════════
        if 'tranche_age' in fdf.columns:
            hm = fdf.groupby(['tranche_age', 'type_assurance'], observed=True)['nb_sinistres'].mean().unstack(fill_value=0)
        else:
            hm = pd.DataFrame()

        if hm.empty:
            fig_hm = empty_fig()
        else:
            fig_hm = go.Figure(go.Heatmap(
                z=hm.values,
                x=hm.columns.tolist(),
                y=hm.index.astype(str).tolist(),
                colorscale='Blues',
                text=[[f"{v:.2f}" for v in row] for row in hm.values],
                texttemplate="%{text}",
                textfont_size=10,
                hovertemplate='<b>%{y} — %{x}</b><br>Moy sinistres: %{z:.3f}<extra></extra>',
                colorbar=dict(title="Moy.", thickness=12, len=0.8, tickfont_size=9)
            ))
            fig_hm.update_layout(
                **base_layout(),
                xaxis=dict(side='bottom'),
                yaxis=dict(autorange='reversed')
            )

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 12 — DISTRIBUTION BONUS/MALUS
        # ══════════════════════════════════════════════════
        if 'bm_cat' in fdf.columns:
            bm_counts = fdf['bm_cat'].value_counts()
            fig_bm = go.Figure(go.Pie(
                labels=bm_counts.index.tolist(),
                values=bm_counts.values,
                hole=0.45,
                marker=dict(
                    colors=[BM_COLORS.get(str(k), '#888') for k in bm_counts.index],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent+value',
                textfont_size=10,
                hovertemplate='<b>%{label}</b><br>%{value} assurés (%{percent})<extra></extra>'
            ))
        else:
            fig_bm = go.Figure(go.Histogram(
                x=fdf['bonus_malus'], nbinsx=20,
                marker_color='#1565C0',
                hovertemplate='B/M: %{x:.2f}<br>Nb: %{y}<extra></extra>'
            ))
        fig_bm.update_layout(showlegend=False, **base_layout())

        # ══════════════════════════════════════════════════
        # GRAPHIQUE 13 — SCATTER B/M × SINISTRES × MONTANT
        # ══════════════════════════════════════════════════
        fig_bm_sc = go.Figure()
        for t in ['Auto', 'Santé', 'Habitation', 'Vie']:
            sub = fdf[fdf['type_assurance'] == t]
            if sub.empty: continue
            fig_bm_sc.add_trace(go.Scatter(
                x=sub['bonus_malus'],
                y=sub['nb_sinistres'],
                mode='markers', name=t,
                marker=dict(
                    color=TYPE_COLORS[t],
                    size=np.clip(sub['montant_sinistres'] / 500, 4, 18),
                    opacity=0.55,
                    line=dict(color='white', width=0.5)
                ),
                customdata=sub[['montant_sinistres', 'age', 'region']].values,
                hovertemplate=(f'<b>{t}</b><br>B/M: %{{x:.2f}}<br>'
                               'Nb sinistres: %{y}<br>Montant: %{customdata[0]:,.0f} €<br>'
                               'Âge: %{customdata[1]} | %{customdata[2]}<extra></extra>')
            ))
        fig_bm_sc.add_vline(x=1.0, line_dash='dot', line_color='#FFB300',
                             annotation_text="Seuil Malus (1.0)",
                             annotation_font_color='#FFB300', annotation_font_size=9)
        fig_bm_sc.update_layout(
            showlegend=True, **base_layout(height=340),
            xaxis=dict(title='Coefficient Bonus/Malus', showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(title='Nb sinistres déclarés', showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font_size=10)
        )

        # ══════════════════════════════════════════════════
        # TABLEAU DE DONNÉES
        # ══════════════════════════════════════════════════
        cols_show = ['id_assure', 'age', 'sexe', 'type_assurance', 'region',
                     'duree_contrat', 'montant_prime', 'nb_sinistres',
                     'montant_sinistres', 'bonus_malus', 'bm_cat', 'ratio_SP']
        cols_ok = [c for c in cols_show if c in fdf.columns]
        df_table = fdf[cols_ok].head(100).copy()
        df_table['montant_prime']     = df_table['montant_prime'].round(0)
        df_table['montant_sinistres'] = df_table['montant_sinistres'].round(0)
        df_table['bonus_malus']       = df_table['bonus_malus'].round(3)
        df_table['ratio_SP']          = df_table['ratio_SP'].round(2)
        df_table['bm_cat']            = df_table['bm_cat'].astype(str)

        table = dash_table.DataTable(
            data=df_table.to_dict('records'),
            columns=[{'name': c, 'id': c} for c in cols_ok],
            page_size=15,
            sort_action='native',
            filter_action='native',
            style_table={'overflowX': 'auto'},
            style_cell={
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '12px',
                'padding': '6px 10px',
                'textAlign': 'left',
                'border': '1px solid #e2e8f0',
                'maxWidth': '140px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_header={
                'backgroundColor': '#1565C0',
                'color': 'white',
                'fontWeight': '700',
                'fontSize': '11px',
                'textTransform': 'uppercase',
                'letterSpacing': '0.06em',
                'border': '1px solid #1565C0',
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f7fafc'},
                {'if': {'filter_query': '{nb_sinistres} > 2'},
                 'backgroundColor': '#fff5f5', 'color': '#c53030'},
                {'if': {'filter_query': '{bonus_malus} > 1.2'},
                 'backgroundColor': '#fffbeb'},
                {'if': {'filter_query': '{ratio_SP} > 10'},
                 'backgroundColor': '#fff5f5'},
            ]
        )
        table_count = f"Affichage de {min(100, n)} lignes sur {n:,} au total"

        return (
            kpi_assures, kpi_sinistres, kpi_cout, kpi_prime,
            t_assures, t_sinistres, t_cout, t_prime,
            taux_sin, ratio_sp, bm_moyen, pct_def,
            counter, insights_html,
            # Section 1
            fig_pie, fig_age, fig_as, fig_reg_pie,
            # Section 2
            fig_reg, fig_hist, fig_time, fig_sin_age,
            # Section 3
            fig_sc, fig_ct,
            # Section 4
            fig_hm, fig_bm, fig_bm_sc,
            # Tableau
            table, table_count
        )

    # ════════════════════════════════════════════════════════
    # CALLBACK — EXPORT EXCEL
    # ════════════════════════════════════════════════════════
    @app.callback(
        Output('download-excel', 'data'),
        Input('btn-download-excel', 'n_clicks'),
        [State('type-filter',      'value'),
         State('sexe-filter',      'value'),
         State('region-filter',    'value'),
         State('sinistres-filter', 'value'),
         State('age-filter',       'value'),
         State('bm-filter',        'value')],
        prevent_initial_call=True
    )
    def download_excel(n, tv, sv, rv, sinv, av, bmv):
        fdf = filter_data(tv, sv, rv, sinv, av, bmv)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:

            # Feuille 1 — Données brutes
            cols_keep = ['id_assure', 'age', 'sexe', 'type_assurance', 'region',
                         'duree_contrat', 'montant_prime', 'nb_sinistres',
                         'montant_sinistres', 'bonus_malus', 'bm_cat', 'ratio_SP', 'tranche_age']
            fdf[[c for c in cols_keep if c in fdf.columns]].to_excel(
                writer, sheet_name='Données', index=False)

            # Feuille 2 — KPIs
            df_sin = fdf[fdf['nb_sinistres'] > 0]
            kpis = pd.DataFrame({
                'Indicateur': [
                    'Nb assurés analysés', 'Total sinistres', 'Taux sinistralité (%)',
                    'Coût moyen sinistre (€)', 'Prime moyenne (€)',
                    'Ratio S/P médian', '% déficitaires', 'B/M moyen'
                ],
                'Valeur': [
                    len(fdf), fdf['nb_sinistres'].sum(),
                    round((fdf['nb_sinistres'] > 0).mean() * 100, 2),
                    round(df_sin['montant_sinistres'].mean(), 0) if len(df_sin) else 0,
                    round(fdf['montant_prime'].mean(), 0),
                    round(fdf['ratio_SP'].median(), 2),
                    round((fdf['ratio_SP'] > 1).mean() * 100, 1),
                    round(fdf['bonus_malus'].mean(), 3),
                ]
            })
            kpis.to_excel(writer, sheet_name='KPIs', index=False)

            # Feuille 3 — Agrégat région
            reg = fdf.groupby('region').agg(
                assures=('id_assure', 'count'),
                sinistres=('nb_sinistres', 'sum'),
                montant_sin=('montant_sinistres', 'sum'),
                prime_moy=('montant_prime', 'mean'),
                bm_moyen=('bonus_malus', 'mean')
            ).round(2).reset_index()
            reg.to_excel(writer, sheet_name='Par Région', index=False)

            # Feuille 4 — Agrégat type
            typ = fdf.groupby('type_assurance').agg(
                assures=('id_assure', 'count'),
                sinistres=('nb_sinistres', 'sum'),
                cout_moy=('montant_sinistres', 'mean'),
                prime_moy=('montant_prime', 'mean'),
                ratio_sp_med=('ratio_SP', 'median')
            ).round(2).reset_index()
            typ.to_excel(writer, sheet_name='Par Type', index=False)

        buf.seek(0)
        fname = f"assuranalytics_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return dcc.send_bytes(buf.getvalue(), fname)

    # ════════════════════════════════════════════════════════
    # CALLBACK — EXPORT HTML
    # ════════════════════════════════════════════════════════
    @app.callback(
        Output('download-html', 'data'),
        Input('btn-download-html', 'n_clicks'),
        [State('type-filter',      'value'),
         State('sexe-filter',      'value'),
         State('region-filter',    'value'),
         State('sinistres-filter', 'value'),
         State('age-filter',       'value'),
         State('bm-filter',        'value')],
        prevent_initial_call=True
    )
    def download_html(n, tv, sv, rv, sinv, av, bmv):
        import plotly.io as pio
        fdf = filter_data(tv, sv, rv, sinv, av, bmv)
        df_sin = fdf[fdf['nb_sinistres'] > 0]
        cout_str = f"{df_sin['montant_sinistres'].mean():,.0f} €" if len(df_sin) else "—"

        # 3 figures clés
        ct = fdf['type_assurance'].value_counts()
        f1 = go.Figure(go.Pie(labels=ct.index, values=ct.values, hole=0.4,
                               marker_colors=[TYPE_COLORS.get(t, '#888') for t in ct.index]))
        f1.update_layout(title="Répartition par type", height=350,
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

        ar = fdf.groupby('region')['montant_sinistres'].sum().reset_index().sort_values('montant_sinistres')
        f2 = go.Figure(go.Bar(x=ar['montant_sinistres'], y=ar['region'], orientation='h',
                               marker_color=[REGION_COLORS.get(r, '#888') for r in ar['region']]))
        f2.update_layout(title="Montants par région", height=350,
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

        if 'tranche_age' in fdf.columns:
            pv = fdf.groupby(['tranche_age'], observed=True)['nb_sinistres'].mean().reset_index()
            f3 = go.Figure(go.Bar(x=pv['tranche_age'].astype(str), y=pv['nb_sinistres'],
                                   marker_color='#1565C0'))
            f3.update_layout(title="Sinistres moyens par tranche d'âge", height=350,
                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        else:
            f3 = go.Figure()

        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Rapport AssurAnalytics</title>
<style>
  body {{ font-family: Inter, Arial, sans-serif; background: #f0f4f8; color: #2d3748; margin: 0; }}
  .header {{ background: linear-gradient(135deg,#0D47A1,#1976D2); color: white; padding: 28px 40px; }}
  h1 {{ margin: 0; font-size: 1.8rem; }} p.sub {{ margin: 4px 0 0; opacity: .8; font-size: .85rem; }}
  .kpis {{ display: flex; gap: 16px; padding: 20px 40px; flex-wrap: wrap; }}
  .kpi {{ background: white; border-radius: 12px; padding: 16px 24px; flex: 1; min-width: 160px;
          box-shadow: 0 2px 10px rgba(0,0,0,.08); text-align: center; }}
  .kpi-v {{ font-size: 1.6rem; font-weight: 800; color: #1565C0; }}
  .kpi-l {{ font-size: .72rem; color: #718096; text-transform: uppercase; letter-spacing: .06em; }}
  .insight {{ background: white; margin: 0 40px 8px; padding: 12px 16px; border-radius: 8px;
              border-left: 4px solid #1565C0; font-size: .83rem; box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
  .graphs {{ padding: 20px 40px; }}
  footer {{ background: #0D47A1; color: rgba(255,255,255,.8); text-align: center; padding: 14px; font-size:.75rem; margin-top:20px; }}
</style>
</head>
<body>
<div class="header">
  <h1>📊 AssurAnalytics — Rapport d'Analyse</h1>
  <p class="sub">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} | {len(fdf)} assurés analysés</p>
</div>
<div class="kpis">
  <div class="kpi"><div class="kpi-v">{len(fdf):,}</div><div class="kpi-l">Total assurés</div></div>
  <div class="kpi"><div class="kpi-v">{fdf['nb_sinistres'].sum():,}</div><div class="kpi-l">Total sinistres</div></div>
  <div class="kpi"><div class="kpi-v">{cout_str}</div><div class="kpi-l">Coût moyen sinistre</div></div>
  <div class="kpi"><div class="kpi-v">{fdf['montant_prime'].mean():,.0f} €</div><div class="kpi-l">Prime moyenne</div></div>
  <div class="kpi"><div class="kpi-v">{(fdf['nb_sinistres']>0).mean()*100:.1f}%</div><div class="kpi-l">Taux sinistralité</div></div>
  <div class="kpi"><div class="kpi-v">{fdf['ratio_SP'].median():.2f}x</div><div class="kpi-l">Ratio S/P médian</div></div>
</div>
<div class="insight">📌 <strong>{(fdf['nb_sinistres']==0).mean()*100:.1f}%</strong> des assurés n'ont déclaré aucun sinistre.</div>
<div class="insight">⚠️ Ratio S/P médian : <strong>{fdf['ratio_SP'].median():.1f}x</strong>. {(fdf['ratio_SP']>1).mean()*100:.1f}% des assurés sont déficitaires.</div>
<div class="insight">💡 B/M moyen : <strong>{fdf['bonus_malus'].mean():.3f}</strong> — {(fdf['bonus_malus']>1).mean()*100:.1f}% des assurés en malus.</div>
<div class="graphs">
  <h2>Répartition par type d'assurance</h2>
  {pio.to_html(f1, full_html=False, include_plotlyjs='cdn')}
  <h2>Montants des sinistres par région</h2>
  {pio.to_html(f2, full_html=False, include_plotlyjs=False)}
  <h2>Sinistres moyens par tranche d'âge</h2>
  {pio.to_html(f3, full_html=False, include_plotlyjs=False)}
</div>
<footer>AssurAnalytics · Mastère 2 Big Data & Data Stratégie · Sona KOULIBALY · {len(fdf)} assurés analysés</footer>
</body>
</html>"""

        fname = f"rapport_assuranalytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        return dcc.send_bytes(html_content.encode('utf-8'), fname)

    # ════════════════════════════════════════════════════════
    # CALLBACK — EXPORT PDF
    # ════════════════════════════════════════════════════════
    @app.callback(
        Output('download-pdf', 'data'),
        Input('btn-download-pdf', 'n_clicks'),
        [State('type-filter',      'value'),
         State('sexe-filter',      'value'),
         State('region-filter',    'value'),
         State('sinistres-filter', 'value'),
         State('age-filter',       'value'),
         State('bm-filter',        'value')],
        prevent_initial_call=True
    )
    def download_pdf(n, tv, sv, rv, sinv, av, bmv):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            fdf = filter_data(tv, sv, rv, sinv, av, bmv)
            df_sin = fdf[fdf['nb_sinistres'] > 0]

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4,
                                    leftMargin=0.7*inch, rightMargin=0.7*inch,
                                    topMargin=0.7*inch, bottomMargin=0.7*inch)
            elements = []
            styles = getSampleStyleSheet()

            title_s  = ParagraphStyle('T', parent=styles['Heading1'], fontSize=20,
                                       textColor=colors.HexColor('#1565C0'), alignment=TA_CENTER, spaceAfter=6)
            sub_s    = ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
                                       textColor=colors.HexColor('#718096'), alignment=TA_CENTER, spaceAfter=20)
            section_s = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=13,
                                        textColor=colors.HexColor('#1565C0'), spaceBefore=16, spaceAfter=8)
            body_s   = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, spaceAfter=4)

            elements.append(Paragraph("RAPPORT ASSURANALYTICS", title_s))
            elements.append(Paragraph(
                f"Analyse des Sinistres & Profil des Assurés<br/>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                sub_s))

            # KPIs
            elements.append(Paragraph("Indicateurs Clés", section_s))
            cout_str = f"{df_sin['montant_sinistres'].mean():,.0f} €" if len(df_sin) else "—"
            kpi_data = [
                ['Indicateur', 'Valeur'],
                ["Nb assurés analysés",        f"{len(fdf):,}"],
                ["Total sinistres",             f"{fdf['nb_sinistres'].sum():,}"],
                ["Taux de sinistralité",        f"{(fdf['nb_sinistres']>0).mean()*100:.1f}%"],
                ["Coût moyen sinistre",         cout_str],
                ["Prime moyenne",               f"{fdf['montant_prime'].mean():,.0f} €"],
                ["Ratio S/P médian",            f"{fdf['ratio_SP'].median():.2f}x"],
                ["% assurés déficitaires",      f"{(fdf['ratio_SP']>1).mean()*100:.1f}%"],
                ["Bonus/Malus moyen",           f"{fdf['bonus_malus'].mean():.3f}"],
            ]
            kpi_t = Table(kpi_data, colWidths=[3.5*inch, 2.5*inch])
            kpi_t.setStyle(TableStyle([
                ('BACKGROUND',    (0,0),(-1,0), colors.HexColor('#1565C0')),
                ('TEXTCOLOR',     (0,0),(-1,0), colors.white),
                ('FONTNAME',      (0,0),(-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',      (0,0),(-1,-1), 10),
                ('ALIGN',         (0,0),(-1,-1), 'LEFT'),
                ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, colors.HexColor('#EBF8FF')]),
                ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('BOTTOMPADDING', (0,0),(-1,-1), 6),
                ('TOPPADDING',    (0,0),(-1,-1), 6),
            ]))
            elements.append(kpi_t)
            elements.append(Spacer(1, 0.2*inch))

            # Agrégat région
            elements.append(Paragraph("Analyse par Région", section_s))
            reg = fdf.groupby('region').agg(
                assures=('id_assure', 'count'),
                sinistres=('nb_sinistres', 'sum'),
                montant=('montant_sinistres', 'sum'),
                prime_moy=('montant_prime', 'mean')
            ).round(0).reset_index()
            reg_data = [['Région', 'Assurés', 'Sinistres', 'Montant (€)', 'Prime moy. (€)']]
            for _, row in reg.iterrows():
                reg_data.append([row['region'], f"{int(row['assures']):,}",
                                  f"{int(row['sinistres']):,}", f"{int(row['montant']):,}",
                                  f"{int(row['prime_moy']):,}"])
            reg_t = Table(reg_data)
            reg_t.setStyle(TableStyle([
                ('BACKGROUND',    (0,0),(-1,0), colors.HexColor('#1565C0')),
                ('TEXTCOLOR',     (0,0),(-1,0), colors.white),
                ('FONTNAME',      (0,0),(-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',      (0,0),(-1,-1), 9),
                ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
                ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, colors.HexColor('#EBF8FF')]),
                ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ]))
            elements.append(reg_t)
            elements.append(Spacer(1, 0.2*inch))

            # Insights
            elements.append(Paragraph("Insights & Recommandations", section_s))
            insights_txt = [
                f"• {(fdf['nb_sinistres']==0).mean()*100:.1f}% des assurés n'ont déclaré aucun sinistre.",
                f"• Ratio S/P médian : {fdf['ratio_SP'].median():.1f}x — {(fdf['ratio_SP']>1).mean()*100:.1f}% des assurés sont déficitaires.",
                f"• B/M moyen : {fdf['bonus_malus'].mean():.3f} — {(fdf['bonus_malus']>1).mean()*100:.1f}% des assurés en malus.",
                f"• Le coût moyen ({fdf['montant_sinistres'].mean():,.0f} €) dépasse la prime moyenne de {fdf['montant_sinistres'].mean()/fdf['montant_prime'].mean():.1f}x.",
            ]
            for txt in insights_txt:
                elements.append(Paragraph(txt, body_s))

            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                f"© 2025 AssurAnalytics — Mastère 2 Big Data & Data Stratégie — Sona KOULIBALY",
                ParagraphStyle('foot', parent=styles['Normal'], fontSize=8,
                                textColor=colors.HexColor('#718096'), alignment=TA_CENTER)
            ))

            doc.build(elements)
            buf.seek(0)
            fname = f"rapport_assuranalytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return dcc.send_bytes(buf.getvalue(), fname)

        except ImportError:
            return dict(content="⚠️ reportlab non installé. Installez-le avec : pip install reportlab",
                        filename="erreur.txt")
        except Exception as e:
            return dict(content=f"Erreur PDF : {str(e)}", filename="erreur.txt")
