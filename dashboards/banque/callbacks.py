"""
callbacks.py — Logique interactive du Dashboard Bancaire Sénégal
================================================================
Tous les callbacks Dash : filtres, graphiques, téléchargements, profil banque.
"""

import io
import json
import base64
import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Input, Output, State, callback, dcc, html, no_update
import dash_bootstrap_components as dbc

# ─── Palette centralisée ──────────────────────────────────────────────────────
NAVY   = "#0A1628"
NAVY2  = "#0F2040"
GOLD   = "#D4A843"
GOLD2  = "#F0C060"
CREAM  = "#F8F4EE"
SUCCESS= "#2ECC71"
DANGER = "#E74C3C"
MUTED  = "#8899AA"

PALETTE_BANQUES = [
    "#D4A843","#5BC8F5","#2ECC71","#E74C3C","#B87BFF",
    "#FF6B6B","#4ECDC4","#FFE66D","#A8E6CF","#FF8B94",
    "#6C5CE7","#00B894","#FDCB6E","#E17055","#74B9FF",
    "#FD79A8","#55EFC4","#636E72","#DFE6E9","#2D3436",
    "#00CEC9","#6D214F","#182C61","#F8EFBA"
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(11,22,40,0.6)",
    font=dict(family="DM Sans", color=CREAM, size=12),
    title_font=dict(family="Syne", color=CREAM, size=15),
    legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor=GOLD, borderwidth=1,
                font=dict(color=CREAM, size=11)),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zeroline=False, color=CREAM),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zeroline=False, color=CREAM),
)

COL_LABELS = {
    "bilan"        : "Bilan (M FCFA)",
    "emploi"       : "Emplois (M FCFA)",
    "ressources"   : "Ressources (M FCFA)",
    "fonds_propres": "Fonds Propres (M FCFA)",
    "pnb"          : "Produit Net Bancaire (M FCFA)",
    "resultat_net" : "Résultat Net (M FCFA)",
    "roa"          : "ROA (%)",
    "roe"          : "ROE (%)",
    "cir"          : "Coefficient d'Exploitation (%)",
    "solvabilite"  : "Solvabilité (%)",
}


def safe_fmt(val, suffix=" M", decimals=0):
    """Formate une valeur numérique proprement."""
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return "N/D"
        if abs(val) >= 1_000_000:
            return f"{val/1_000_000:.{decimals}f} Mds"
        if abs(val) >= 1_000:
            return f"{val/1_000:.{decimals}f} K"
        return f"{val:.{decimals}f}{suffix}"
    except Exception:
        return "N/D"


def apply_plotly_defaults(fig, title=""):
    """Applique le thème sombre à toutes les figures."""
    fig.update_layout(**PLOTLY_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, x=0.02, xanchor="left"))
    return fig


# ─── REGISTRATION ─────────────────────────────────────────────────────────────
def register_callbacks(app, df_global):

    # ══════════════════════════════════════════════════════════════
    # CB-00 : Reset tous les filtres
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("filter-annee",      "value"),
        Output("filter-banque",     "value"),
        Output("filter-groupe",     "value"),
        Output("filter-indicateur", "value"),
        Input("btn-reset-filters",  "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n):
        annees = sorted(df_global["annee"].dropna().unique().astype(int).tolist())
        return [min(annees), max(annees)], None, None, "bilan"

    # ══════════════════════════════════════════════════════════════
    # CB-00b : KPIs dynamiques liés au slider + filtres
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("kpi-bilan",       "children"),
        Output("kpi-bilan-sub",   "children"),
        Output("kpi-banques",     "children"),
        Output("kpi-effectif",    "children"),
        Output("kpi-effectif-sub","children"),
        Output("kpi-fonds",       "children"),
        Input("filter-annee",     "value"),
        Input("filter-banque",    "value"),
        Input("filter-groupe",    "value"),
    )
    def update_kpis(annee_range, banques_sel, groupes_sel):
        dff = df_global.copy()

        # Appliquer les filtres
        if annee_range:
            dff = dff[(dff["annee"] >= annee_range[0]) & (dff["annee"] <= annee_range[1])]
        if banques_sel:
            dff = dff[dff["sigle"].isin(banques_sel)]
        if groupes_sel:
            dff = dff[dff["groupe_bancaire"].isin(groupes_sel)]

        # Prendre la dernière année de la sélection
        if dff.empty:
            return "N/D", "", "0", "N/D", "", "N/D"

        last_y   = int(dff["annee"].max())
        df_last  = dff[dff["annee"] == last_y]

        total_bilan = pd.to_numeric(df_last["bilan"], errors="coerce").sum()
        nb_banques  = df_last["sigle"].nunique()
        effectif    = pd.to_numeric(df_last["effectif"], errors="coerce").sum()
        fonds_prop  = pd.to_numeric(df_last["fonds_propres"], errors="coerce").mean()

        # Formater
        bilan_fmt = f"{total_bilan/1_000_000:.2f} Mds FCFA" if total_bilan > 0 else "N/D"
        bilan_sub = f"Secteur {last_y}"
        banques_fmt = str(nb_banques)
        effectif_fmt = f"{int(effectif):,}".replace(",","·") if effectif > 0 else "N/D"
        effectif_sub = f"Employés en {last_y}"
        fonds_fmt = f"{fonds_prop/1000:.1f} Mds" if (fonds_prop and not math.isnan(fonds_prop) and fonds_prop > 0) else "N/D"

        return bilan_fmt, bilan_sub, banques_fmt, effectif_fmt, effectif_sub, fonds_fmt

    # ══════════════════════════════════════════════════════════════
    # CB-01 : Filtrage → Store partagé
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("store-filtered", "data"),
        Input("filter-annee",      "value"),
        Input("filter-banque",     "value"),
        Input("filter-groupe",     "value"),
    )
    def update_store(annee_range, banques_sel, groupes_sel):
        dff = df_global.copy()

        if annee_range:
            dff = dff[(dff["annee"] >= annee_range[0]) & (dff["annee"] <= annee_range[1])]
        if banques_sel:
            dff = dff[dff["sigle"].isin(banques_sel)]
        if groupes_sel:
            dff = dff[dff["groupe_bancaire"].isin(groupes_sel)]

        return dff.to_json(date_format="iso", orient="split")

    # ══════════════════════════════════════════════════════════════
    # CB-02 : Rendu des onglets
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("tabs-content", "children"),
        Input("main-tabs",      "value"),
        Input("store-filtered", "data"),
        Input("filter-indicateur", "value"),
    )
    def render_tab(tab, store_data, indicateur):
        if not store_data:
            return html.Div("Chargement...", style={"color": CREAM})

        dff = pd.read_json(io.StringIO(store_data), orient="split")
        ind = indicateur or "bilan"
        ind_label = COL_LABELS.get(ind, ind)

        # ── TAB 1 : VUE MARCHÉ ────────────────────────────────────
        if tab == "tab-marche":
            # Graphe 1 : Évolution du secteur (bilan total par année)
            df_yr = df_global.groupby("annee")[["bilan","ressources","emploi","fonds_propres"]].sum().reset_index()

            fig_evol = go.Figure()
            for col, name, color in [
                ("bilan","Total Actif", GOLD),
                ("ressources","Ressources", "#5BC8F5"),
                ("emploi","Emplois", SUCCESS),
                ("fonds_propres","Fonds Propres", "#B87BFF"),
            ]:
                fig_evol.add_trace(go.Scatter(
                    x=df_yr["annee"], y=df_yr[col]/1000,
                    name=name, line=dict(color=color, width=2.5),
                    mode="lines+markers",
                    hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{y:,.0f}} Mds FCFA<extra></extra>",
                ))
            apply_plotly_defaults(fig_evol, "📈 Évolution du Secteur Bancaire Sénégalais (Mds FCFA)")

            # Graphe 2 : Répartition groupes (camembert)
            df_grp = dff.groupby("groupe_bancaire")[ind].sum().reset_index()
            df_grp = df_grp[df_grp[ind] > 0]
            fig_pie = go.Figure(go.Pie(
                labels=df_grp["groupe_bancaire"],
                values=df_grp[ind],
                hole=0.55,
                marker=dict(colors=PALETTE_BANQUES[:len(df_grp)],
                            line=dict(color=NAVY2, width=2)),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>%{value:,.0f} M FCFA<br>%{percent}<extra></extra>",
            ))
            fig_pie.update_layout(
                title=dict(text=f"Répartition par Groupe · {ind_label}", font=dict(family="Syne", color=CREAM, size=14)),
                annotations=[dict(text="Groupes", x=0.5, y=0.5, font_size=13, showarrow=False, font_color=CREAM)],
                **{k:v for k,v in PLOTLY_LAYOUT.items() if k != "xaxis" and k != "yaxis"},
            )

            # Graphe 3 : Part de marché bilan 2020 (bar horizontal)
            last_y = dff["annee"].max()
            df_pm = dff[dff["annee"] == last_y][["sigle","bilan"]].dropna().sort_values("bilan", ascending=True)
            df_pm["part"] = df_pm["bilan"] / df_pm["bilan"].sum() * 100

            fig_pm = go.Figure(go.Bar(
                x=df_pm["part"], y=df_pm["sigle"],
                orientation="h",
                marker=dict(
                    color=df_pm["part"],
                    colorscale=[[0, NAVY2],[0.5, GOLD],[1, GOLD2]],
                    showscale=False,
                ),
                text=df_pm["part"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
                textfont=dict(color=CREAM, size=10),
                hovertemplate="<b>%{y}</b><br>Part de marché: %{x:.2f}%<extra></extra>",
            ))
            apply_plotly_defaults(fig_pm, f"🏆 Parts de Marché — {ind_label} ({last_y})")
            fig_pm.update_layout(height=600, yaxis=dict(tickfont=dict(size=11)))

            return html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig_evol, config={"displayModeBar":False}), md=8),
                    dbc.Col(dcc.Graph(figure=fig_pie,  config={"displayModeBar":False}), md=4),
                ], className="g-3 mb-3"),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig_pm, config={"displayModeBar":False}), md=12),
                ]),
            ])

        # ── TAB 2 : COMPARAISON ───────────────────────────────────
        elif tab == "tab-comparaison":
            # Scatter : bilan vs résultat net, bulle = fonds propres
            last_y = dff["annee"].max()
            df_sc = dff[dff["annee"] == last_y][["sigle","bilan","resultat_net","fonds_propres","groupe_bancaire"]].dropna(subset=["bilan"])
            df_sc["resultat_net"] = pd.to_numeric(df_sc["resultat_net"], errors="coerce").fillna(0)
            df_sc["fonds_propres"] = pd.to_numeric(df_sc["fonds_propres"], errors="coerce").abs().fillna(1)

            fig_scatter = px.scatter(
                df_sc, x="bilan", y="resultat_net",
                size="fonds_propres", color="groupe_bancaire",
                text="sigle", size_max=60,
                color_discrete_sequence=PALETTE_BANQUES,
                labels={"bilan":"Bilan (M FCFA)","resultat_net":"Résultat Net (M FCFA)",
                        "groupe_bancaire":"Groupe"},
                hover_data={"sigle":True,"fonds_propres":":.0f"},
            )
            fig_scatter.update_traces(textposition="top center", textfont=dict(color=CREAM, size=9))
            apply_plotly_defaults(fig_scatter, f"🔵 Bilan vs Résultat Net — taille = Fonds Propres ({last_y})")

            # Barres groupées : indicateur par banque et année
            df_bar = dff.groupby(["annee","sigle"])[ind].sum().reset_index()
            fig_bar = px.bar(
                df_bar, x="sigle", y=ind, color="annee",
                barmode="group",
                color_discrete_sequence=px.colors.sequential.YlOrBr,
                labels={"sigle":"Banque", ind: ind_label, "annee":"Année"},
                hover_data={"sigle":True, ind:":.0f"},
            )
            apply_plotly_defaults(fig_bar, f"📊 Comparaison {ind_label} par Banque et Année")
            fig_bar.update_layout(xaxis_tickangle=-45)

            return html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig_scatter, config={"displayModeBar":False}), md=6),
                    dbc.Col(dcc.Graph(figure=fig_bar,     config={"displayModeBar":False}), md=6),
                ], className="g-3"),
            ])

        # ── TAB 3 : PERFORMANCE ───────────────────────────────────
        elif tab == "tab-performance":
            # Heatmap performances banques x années
            df_heat = dff.pivot_table(index="sigle", columns="annee", values=ind, aggfunc="sum")

            fig_heat = go.Figure(go.Heatmap(
                z=df_heat.values,
                x=[str(c) for c in df_heat.columns],
                y=df_heat.index.tolist(),
                colorscale=[[0,"#0A1628"],[0.5,GOLD],[1,GOLD2]],
                hovertemplate="<b>%{y}</b><br>%{x}: %{z:,.0f}<extra></extra>",
                showscale=True,
                colorbar=dict(tickfont=dict(color=CREAM)),
            ))
            apply_plotly_defaults(fig_heat, f"🌡 Heatmap {ind_label} — Banques × Années")
            fig_heat.update_layout(height=580)

            # Waterfall : top 10 croissance bilan
            annees_disp = sorted(dff["annee"].unique())
            if len(annees_disp) >= 2:
                y1, y2 = annees_disp[0], annees_disp[-1]
                df_wf = dff[dff["annee"].isin([y1,y2])].groupby(["sigle","annee"])[ind].sum().unstack()
                df_wf.columns = ["debut","fin"]
                df_wf["croissance"] = df_wf["fin"] - df_wf["debut"]
                df_wf = df_wf.sort_values("croissance", ascending=False).head(12)

                fig_wf = go.Figure(go.Bar(
                    x=df_wf.index.tolist(),
                    y=df_wf["croissance"],
                    marker_color=[SUCCESS if v >= 0 else DANGER for v in df_wf["croissance"]],
                    hovertemplate="<b>%{x}</b><br>Croissance: %{y:+,.0f}<extra></extra>",
                    text=df_wf["croissance"].apply(lambda x: f"{x:+,.0f}"),
                    textposition="outside", textfont=dict(color=CREAM, size=9),
                ))
                apply_plotly_defaults(fig_wf, f"📈 Croissance {ind_label} ({y1}→{y2})")
            else:
                fig_wf = go.Figure()
                apply_plotly_defaults(fig_wf, "Données insuffisantes")

            return html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig_heat, config={"displayModeBar":False}), md=12),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig_wf,  config={"displayModeBar":False}), md=12),
                ]),
            ])

        # ── TAB 4 : RATIOS FINANCIERS ─────────────────────────────
        elif tab == "tab-ratios":
            last_y = dff["annee"].max()
            df_r = dff[dff["annee"] == last_y].copy()

            # Calculer ratios si absents
            if "roa" not in df_r.columns or df_r["roa"].isna().all():
                df_r["roa"] = pd.to_numeric(df_r["resultat_net"],errors="coerce") / pd.to_numeric(df_r["bilan"],errors="coerce") * 100
            if "roe" not in df_r.columns or df_r["roe"].isna().all():
                df_r["roe"] = pd.to_numeric(df_r["resultat_net"],errors="coerce") / pd.to_numeric(df_r["fonds_propres"],errors="coerce") * 100
            if "cir" not in df_r.columns or df_r["cir"].isna().all():
                df_r["cir"] = pd.to_numeric(df_r["charges_generales"],errors="coerce") / pd.to_numeric(df_r["pnb"],errors="coerce") * 100
            if "solvabilite" not in df_r.columns or df_r["solvabilite"].isna().all():
                df_r["solvabilite"] = pd.to_numeric(df_r["fonds_propres"],errors="coerce") / pd.to_numeric(df_r["bilan"],errors="coerce") * 100

            # Scatter ROA vs ROE
            df_rr = df_r[["sigle","roa","roe","groupe_bancaire","bilan"]].dropna(subset=["bilan"])
            df_rr["roa"] = pd.to_numeric(df_rr["roa"], errors="coerce")
            df_rr["roe"] = pd.to_numeric(df_rr["roe"], errors="coerce")
            df_rr = df_rr.dropna(subset=["roa","roe"])

            fig_roa_roe = px.scatter(
                df_rr, x="roa", y="roe", text="sigle",
                color="groupe_bancaire", size="bilan", size_max=40,
                color_discrete_sequence=PALETTE_BANQUES,
                labels={"roa":"ROA (%)","roe":"ROE (%)","groupe_bancaire":"Groupe"},
            )
            fig_roa_roe.update_traces(textposition="top center", textfont=dict(color=CREAM, size=9))
            apply_plotly_defaults(fig_roa_roe, f"💡 ROA vs ROE ({last_y}) — taille = Bilan")

            # Bar chart : CIR (coefficient exploitation)
            df_cir = df_r[["sigle","cir"]].dropna().sort_values("cir")
            df_cir["cir"] = pd.to_numeric(df_cir["cir"], errors="coerce").dropna()
            df_cir = df_cir.dropna()

            fig_cir = go.Figure(go.Bar(
                x=df_cir["sigle"], y=df_cir["cir"],
                marker_color=[SUCCESS if v < 60 else (GOLD if v < 80 else DANGER) for v in df_cir["cir"]],
                hovertemplate="<b>%{x}</b><br>CIR: %{y:.1f}%<extra></extra>",
                text=df_cir["cir"].apply(lambda x: f"{x:.0f}%"),
                textposition="outside", textfont=dict(color=CREAM, size=9),
            ))
            fig_cir.add_hline(y=60, line_dash="dash", line_color=SUCCESS,
                              annotation_text="Seuil optimal 60%", annotation_font_color=SUCCESS)
            fig_cir.add_hline(y=80, line_dash="dash", line_color=DANGER,
                              annotation_text="Seuil critique 80%", annotation_font_color=DANGER)
            apply_plotly_defaults(fig_cir, f"⚙️ Coefficient d'Exploitation (CIR) — {last_y}")

            return html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig_roa_roe, config={"displayModeBar":False}), md=6),
                    dbc.Col(dcc.Graph(figure=fig_cir,     config={"displayModeBar":False}), md=6),
                ], className="g-3"),
            ])

        # ── TAB 5 : CARTE SÉNÉGAL ─────────────────────────────────
        elif tab == "tab-carte":
            # Coordonnées des sièges sociaux des banques à Dakar
            coords = {
                "CBAO"      : (14.6937, -17.4441, "Rue du Docteur Thèze, Dakar"),
                "SGBS"      : (14.6942, -17.4382, "19 Av. Léopold Sédar Senghor"),
                "ECOBANK"   : (14.7167, -17.4677, "Km 5 Bd du Centenaire"),
                "BOA"       : (14.6928, -17.4431, "Place de l'Indépendance"),
                "ORABANK"   : (14.6894, -17.4462, "Avenue Peytavin"),
                "BICIS"     : (14.6939, -17.4385, "2 Av. du Président Lamine Guèye"),
                "BHS"       : (14.7133, -17.4676, "Sacré-Cœur III"),
                "BIS"       : (14.7291, -17.4627, "Route de la Corniche Ouest"),
                "BAS"       : (14.6921, -17.4418, "Avenue William Ponty"),
                "NSIA Banque":(14.6931,-17.4447, "Immeuble Fahd"),
                "LBA"       : (14.7022, -17.4489, "Route de Rufisque"),
                "CBI"       : (14.6910, -17.4430, "Place de l'Indépendance"),
                "BRM"       : (14.7054, -17.4506, "Liberté VI"),
                "BNDE"      : (14.6944, -17.4419, "6 Av. Carde"),
                "UBA"       : (14.6916, -17.4452, "Av. Léopold Sédar Senghor"),
                "FBNBANK"   : (14.6925, -17.4437, "Immeuble SDIH"),
                "CISA"      : (14.6978, -17.4510, "Liberté II"),
                "BDK"       : (14.7201, -17.4621, "Mermoz"),
                "BGFI"      : (14.6953, -17.4445, "Avenue Roume"),
                "BSIC"      : (14.6888, -17.4422, "Médina"),
                "CITIBANK"  : (14.6946, -17.4378, "Plateau"),
                "LBO"       : (14.7012, -17.4498, "Ouakam"),
                "BCIM"      : (14.6907, -17.4461, "Av. Georges Pompidou"),
                "CDS"       : (14.6933, -17.4439, "Allées Robert Delmas"),
            }

            last_y = dff["annee"].max()
            df_map = dff[dff["annee"] == last_y][["sigle","bilan","groupe_bancaire"]].copy()
            df_map["bilan"] = pd.to_numeric(df_map["bilan"], errors="coerce").fillna(0)

            map_data = []
            for _, row in df_map.iterrows():
                sig = row["sigle"]
                if sig in coords:
                    lat, lon, adresse = coords[sig]
                    map_data.append({
                        "sigle": sig, "lat": lat, "lon": lon,
                        "bilan": row["bilan"],
                        "groupe": row["groupe_bancaire"],
                        "adresse": adresse,
                    })

            df_map2 = pd.DataFrame(map_data)
            if not df_map2.empty:
                df_map2["taille"] = (df_map2["bilan"] / df_map2["bilan"].max() * 40 + 5).clip(5, 50)

                fig_carte = px.scatter_mapbox(
                    df_map2,
                    lat="lat", lon="lon",
                    size="taille", size_max=50,
                    color="groupe",
                    hover_name="sigle",
                    hover_data={"bilan":":.0f", "adresse":True, "lat":False, "lon":False, "taille":False},
                    color_discrete_sequence=PALETTE_BANQUES,
                    zoom=11.5, center=dict(lat=14.6937, lon=-17.4441),
                    mapbox_style="carto-darkmatter",
                )
                fig_carte.update_layout(
                    height=580,
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0,r=0,t=40,b=0),
                    title=dict(text=f"🗺 Localisation des Banques à Dakar — Bilan {last_y}",
                               font=dict(family="Syne",color=CREAM,size=14)),
                    legend=dict(bgcolor="rgba(10,22,40,0.8)", bordercolor=GOLD, borderwidth=1,
                                font=dict(color=CREAM)),
                )
            else:
                fig_carte = go.Figure()
                apply_plotly_defaults(fig_carte, "Données cartographiques indisponibles")

            return html.Div([
                dcc.Graph(figure=fig_carte, config={"displayModeBar":False}),
            ])

        # ── TAB 6 : CLASSEMENT ────────────────────────────────────
        elif tab == "tab-classement":
            last_y = dff["annee"].max()
            df_rank = dff[dff["annee"] == last_y].copy()

            # Calcul des ratios
            for col in ["bilan","resultat_net","fonds_propres","pnb","ressources","emploi"]:
                df_rank[col] = pd.to_numeric(df_rank.get(col, pd.Series()), errors="coerce")

            df_rank["roa_calc"] = df_rank["resultat_net"] / df_rank["bilan"] * 100
            df_rank["roe_calc"] = df_rank["resultat_net"] / df_rank["fonds_propres"] * 100
            df_rank["part_marche"] = df_rank["bilan"] / df_rank["bilan"].sum() * 100

            df_rank = df_rank.sort_values("bilan", ascending=False).reset_index(drop=True)
            df_rank.index += 1

            cols_show = {
                "sigle"        : "Banque",
                "groupe_bancaire": "Groupe",
                "bilan"        : "Bilan (M)",
                "resultat_net" : "Résultat Net (M)",
                "fonds_propres": "Fonds Propres (M)",
                "part_marche"  : "Part Marché (%)",
                "roa_calc"     : "ROA (%)",
                "roe_calc"     : "ROE (%)",
            }

            def fmt_col(series, col):
                if col in ["part_marche","roa_calc","roe_calc"]:
                    return series.apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/D")
                elif col in ["bilan","resultat_net","fonds_propres"]:
                    return series.apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/D")
                return series

            table_rows = []
            for rank, (_, row) in enumerate(df_rank[list(cols_show.keys())].iterrows(), 1):
                medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
                cells = [html.Td(medal, className="rank-medal")]
                for col, label in cols_show.items():
                    val = row.get(col, "N/D")
                    if col in ["part_marche","roa_calc","roe_calc"]:
                        display = f"{val:.2f}%" if pd.notna(val) else "N/D"
                    elif col in ["bilan","resultat_net","fonds_propres"]:
                        display = f"{val:,.0f}" if pd.notna(val) else "N/D"
                        if col == "resultat_net" and pd.notna(val):
                            color = SUCCESS if val >= 0 else DANGER
                            cells.append(html.Td(display, style={"color": color}))
                            continue
                    else:
                        display = str(val)
                    cells.append(html.Td(display))
                table_rows.append(html.Tr(cells))

            table = html.Table([
                html.Thead(html.Tr(
                    [html.Th("#")] + [html.Th(v) for v in cols_show.values()]
                )),
                html.Tbody(table_rows),
            ], className="classement-table")

            return html.Div([
                html.Div([
                    html.H3(f"🏆 Classement des Banques — {last_y}", className="classement-title"),
                    html.P(f"Trié par Bilan (Total Actif) — {df_rank['sigle'].nunique()} banques",
                           style={"color": MUTED, "fontSize": "13px"}),
                ], className="mb-3"),
                html.Div(table, className="table-wrapper"),
            ])

        return html.Div("Onglet non trouvé", style={"color": CREAM})

    # ══════════════════════════════════════════════════════════════
    # CB-03 : KPIs banque individuelle
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("profil-banque-kpi", "children"),
        Input("select-banque-profil", "value"),
        Input("select-annee-profil",  "value"),
    )
    def update_profil_kpi(sigle, annee):
        if not sigle or not annee:
            return ""
        df_b = df_global[(df_global["sigle"] == sigle) & (df_global["annee"] == annee)]
        if df_b.empty:
            return html.P(f"Aucune donnée pour {sigle} en {annee}", style={"color": MUTED})

        row = df_b.iloc[0]
        bilan       = pd.to_numeric(row.get("bilan"), errors="coerce")
        rn          = pd.to_numeric(row.get("resultat_net"), errors="coerce")
        fp          = pd.to_numeric(row.get("fonds_propres"), errors="coerce")
        ressources  = pd.to_numeric(row.get("ressources"), errors="coerce")
        effectif    = pd.to_numeric(row.get("effectif"), errors="coerce")
        agences     = pd.to_numeric(row.get("agences"), errors="coerce")

        roa = (rn / bilan * 100) if (pd.notna(bilan) and bilan != 0 and pd.notna(rn)) else None
        roe = (rn / fp * 100)    if (pd.notna(fp) and fp != 0 and pd.notna(rn)) else None

        def fmt(v, pct=False, k=False):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return "N/D"
            if pct:
                return f"{v:.2f}%"
            if k:
                return f"{int(v):,}".replace(",","·")
            return f"{v/1000:.1f} Mds"

        return dbc.Row([
            dbc.Col(html.Div([
                html.P("Total Actif (Bilan)", className="kpi-label"),
                html.H4(fmt(bilan), className="kpi-value", style={"color":GOLD}),
            ], className="kpi-card mini"), xs=6, md=2),
            dbc.Col(html.Div([
                html.P("Résultat Net", className="kpi-label"),
                html.H4(fmt(rn), className="kpi-value",
                        style={"color": SUCCESS if (pd.notna(rn) and rn >= 0) else DANGER}),
            ], className="kpi-card mini"), xs=6, md=2),
            dbc.Col(html.Div([
                html.P("Fonds Propres", className="kpi-label"),
                html.H4(fmt(fp), className="kpi-value", style={"color":"#B87BFF"}),
            ], className="kpi-card mini"), xs=6, md=2),
            dbc.Col(html.Div([
                html.P("ROA", className="kpi-label"),
                html.H4(fmt(roa, pct=True), className="kpi-value", style={"color":"#5BC8F5"}),
            ], className="kpi-card mini"), xs=6, md=2),
            dbc.Col(html.Div([
                html.P("ROE", className="kpi-label"),
                html.H4(fmt(roe, pct=True), className="kpi-value", style={"color":GOLD2}),
            ], className="kpi-card mini"), xs=6, md=2),
            dbc.Col(html.Div([
                html.P("Effectif / Agences", className="kpi-label"),
                html.H4(f"{fmt(effectif, k=True)} / {fmt(agences, k=True)}", className="kpi-value",
                        style={"color": SUCCESS}),
            ], className="kpi-card mini"), xs=6, md=2),
        ], className="g-2 mb-3")

    # ══════════════════════════════════════════════════════════════
    # CB-04 : Graphique évolution banque individuelle
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("graph-profil-evolution", "figure"),
        Input("select-banque-profil", "value"),
    )
    def graph_profil_evolution(sigle):
        if not sigle:
            return go.Figure()
        df_b = df_global[df_global["sigle"] == sigle].sort_values("annee")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for col, name, color, sec in [
            ("bilan",       "Bilan",        GOLD,    False),
            ("ressources",  "Ressources",   "#5BC8F5", False),
            ("emploi",      "Emplois",      SUCCESS, False),
            ("fonds_propres","Fonds Propres","#B87BFF",False),
            ("resultat_net","Résultat Net", DANGER,  True),
        ]:
            if col in df_b.columns:
                vals = pd.to_numeric(df_b[col], errors="coerce")
                fig.add_trace(go.Scatter(
                    x=df_b["annee"], y=vals/1000,
                    name=name, line=dict(color=color, width=2),
                    mode="lines+markers",
                    hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{y:,.1f}} Mds<extra></extra>",
                ), secondary_y=sec)

        apply_plotly_defaults(fig, f"📈 Évolution {sigle} — Indicateurs Clés (Mds FCFA)")
        return fig

    # ══════════════════════════════════════════════════════════════
    # CB-05 : Radar chart banque individuelle
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("graph-profil-radar", "figure"),
        Input("select-banque-profil", "value"),
        Input("select-annee-profil",  "value"),
    )
    def graph_profil_radar(sigle, annee):
        if not sigle or not annee:
            return go.Figure()

        df_b   = df_global[(df_global["sigle"] == sigle) & (df_global["annee"] == annee)]
        df_all = df_global[df_global["annee"] == annee]
        if df_b.empty:
            return go.Figure()

        dims = ["bilan","ressources","emploi","fonds_propres","effectif"]
        dims = [d for d in dims if d in df_global.columns]

        def normalize(val, col):
            mx = pd.to_numeric(df_all[col], errors="coerce").max()
            if mx and mx != 0:
                return float(pd.to_numeric(val, errors="coerce") or 0) / mx * 100
            return 0

        row    = df_b.iloc[0]
        values = [normalize(row.get(d), d) for d in dims]
        labels = [COL_LABELS.get(d, d).replace(" (M FCFA)","") for d in dims]

        fig = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            fillcolor=f"rgba(212,168,67,0.2)",
            line=dict(color=GOLD, width=2),
            name=sigle,
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(15,32,64,0.6)",
                radialaxis=dict(visible=True, range=[0,100], gridcolor="rgba(255,255,255,0.1)",
                                tickfont=dict(color=MUTED, size=8)),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color=CREAM, size=10)),
            ),
            showlegend=False,
            title=dict(text=f"Profil {sigle} ({annee})", font=dict(family="Syne",color=CREAM,size=13)),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40,r=40,t=50,b=40),
        )
        return fig

    # ══════════════════════════════════════════════════════════════
    # CB-06 : Téléchargement Excel
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("download-excel", "data"),
        Input("btn-download-excel", "n_clicks"),
        State("store-filtered", "data"),
        prevent_initial_call=True,
    )
    def download_excel(n, store_data):
        if not n or not store_data:
            return no_update
        dff = pd.read_json(io.StringIO(store_data), orient="split")

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            dff.to_excel(writer, sheet_name="Données Brutes", index=False)

            # Onglet résumé
            summary = dff.groupby("sigle").agg(
                bilan_moy=("bilan","mean"),
                resultat_net_moy=("resultat_net","mean"),
                fonds_propres_moy=("fonds_propres","mean"),
            ).round(0)
            summary.to_excel(writer, sheet_name="Résumé par Banque")

        buf.seek(0)
        return dcc.send_bytes(buf.read(), "banques_senegal_export.xlsx")

    # ══════════════════════════════════════════════════════════════
    # CB-07 : Téléchargement HTML
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("download-html", "data"),
        Input("btn-download-html", "n_clicks"),
        State("store-filtered", "data"),
        prevent_initial_call=True,
    )
    def download_html(n, store_data):
        if not n or not store_data:
            return no_update
        dff = pd.read_json(io.StringIO(store_data), orient="split")

        last_y = int(dff["annee"].max()) if not dff.empty else "N/D"
        total_bilan = dff[dff["annee"]==last_y]["bilan"].sum() / 1_000_000 if not dff.empty else 0

        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Rapport Banques Sénégal {last_y}</title>
<style>
  body{{font-family:'Segoe UI',sans-serif;background:#0A1628;color:#F8F4EE;margin:0;padding:20px}}
  h1{{color:#D4A843;font-size:2em;border-bottom:2px solid #D4A843;padding-bottom:10px}}
  h2{{color:#5BC8F5;margin-top:30px}}
  table{{width:100%;border-collapse:collapse;margin:15px 0}}
  th{{background:#1E3050;color:#D4A843;padding:10px;text-align:left}}
  td{{padding:8px;border-bottom:1px solid #1E3050;color:#F8F4EE}}
  tr:hover{{background:#111E35}}
  .badge{{background:#1E3050;border-radius:4px;padding:2px 8px;color:#D4A843;font-size:.8em}}
  .kpi-box{{display:inline-block;background:#111E35;border:1px solid #1E3050;
            border-radius:8px;padding:15px 25px;margin:10px;text-align:center}}
  .kpi-val{{font-size:1.8em;font-weight:bold;color:#D4A843}}
  .kpi-lbl{{font-size:.85em;color:#8899AA;margin-top:5px}}
  footer{{margin-top:40px;color:#8899AA;font-size:.8em;border-top:1px solid #1E3050;padding-top:10px}}
</style>
</head>
<body>
<h1>🏦 Rapport — Positionnement des Banques au Sénégal</h1>
<p>Source : BCEAO · Base Sénégal | Exporté depuis le Dashboard</p>

<h2>📊 Indicateurs Globaux {last_y}</h2>
<div>
  <div class="kpi-box"><div class="kpi-val">{total_bilan:.2f} Mds</div><div class="kpi-lbl">Total Actif Bancaire</div></div>
  <div class="kpi-box"><div class="kpi-val">{dff[dff['annee']==last_y]['sigle'].nunique()}</div><div class="kpi-lbl">Banques Actives</div></div>
  <div class="kpi-box"><div class="kpi-val">{int(dff[dff['annee']==last_y]['effectif'].sum()):,}</div><div class="kpi-lbl">Effectif Total</div></div>
</div>

<h2>🏆 Classement par Bilan — {last_y}</h2>
<table>
<thead><tr><th>#</th><th>Banque</th><th>Groupe</th><th>Bilan (M FCFA)</th><th>Ressources</th><th>Emplois</th><th>Fonds Propres</th></tr></thead>
<tbody>
"""
        df_rank = dff[dff["annee"]==last_y].sort_values("bilan",ascending=False).reset_index(drop=True)
        for i, row in df_rank.iterrows():
            html_content += f"<tr><td>{i+1}</td><td><b>{row.get('sigle','')}</b></td><td>{row.get('groupe_bancaire','')}</td>"
            for col in ["bilan","ressources","emploi","fonds_propres"]:
                val = pd.to_numeric(row.get(col), errors="coerce")
                html_content += f"<td>{val:,.0f}</td>" if pd.notna(val) else "<td>N/D</td>"
            html_content += "</tr>\n"

        html_content += """</tbody></table>
<footer>Dashboard Banques Sénégal · Python · Dash · MongoDB Atlas · Source BCEAO</footer>
</body></html>"""

        return dcc.send_string(html_content, "rapport_banques_senegal.html")

    # ══════════════════════════════════════════════════════════════
    # CB-09 : Bouton "Générer & Télécharger le Rapport" individuel
    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("download-rapport-individuel", "data"),
        Input("btn-generer-rapport",          "n_clicks"),
        State("select-banque-profil",         "value"),
        State("select-annee-profil",          "value"),
        prevent_initial_call=True,
    )
    def generer_rapport_individuel(n, sigle, annee):
        if not n or not sigle:
            return no_update
        try:
            from utils.pdf_generator import generate_bank_pdf
            pdf_bytes = generate_bank_pdf(df_global, sigle, annee or int(df_global["annee"].max()))
            return dcc.send_bytes(pdf_bytes, f"rapport_{sigle}_{annee}.pdf")
        except Exception as e:
            log.error(f"Erreur génération PDF : {e}")
            # Fallback HTML
            df_b = df_global[df_global["sigle"] == sigle].sort_values("annee")
            rows = ""
            for _, row in df_b.iterrows():
                rn = pd.to_numeric(row.get("resultat_net"), errors="coerce")
                col_rn = "#2ECC71" if (pd.notna(rn) and rn >= 0) else "#E74C3C"
                rows += f"<tr><td><b>{int(row['annee'])}</b></td>"
                for c in ["bilan","ressources","emploi","fonds_propres"]:
                    v = pd.to_numeric(row.get(c), errors="coerce")
                    rows += f"<td>{v:,.0f}</td>" if pd.notna(v) else "<td>N/D</td>"
                rn_disp = f"{rn:,.0f}" if pd.notna(rn) else "N/D"
                rows += f"<td style='color:{col_rn}'>{rn_disp}</td></tr>\n"
            groupe = df_b.iloc[0].get("groupe_bancaire","N/D") if not df_b.empty else "N/D"
            html_f = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Rapport {sigle}</title>
<style>body{{font-family:sans-serif;background:#0A1628;color:#F8F4EE;padding:30px}}
h1{{color:#D4A843}}table{{width:100%;border-collapse:collapse}}
th{{background:#1E3050;color:#D4A843;padding:10px}}td{{padding:8px;border-bottom:1px solid #1E3050}}
</style></head><body>
<h1>Rapport {sigle} — {annee}</h1>
<p>Groupe : {groupe}</p>
<table><thead><tr><th>Année</th><th>Bilan</th><th>Ressources</th><th>Emplois</th><th>Fonds Propres</th><th>Résultat Net</th></tr></thead>
<tbody>{rows}</tbody></table>
<p style="color:#8899AA;margin-top:20px">Dashboard Banques Sénégal · Source BCEAO</p>
</body></html>"""
            return dcc.send_string(html_f, f"rapport_{sigle}_{annee}.html")


    # ══════════════════════════════════════════════════════════════
    @app.callback(
        Output("download-pdf", "data"),
        Input("btn-download-pdf",    "n_clicks"),
        State("select-banque-profil","value"),
        State("select-annee-profil", "value"),
        prevent_initial_call=True,
    )
    def download_rapport_pdf(n, sigle, annee):
        if not n or not sigle:
            return no_update
        try:
            from utils.pdf_generator import generate_bank_pdf
            pdf_bytes = generate_bank_pdf(df_global, sigle, annee or df_global["annee"].max())
            return dcc.send_bytes(pdf_bytes, f"rapport_{sigle}_{annee}.pdf")
        except Exception as e:
            # Fallback HTML si ReportLab échoue
            df_b = df_global[df_global["sigle"] == sigle].sort_values("annee")
            rows = ""
            for _, row in df_b.iterrows():
                rn = pd.to_numeric(row.get("resultat_net"), errors="coerce")
                col = "#2ECC71" if (pd.notna(rn) and rn >= 0) else "#E74C3C"
                rows += f"<tr><td><b>{int(row['annee'])}</b></td>"
                for c in ["bilan","ressources","emploi","fonds_propres"]:
                    v = pd.to_numeric(row.get(c), errors="coerce")
                    rows += f"<td>{v:,.0f}</td>" if pd.notna(v) else "<td>N/D</td>"
                rows += f"<td style='color:{col}'>{rn:,.0f}</td></tr>\n" if pd.notna(rn) else "<td>N/D</td></tr>\n"
            html_f = f"<html><body style='font-family:sans-serif;background:#0A1628;color:#F8F4EE;padding:20px'><h1 style='color:#D4A843'>Rapport {sigle}</h1><table border='1'><thead><tr><th>Année</th><th>Bilan</th><th>Ressources</th><th>Emplois</th><th>Fonds Propres</th><th>Résultat Net</th></tr></thead><tbody>{rows}</tbody></table></body></html>"
            return dcc.send_string(html_f, f"rapport_{sigle}_{annee}.html")