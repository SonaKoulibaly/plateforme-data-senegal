# =============================================================================
# CALLBACKS.PY — Logique Interactive | Projet Énergie Solaire
# Auteur : SK | Dashboard Parc Photovoltaïque
# CORRECTIONS : fillcolor rgba, reset button, datetime parsing, filtre pays
# =============================================================================

import io
import json
import base64
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Input, Output, State, html, dash_table, dcc
from dash.exceptions import PreventUpdate

# ─── PALETTE & THÈME ─────────────────────────────────────────────────────────

COLORS = {
    "primary":   "#F97316",
    "secondary": "#0F172A",
    "accent":    "#3B82F6",
    "success":   "#10B981",
    "warning":   "#FBBF24",
    "danger":    "#EF4444",
    "purple":    "#8B5CF6",
    "cyan":      "#06B6D4",
    "pink":      "#EC4899",
    "bg":        "#0F172A",
    "card":      "#1E293B",
    "border":    "#334155",
    "text":      "#E2E8F0",
    "muted":     "#94A3B8",
}

COUNTRY_COLORS = {
    "Norway":    "#3B82F6",
    "Brazil":    "#10B981",
    "India":     "#F97316",
    "Australia": "#8B5CF6",
}

# ✅ FIX GLOBAL : Plotly refuse hex+alpha (#RRGGBBAA) — rgba() obligatoire
COUNTRY_FILL = {
    "Norway":    "rgba(59,130,246,0.12)",
    "Brazil":    "rgba(16,185,129,0.12)",
    "India":     "rgba(249,115,22,0.12)",
    "Australia": "rgba(139,92,246,0.12)",
}
COUNTRY_FILL_LIGHT = {
    "Norway":    "rgba(59,130,246,0.07)",
    "Brazil":    "rgba(16,185,129,0.07)",
    "India":     "rgba(249,115,22,0.07)",
    "Australia": "rgba(139,92,246,0.07)",
}

COUNTRY_FLAGS = {
    "Norway":    "🇳🇴 Norvège",
    "Brazil":    "🇧🇷 Brésil",
    "India":     "🇮🇳 Inde",
    "Australia": "🇦🇺 Australie",
}

MONTH_NAMES = {
    1:"Jan", 2:"Fév", 3:"Mar", 4:"Avr", 5:"Mai", 6:"Jun",
    7:"Jul", 8:"Aoû", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Déc"
}


def plotly_layout(title="", height=400):
    """Template Plotly sombre unifié."""
    return dict(
        title=dict(text=title, font=dict(size=14, color=COLORS["text"], family="Poppins"), x=0.01),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins", color=COLORS["text"], size=11),
        legend=dict(
            bgcolor="rgba(30,41,59,0.8)",
            bordercolor=COLORS["border"],
            borderwidth=1,
            font=dict(size=10),
        ),
        margin=dict(l=50, r=20, t=40, b=50),
        xaxis=dict(
            gridcolor=COLORS["border"],
            linecolor=COLORS["border"],
            tickfont=dict(size=10),
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=COLORS["border"],
            linecolor=COLORS["border"],
            tickfont=dict(size=10),
            showgrid=True,
            zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor=COLORS["card"],
            bordercolor=COLORS["primary"],
            font=dict(family="Poppins", size=11, color=COLORS["text"]),
        ),
    )


def filter_df(df, countries, months, hours):
    """Filtre le dataframe selon les contrôles."""
    dff = df.copy()
    if countries:
        dff = dff[dff["Country"].isin(countries)]
    if months:
        dff = dff[dff["Month"].isin(months)]
    if hours and len(hours) == 2:
        dff = dff[(dff["Hour"] >= hours[0]) & (dff["Hour"] <= hours[1])]
    return dff


def fmt_number(val, decimals=1):
    """Formate un nombre pour KPI."""
    if pd.isna(val): return "—"
    if val >= 1_000_000:
        return f"{val/1_000_000:.{decimals}f}M"
    if val >= 1_000:
        return f"{val/1_000:.{decimals}f}K"
    return f"{val:.{decimals}f}"


def read_store(json_data):
    """Désérialise le store JSON en DataFrame + recrée les colonnes dérivées."""
    dff = pd.read_json(io.StringIO(json_data), orient="split")
    # Recrée Efficiency si absente (perdue à la sérialisation)
    if "Efficiency" not in dff.columns:
        dff["Efficiency"] = np.where(
            dff["DC_Power"] > 0,
            (dff["AC_Power"] / dff["DC_Power"] * 100).round(2),
            np.nan
        )
    # Recrée Anomalie si absente
    if "Anomalie" not in dff.columns:
        dff["Anomalie"] = (
            (dff["Hour"] >= 8) & (dff["Hour"] <= 18) & (dff["DC_Power"] == 0)
        )
    return dff


def no_data_fig(height=400):
    """Figure vide avec message 'Aucune donnée'."""
    fig = go.Figure()
    fig.add_annotation(
        text="Aucune donnée pour la sélection",
        xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(color=COLORS["muted"], size=14)
    )
    fig.update_layout(**plotly_layout(height=height))
    return fig


# =============================================================================
# REGISTER CALLBACKS
# =============================================================================

def register_callbacks(app, df):

    # ─── SLIDER LABEL ────────────────────────────────────────────────────────
    @app.callback(
        Output("slider-hour-label", "children"),
        Input("filter-hour", "value"),
    )
    def update_slider_label(hours):
        if not hours: return "0h — 23h"
        return f"{hours[0]}h — {hours[1]}h"


    # ─── ✅ BOUTON RÉINITIALISER ─────────────────────────────────────────────
    @app.callback(
        [Output("filter-country", "value"),
         Output("filter-month",   "value"),
         Output("filter-hour",    "value")],
        Input("btn-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        return (
            ["Norway", "Brazil", "India", "Australia"],
            list(range(1, 13)),
            [0, 23],
        )


    # ─── STORE DONNÉES FILTRÉES ──────────────────────────────────────────────
    @app.callback(
        Output("store-filtered-data", "data"),
        [Input("filter-country", "value"),
         Input("filter-month",   "value"),
         Input("filter-hour",    "value")],
    )
    def update_store(countries, months, hours):
        dff = filter_df(df, countries, months, hours)
        # ✅ FIX : exclure DateTime (timestamp) — évite erreurs de sérialisation JSON
        cols = [c for c in dff.columns if c != "DateTime"]
        return dff[cols].to_json(orient="split", date_format="iso")


    # ─── KPI CARDS ───────────────────────────────────────────────────────────
    @app.callback(
        [Output("kpi-dc-total",    "children"),
         Output("kpi-ac-total",    "children"),
         Output("kpi-efficiency",  "children"),
         Output("kpi-irradiation", "children"),
         Output("kpi-temp-mod",    "children"),
         Output("kpi-anomalies",   "children"),
         Output("kpi-pic-hour",    "children"),
         Output("kpi-best-site",   "children")],
        Input("store-filtered-data", "data"),
    )
    def update_kpis(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty:
            return ["—"] * 8

        dc_total  = dff["DC_Power"].sum()
        ac_total  = dff["AC_Power"].sum()
        eff       = dff.loc[dff["DC_Power"] > 0, "Efficiency"].mean()
        irrad     = dff["Irradiation"].mean()
        temp      = dff["Module_Temperature"].mean()
        anomalies = int(dff["Anomalie"].sum())

        hour_mean = dff.groupby("Hour")["DC_Power"].mean()
        pic_hour  = int(hour_mean.idxmax()) if not hour_mean.empty else 0

        country_sum = dff.groupby("Country")["DC_Power"].sum()
        best_raw  = country_sum.idxmax() if not country_sum.empty else "—"
        best_site = COUNTRY_FLAGS.get(best_raw, best_raw)

        return [
            fmt_number(dc_total),
            fmt_number(ac_total),
            f"{eff:.1f}" if not pd.isna(eff) else "—",
            f"{irrad:.3f}",
            f"{temp:.1f}",
            str(anomalies),
            f"{pic_hour}h",
            best_site,
        ]


    # ─── GRAPHE 1 : DC vs AC PAR HEURE ───────────────────────────────────────
    @app.callback(
        Output("chart-dc-ac-hour", "figure"),
        [Input("store-filtered-data", "data"),
         Input("dd-dc-ac-country",    "value")],
    )
    def chart_dc_ac(json_data, country):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if country and country != "ALL":
            dff = dff[dff["Country"] == country]
        if dff.empty: return no_data_fig(380)

        agg = dff.groupby("Hour").agg(
            DC_mean=("DC_Power", "mean"),
            AC_mean=("AC_Power", "mean"),
            DC_max =("DC_Power", "max"),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg["Hour"], y=agg["DC_mean"], name="DC Power (moy.)",
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=3), marker=dict(size=6),
            fill="tozeroy", fillcolor="rgba(249,115,22,0.12)",
            hovertemplate="<b>%{x}h</b><br>DC moy: %{y:.2f} kW<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=agg["Hour"], y=agg["AC_mean"], name="AC Power (moy.)",
            mode="lines+markers",
            line=dict(color=COLORS["accent"], width=3), marker=dict(size=6),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.10)",
            hovertemplate="<b>%{x}h</b><br>AC moy: %{y:.2f} kW<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=list(agg["Hour"]) + list(agg["Hour"][::-1]),
            y=list(agg["DC_mean"]) + list(agg["AC_mean"][::-1]),
            fill="toself", fillcolor="rgba(239,68,68,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Perte conversion", hoverinfo="skip",
        ))
        if not agg.empty:
            peak_h = int(agg.loc[agg["DC_max"].idxmax(), "Hour"])
            fig.add_vline(x=peak_h, line_dash="dot", line_color=COLORS["warning"],
                          annotation_text=f"⚡ Pic: {peak_h}h",
                          annotation_font_color=COLORS["warning"],
                          annotation_position="top right")

        layout = plotly_layout(height=380)
        layout.update(
            xaxis=dict(**layout.get("xaxis", {}), title="Heure de la journée",
                       tickvals=list(range(0,24,2)), ticktext=[f"{h}h" for h in range(0,24,2)]),
            yaxis=dict(**layout.get("yaxis", {}), title="Puissance (kW)"),
        )
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 2 : PRODUCTION CUMULÉE JOURNALIÈRE ───────────────────────────
    @app.callback(
        Output("chart-daily-cumul", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_daily_cumul(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(380)

        fig = go.Figure()
        has_trace = False

        for country, color in COUNTRY_COLORS.items():
            sub = dff[dff["Country"] == country]
            if sub.empty: continue
            agg = sub.groupby("Hour")["Daily_Yield"].mean().reset_index()
            if agg.empty: continue
            # ✅ FIX : COUNTRY_FILL rgba — plus de f"{color}18"
            fig.add_trace(go.Scatter(
                x=agg["Hour"], y=agg["Daily_Yield"],
                name=COUNTRY_FLAGS[country],
                mode="lines+markers",
                line=dict(color=color, width=2.5), marker=dict(size=5),
                fill="tozeroy", fillcolor=COUNTRY_FILL[country],
                hovertemplate=(
                    f"<b>{COUNTRY_FLAGS[country]}</b>"
                    "<br>Heure: %{x}h"
                    "<br>Daily Yield moy: %{y:.1f} kWh"
                    "<extra></extra>"
                ),
            ))
            has_trace = True

        if not has_trace: return no_data_fig(380)

        layout = plotly_layout(height=380)
        layout.update(
            xaxis=dict(**layout.get("xaxis", {}), title="Heure",
                       tickvals=list(range(0,24,3)), ticktext=[f"{h}h" for h in range(0,24,3)]),
            yaxis=dict(**layout.get("yaxis", {}), title="Daily Yield moyen (kWh)"),
        )
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 3 : RENDEMENT PAR MOIS ───────────────────────────────────────
    @app.callback(
        Output("chart-efficiency-month", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_efficiency_month(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        dff_active = dff[dff["DC_Power"] > 0].copy()
        if dff_active.empty: return no_data_fig(360)

        agg = dff_active.groupby(["Month", "Country"])["Efficiency"].mean().reset_index()
        agg["Month_Name"] = agg["Month"].map(MONTH_NAMES)

        fig = go.Figure()
        for country, color in COUNTRY_COLORS.items():
            sub = agg[agg["Country"] == country]
            if sub.empty: continue
            fig.add_trace(go.Bar(
                x=sub["Month_Name"], y=sub["Efficiency"],
                name=COUNTRY_FLAGS[country], marker_color=color, opacity=0.85,
                hovertemplate=(
                    f"<b>{COUNTRY_FLAGS[country]}</b>"
                    "<br>Mois: %{x}<br>Rendement: %{y:.1f}%<extra></extra>"
                ),
            ))
        fig.add_hline(y=90, line_dash="dash", line_color=COLORS["warning"],
                      annotation_text="Seuil 90%", annotation_font_color=COLORS["warning"])

        layout = plotly_layout(height=360)
        layout.update(barmode="group",
                      yaxis=dict(**layout.get("yaxis",{}), title="Rendement AC/DC (%)", range=[75,105]))
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 4 : TOTAL YIELD PAR PAYS ─────────────────────────────────────
    @app.callback(
        Output("chart-total-by-country", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_total_country(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(360)

        agg = dff.groupby("Country").agg(
            DC_total=("DC_Power","sum"),
            AC_total=("AC_Power","sum"),
        ).reset_index().sort_values("DC_total", ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=[COUNTRY_FLAGS.get(c,c) for c in agg["Country"]], x=agg["DC_total"],
            name="DC Total", orientation="h", marker_color=COLORS["primary"],
            hovertemplate="<b>%{y}</b><br>DC Total: %{x:.0f} kWh<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            y=[COUNTRY_FLAGS.get(c,c) for c in agg["Country"]], x=agg["AC_total"],
            name="AC Total", orientation="h", marker_color=COLORS["accent"],
            hovertemplate="<b>%{y}</b><br>AC Total: %{x:.0f} kWh<extra></extra>",
        ))
        layout = plotly_layout(height=360)
        layout.update(barmode="overlay",
                      xaxis=dict(**layout.get("xaxis",{}), title="Production totale (kWh)"),
                      bargap=0.3)
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 5 : TOTAL YIELD TREND ────────────────────────────────────────
    @app.callback(
        Output("chart-total-yield-trend", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_total_yield_trend(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(350)

        fig = go.Figure()
        has_trace = False

        for country, color in COUNTRY_COLORS.items():
            sub = dff[dff["Country"] == country].copy()
            if sub.empty: continue
            try:
                # ✅ FIX : utiliser colonne "Date" (string) — DateTime exclu du store
                agg = sub.groupby("Date")["Total_Yield"].max().reset_index()
                if agg.empty: continue
                # ✅ FIX : fillcolor rgba — plus de f"{color}15"
                fig.add_trace(go.Scatter(
                    x=agg["Date"], y=agg["Total_Yield"],
                    name=COUNTRY_FLAGS[country],
                    mode="lines",
                    line=dict(color=color, width=2),
                    fill="tozeroy",
                    fillcolor=COUNTRY_FILL_LIGHT[country],
                    hovertemplate=(
                        f"<b>{COUNTRY_FLAGS[country]}</b>"
                        "<br>Date: %{x}"
                        "<br>Total Yield: %{y:,.0f} kWh"
                        "<extra></extra>"
                    ),
                ))
                has_trace = True
            except Exception:
                continue

        if not has_trace: return no_data_fig(350)

        layout = plotly_layout(height=350)
        layout.update(yaxis=dict(**layout.get("yaxis",{}), title="Total Yield cumulé (kWh)"))
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 6 : HEATMAP IRRADIATION ──────────────────────────────────────
    @app.callback(
        Output("chart-heatmap", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_heatmap(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(420)

        pivot = dff.groupby(["Month","Hour"])["DC_Power"].mean().reset_index()
        pivot_table = pivot.pivot(index="Month", columns="Hour", values="DC_Power").fillna(0)
        y_labels = [MONTH_NAMES.get(m, str(m)) for m in pivot_table.index]

        fig = go.Figure(go.Heatmap(
            z=pivot_table.values,
            x=[f"{h}h" for h in pivot_table.columns],
            y=y_labels,
            colorscale=[
                [0.0,"#0F172A"],[0.2,"#1e3a5f"],[0.4,"#1d4ed8"],
                [0.6,"#f97316"],[0.8,"#fbbf24"],[1.0,"#fef08a"],
            ],
            hovertemplate="<b>%{y} — %{x}</b><br>DC Power moy: %{z:.2f} kW<extra></extra>",
            colorbar=dict(title="DC Power (kW)",
                          titlefont=dict(color=COLORS["text"]),
                          tickfont=dict(color=COLORS["text"]),
                          bgcolor="rgba(30,41,59,0.8)"),
        ))
        layout = plotly_layout(height=420)
        layout.update(xaxis=dict(**layout.get("xaxis",{}), title="Heure"),
                      yaxis=dict(**layout.get("yaxis",{}), title="Mois"))
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 7 : SCATTER TEMP MODULE vs DC ────────────────────────────────
    @app.callback(
        Output("chart-temp-dc", "figure"),
        [Input("store-filtered-data", "data"),
         Input("dd-scatter-country",  "value")],
    )
    def chart_temp_dc(json_data, country):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if country and country != "ALL":
            dff = dff[dff["Country"] == country]
        active = dff[dff["DC_Power"] > 0]
        if active.empty: return no_data_fig(420)

        sample = active.sample(min(3000, len(active)), random_state=42)
        fig = go.Figure()

        for c, color in COUNTRY_COLORS.items():
            sub = sample[sample["Country"] == c]
            if sub.empty: continue
            fig.add_trace(go.Scatter(
                x=sub["Module_Temperature"], y=sub["DC_Power"],
                mode="markers", name=COUNTRY_FLAGS[c],
                marker=dict(color=color, size=4, opacity=0.6),
                hovertemplate=(
                    f"<b>{COUNTRY_FLAGS[c]}</b>"
                    "<br>T° Module: %{x:.1f}°C"
                    "<br>DC Power: %{y:.2f} kW<extra></extra>"
                ),
            ))

        if len(sample) > 10:
            try:
                xs = sample["Module_Temperature"].values
                ys = sample["DC_Power"].values
                coefs = np.polyfit(xs, ys, 2)
                xs_s  = np.linspace(xs.min(), xs.max(), 100)
                fig.add_trace(go.Scatter(
                    x=xs_s, y=np.polyval(coefs, xs_s),
                    mode="lines", name="Tendance quadratique",
                    line=dict(color=COLORS["warning"], width=2.5, dash="dot"),
                    hoverinfo="skip",
                ))
            except Exception:
                pass

        layout = plotly_layout(height=420)
        layout.update(xaxis=dict(**layout.get("xaxis",{}), title="Température Module (°C)"),
                      yaxis=dict(**layout.get("yaxis",{}), title="DC Power (kW)"))
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 8 : IRRADIATION PAR HEURE ────────────────────────────────────
    @app.callback(
        Output("chart-irrad-hour", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_irrad_hour(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(340)

        fig = go.Figure()
        has_trace = False

        for country, color in COUNTRY_COLORS.items():
            sub = dff[dff["Country"] == country]
            if sub.empty: continue
            agg = sub.groupby("Hour")["Irradiation"].agg(["mean","max","min"]).reset_index()
            if agg.empty: continue

            # ✅ FIX : COUNTRY_FILL rgba — plus de f"{color}20"
            fig.add_trace(go.Scatter(
                x=list(agg["Hour"]) + list(agg["Hour"][::-1]),
                y=list(agg["max"])  + list(agg["min"][::-1]),
                fill="toself", fillcolor=COUNTRY_FILL[country],
                line=dict(color="rgba(0,0,0,0)"),
                name=f"{COUNTRY_FLAGS[country]} (plage)",
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=agg["Hour"], y=agg["mean"],
                name=COUNTRY_FLAGS[country],
                mode="lines+markers",
                line=dict(color=color, width=2), marker=dict(size=5),
                hovertemplate=(
                    f"<b>{COUNTRY_FLAGS[country]}</b>"
                    "<br>Heure: %{x}h"
                    "<br>Irrad. moy: %{y:.3f} kW/m²<extra></extra>"
                ),
            ))
            has_trace = True

        if not has_trace: return no_data_fig(340)

        layout = plotly_layout(height=340)
        layout.update(
            xaxis=dict(**layout.get("xaxis",{}), title="Heure",
                       tickvals=list(range(0,24,2)), ticktext=[f"{h}h" for h in range(0,24,2)]),
            yaxis=dict(**layout.get("yaxis",{}), title="Irradiation moy. (kW/m²)"),
        )
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 9 : TEMPÉRATURE AMBIANTE vs MODULE ───────────────────────────
    @app.callback(
        Output("chart-temp-compare", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_temp_compare(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(340)

        agg = dff.groupby("Hour").agg(
            Ambient_mean=("Ambient_Temperature","mean"),
            Module_mean =("Module_Temperature", "mean"),
        ).reset_index()
        agg["Delta"] = agg["Module_mean"] - agg["Ambient_mean"]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=agg["Hour"], y=agg["Ambient_mean"], name="T° Ambiante (°C)",
            mode="lines+markers", line=dict(color=COLORS["accent"], width=2.5),
            hovertemplate="<b>Heure: %{x}h</b><br>T° Ambiante: %{y:.1f}°C<extra></extra>",
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=agg["Hour"], y=agg["Module_mean"], name="T° Module (°C)",
            mode="lines+markers", line=dict(color=COLORS["danger"], width=2.5),
            hovertemplate="<b>Heure: %{x}h</b><br>T° Module: %{y:.1f}°C<extra></extra>",
        ), secondary_y=False)
        fig.add_trace(go.Bar(
            x=agg["Hour"], y=agg["Delta"], name="ΔT (Module − Ambiant)",
            marker_color=[COLORS["warning"] if d > 10 else COLORS["muted"] for d in agg["Delta"]],
            opacity=0.5,
            hovertemplate="<b>ΔT Heure %{x}h</b><br>Écart: %{y:.1f}°C<extra></extra>",
        ), secondary_y=True)

        layout = plotly_layout(height=340)
        layout.update(
            xaxis=dict(**layout.get("xaxis",{}), title="Heure",
                       tickvals=list(range(0,24,2)), ticktext=[f"{h}h" for h in range(0,24,2)]),
            yaxis =dict(**layout.get("yaxis",{}), title="Température (°C)"),
            yaxis2=dict(title="ΔT (°C)", overlaying="y", side="right", showgrid=False,
                        tickfont=dict(color=COLORS["warning"]),
                        titlefont=dict(color=COLORS["warning"])),
        )
        fig.update_layout(**layout)
        return fig


    # ─── ANOMALIES ALERT ─────────────────────────────────────────────────────
    @app.callback(
        Output("anomaly-alert", "children"),
        Input("store-filtered-data", "data"),
    )
    def update_anomaly_alert(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return []

        anomalies  = dff[(dff["Hour"] >= 8) & (dff["Hour"] <= 18) & (dff["DC_Power"] == 0)]
        n          = len(anomalies)
        rate       = n / len(dff) * 100 if len(dff) > 0 else 0
        by_country = anomalies.groupby("Country").size()
        worst      = by_country.idxmax() if len(by_country) > 0 else "—"
        worst_flag = COUNTRY_FLAGS.get(worst, worst)
        worst_n    = int(by_country.get(worst, 0))

        color = COLORS["danger"] if rate > 5 else COLORS["warning"] if rate > 2 else COLORS["success"]
        icon  = "fas fa-times-circle" if rate > 5 else "fas fa-exclamation-triangle" if rate > 2 else "fas fa-check-circle"
        level = "CRITIQUE" if rate > 5 else "ATTENTION" if rate > 2 else "NORMAL"

        return html.Div(
            className="anomaly-summary",
            style={"borderLeft": f"4px solid {color}"},
            children=[
                html.Div([
                    html.I(className=f"{icon} me-2", style={"color": color}),
                    html.Strong(f"Niveau {level}", style={"color": color}),
                    html.Span(f" — {n:,} anomalies détectées ({rate:.1f}% du temps solaire)",
                              className="anomaly-count"),
                ]),
                html.Div(
                    f"Site le plus affecté : {worst_flag} ({worst_n:,} occurrences) "
                    f"| Plage concernée : 8h–18h "
                    f"| Cause probable : ombrage, panne onduleur, entretien",
                    className="anomaly-detail",
                ),
            ]
        )


    # ─── GRAPHE 10 : ANOMALIES SCATTER ───────────────────────────────────────
    @app.callback(
        Output("chart-anomalies-scatter", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_anomalies_scatter(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(400)

        fig = go.Figure()
        normal = dff[(dff["DC_Power"] > 0) | ~((dff["Hour"] >= 8) & (dff["Hour"] <= 18))]
        if not normal.empty:
            sn = normal.sample(min(2000, len(normal)), random_state=1)
            fig.add_trace(go.Scatter(
                x=sn["Hour"], y=sn["DC_Power"], mode="markers",
                name="Production normale",
                marker=dict(color=COLORS["accent"], size=3, opacity=0.3),
                hoverinfo="skip",
            ))

        anomalies = dff[(dff["Hour"] >= 8) & (dff["Hour"] <= 18) & (dff["DC_Power"] == 0)]
        if not anomalies.empty:
            np.random.seed(42)
            jitter = np.random.uniform(-0.3, 0.3, len(anomalies))
            fig.add_trace(go.Scatter(
                x=anomalies["Hour"] + jitter, y=anomalies["DC_Power"],
                mode="markers", name=f"⚠️ Anomalies ({len(anomalies):,})",
                marker=dict(color=COLORS["danger"], size=7, opacity=0.8,
                            symbol="x", line=dict(width=1, color=COLORS["danger"])),
                hovertemplate="<b>⚠️ Anomalie</b><br>Heure: %{x:.0f}h<br>DC: 0 kW<extra></extra>",
            ))

        fig.add_vrect(x0=8, x1=18, fillcolor=COLORS["warning"], opacity=0.04,
                      annotation_text="Zone solaire (8h–18h)",
                      annotation_font_color=COLORS["warning"],
                      annotation_position="top left")

        layout = plotly_layout(height=400)
        layout.update(
            xaxis=dict(**layout.get("xaxis",{}), title="Heure",
                       tickvals=list(range(0,24)), ticktext=[f"{h}h" for h in range(0,24)]),
            yaxis=dict(**layout.get("yaxis",{}), title="DC Power (kW)"),
        )
        fig.update_layout(**layout)
        return fig


    # ─── GRAPHE 11 : ANOMALIES PAR PAYS & MOIS ───────────────────────────────
    @app.callback(
        Output("chart-anomalies-bar", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_anomalies_bar(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(400)

        anomalies = dff[(dff["Hour"] >= 8) & (dff["Hour"] <= 18) & (dff["DC_Power"] == 0)]
        if anomalies.empty:
            fig = go.Figure()
            fig.add_annotation(text="✅ Aucune anomalie dans la sélection",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False, font=dict(color=COLORS["success"], size=14))
            fig.update_layout(**plotly_layout(height=400))
            return fig

        agg = anomalies.groupby(["Country","Month"]).size().reset_index(name="count")
        agg["Month_Name"] = agg["Month"].map(MONTH_NAMES)

        fig = go.Figure()
        for country, color in COUNTRY_COLORS.items():
            sub = agg[agg["Country"] == country]
            if sub.empty: continue
            fig.add_trace(go.Bar(
                x=sub["Month_Name"], y=sub["count"],
                name=COUNTRY_FLAGS[country], marker_color=color,
                hovertemplate=(
                    f"<b>{COUNTRY_FLAGS[country]}</b>"
                    "<br>Mois: %{x}<br>Anomalies: %{y}<extra></extra>"
                ),
            ))

        layout = plotly_layout(height=400)
        layout.update(barmode="stack",
                      xaxis=dict(**layout.get("xaxis",{}), title="Mois"),
                      yaxis=dict(**layout.get("yaxis",{}), title="Nombre d'anomalies"))
        fig.update_layout(**layout)
        return fig


    # ─── TABLEAU ANOMALIES ────────────────────────────────────────────────────
    @app.callback(
        Output("table-anomalies-container", "children"),
        Input("store-filtered-data", "data"),
    )
    def update_anomalies_table(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return []

        anom = dff[(dff["Hour"] >= 8) & (dff["Hour"] <= 18) & (dff["DC_Power"] == 0)].copy()
        if anom.empty:
            return html.Div("✅ Aucune anomalie détectée dans la sélection courante.",
                            className="no-data-msg")

        anom["Country_Label"] = anom["Country"].map(COUNTRY_FLAGS).fillna(anom["Country"])
        anom["Month_Name"]    = anom["Month"].map(MONTH_NAMES)
        cols = {c: c for c in ["Date","Country_Label","Month_Name","Hour",
                                "Irradiation","Ambient_Temperature","Module_Temperature"]
                if c in anom.columns}
        sub = anom[list(cols.keys())].head(200)

        return dash_table.DataTable(
            data=sub.to_dict("records"),
            columns=[{"name": c, "id": c} for c in sub.columns],
            page_size=10, sort_action="native", filter_action="native",
            style_table={"overflowX":"auto","borderRadius":"8px"},
            style_header={"backgroundColor":"#1E293B","color":"#F97316",
                          "fontWeight":"600","fontFamily":"Poppins","fontSize":"12px",
                          "border":"1px solid #334155","textAlign":"center"},
            style_cell={"backgroundColor":"#0F172A","color":"#E2E8F0",
                        "fontFamily":"Poppins","fontSize":"11px",
                        "border":"1px solid #1E293B","textAlign":"center","padding":"8px"},
            style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#1E293B"}],
        )


    # ─── TABLEAU PREVIEW ─────────────────────────────────────────────────────
    @app.callback(
        [Output("table-preview-container", "children"),
         Output("table-row-count", "children")],
        Input("store-filtered-data", "data"),
    )
    def update_preview_table(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty:
            return html.Div("Aucune donnée.", className="no-data-msg"), "0 lignes"

        wanted = ["Date","Country","DC_Power","AC_Power","Efficiency","Irradiation",
                  "Module_Temperature","Ambient_Temperature","Daily_Yield","Total_Yield","Anomalie"]
        available = [c for c in wanted if c in dff.columns]
        sub = dff[available].copy()
        sub["Country"]  = sub["Country"].map(COUNTRY_FLAGS).fillna(sub["Country"])
        sub["Anomalie"] = sub["Anomalie"].map({True:"⚠️ Oui", False:"✅ Non"})

        return (
            dash_table.DataTable(
                data=sub.head(200).to_dict("records"),
                columns=[{"name": c, "id": c} for c in available],
                page_size=15, sort_action="native", filter_action="native", export_format="csv",
                style_table={"overflowX":"auto","borderRadius":"8px"},
                style_header={"backgroundColor":"#1E293B","color":"#F97316",
                              "fontWeight":"600","fontFamily":"Poppins","fontSize":"12px",
                              "border":"1px solid #334155"},
                style_cell={"backgroundColor":"#0F172A","color":"#E2E8F0",
                            "fontFamily":"Poppins","fontSize":"11px",
                            "border":"1px solid #1E293B","padding":"8px","minWidth":"80px"},
                style_data_conditional=[
                    {"if":{"row_index":"odd"},"backgroundColor":"#1E293B"},
                    {"if":{"filter_query":'{Anomalie} = "⚠️ Oui"'},
                     "backgroundColor":"rgba(239,68,68,0.1)","color":"#EF4444"},
                ],
            ),
            f"{len(dff):,} lignes sélectionnées",
        )


    # ─── GRAPHE RÉSUMÉ STATS ─────────────────────────────────────────────────
    @app.callback(
        Output("chart-summary-stats", "figure"),
        Input("store-filtered-data", "data"),
    )
    def chart_summary_stats(json_data):
        if not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: return no_data_fig(320)

        dff_active = dff[dff["DC_Power"] > 0].copy()
        stats = dff.groupby("Country").agg(
            DC_total  =("DC_Power",   "sum"),
            AC_total  =("AC_Power",   "sum"),
            Irrad_mean=("Irradiation","mean"),
        ).reset_index()
        eff   = dff_active.groupby("Country")["Efficiency"].mean().reset_index(name="Eff_mean")
        stats = stats.merge(eff, on="Country", how="left")
        anom  = dff[(dff["Hour"]>=8)&(dff["Hour"]<=18)&(dff["DC_Power"]==0)]
        anom_c = anom.groupby("Country").size().reset_index(name="Anomalies")
        stats = stats.merge(anom_c, on="Country", how="left").fillna(0)
        stats["Country"] = stats["Country"].map(COUNTRY_FLAGS).fillna(stats["Country"])

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["🌍 Pays","⚡ DC Total (kWh)","🔌 AC Total (kWh)",
                        "📊 Rendement (%)","☀️ Irrad. Moy","⚠️ Anomalies"],
                fill_color="#1E293B", align="center",
                font=dict(color="#F97316", size=12, family="Poppins"),
                height=36, line_color="#334155",
            ),
            cells=dict(
                values=[
                    stats["Country"],
                    stats["DC_total"].apply(lambda x: f"{x:,.0f}"),
                    stats["AC_total"].apply(lambda x: f"{x:,.0f}"),
                    stats["Eff_mean"].apply(lambda x: f"{x:.1f}%" if not pd.isna(x) else "—"),
                    stats["Irrad_mean"].apply(lambda x: f"{x:.3f}"),
                    stats["Anomalies"].apply(lambda x: f"{int(x):,}"),
                ],
                fill_color="#0F172A", align="center",
                font=dict(color="#E2E8F0", size=11, family="Poppins"),
                height=32, line_color="#1E293B",
            ),
        )])
        layout = plotly_layout(height=320)
        layout.update(margin=dict(l=10,r=10,t=10,b=10))
        fig.update_layout(**layout)
        return fig


    # ─── EXPORT EXCEL ────────────────────────────────────────────────────────
    @app.callback(
        Output("download-excel", "data"),
        Input("btn-export-excel", "n_clicks"),
        State("store-filtered-data", "data"),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks, json_data):
        if not n_clicks or not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: raise PreventUpdate

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            dff.to_excel(writer, sheet_name="Données_Brutes", index=False)
            dff_active = dff[dff["DC_Power"] > 0].copy()
            kpi_df = dff.groupby("Country").agg(
                DC_Total=("DC_Power","sum"), AC_Total=("AC_Power","sum"),
                Irrad_Mean=("Irradiation","mean"),
                Temp_Module_Mean=("Module_Temperature","mean"),
            ).reset_index()
            eff = dff_active.groupby("Country")["Efficiency"].mean().reset_index(name="Rendement_Moyen_Pct")
            kpi_df = kpi_df.merge(eff, on="Country", how="left")
            kpi_df.to_excel(writer, sheet_name="KPIs_par_Pays", index=False)
            anom = dff[(dff["Hour"]>=8)&(dff["Hour"]<=18)&(dff["DC_Power"]==0)]
            anom.to_excel(writer, sheet_name="Anomalies", index=False)
            hourly = dff.groupby(["Country","Month","Hour"]).agg(
                DC_Mean=("DC_Power","mean"), AC_Mean=("AC_Power","mean"),
                Irrad_Mean=("Irradiation","mean"),
            ).reset_index()
            hourly.to_excel(writer, sheet_name="Agrégation_Horaire", index=False)
        output.seek(0)
        return dcc.send_bytes(output.read(), "solar_dashboard_export.xlsx")


    # ─── EXPORT HTML ─────────────────────────────────────────────────────────
    @app.callback(
        Output("download-html", "data"),
        Input("btn-export-html", "n_clicks"),
        State("store-filtered-data", "data"),
        prevent_initial_call=True,
    )
    def export_html(n_clicks, json_data):
        if not n_clicks or not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: raise PreventUpdate
        import plotly.io as pio

        agg_h = dff.groupby("Hour")[["DC_Power","AC_Power"]].mean().reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=agg_h["Hour"], y=agg_h["DC_Power"],
                                   name="DC Power", line=dict(color="#F97316", width=3)))
        fig1.add_trace(go.Scatter(x=agg_h["Hour"], y=agg_h["AC_Power"],
                                   name="AC Power", line=dict(color="#3B82F6", width=3)))
        fig1.update_layout(title="DC vs AC Power par Heure", template="plotly_dark")

        pivot = dff.groupby(["Month","Hour"])["DC_Power"].mean().reset_index()
        p2    = pivot.pivot(index="Month", columns="Hour", values="DC_Power").fillna(0)
        fig2  = go.Figure(go.Heatmap(z=p2.values,
                                      x=[f"{h}h" for h in p2.columns],
                                      y=[MONTH_NAMES.get(m,str(m)) for m in p2.index],
                                      colorscale="YlOrRd"))
        fig2.update_layout(title="Heatmap DC Power — Mois × Heure", template="plotly_dark")

        agg_d = dff.groupby(["Date","Country"])["Total_Yield"].max().reset_index()
        fig3  = px.line(agg_d, x="Date", y="Total_Yield", color="Country",
                        title="Évolution Total_Yield par Pays", template="plotly_dark")

        h1 = pio.to_html(fig1, full_html=False, include_plotlyjs=False)
        h2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False)
        h3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False)

        report = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<title>Rapport Solaire — SolarDash</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  body{{background:#0F172A;color:#E2E8F0;font-family:'Poppins',sans-serif;margin:0;padding:20px}}
  h1{{color:#F97316;text-align:center}} .sub{{text-align:center;color:#94A3B8;margin-bottom:30px}}
  .box{{background:#1E293B;border-radius:12px;padding:20px;margin-bottom:20px;border:1px solid #334155}}
  .foot{{text-align:center;color:#475569;margin-top:40px;font-size:12px}}
</style></head><body>
<h1>☀️ Rapport — Parc Photovoltaïque</h1>
<p class="sub">SolarDash | Réalisé par SK | {len(dff):,} mesures | 2024</p>
<div class="box"><h3>⚡ DC vs AC par Heure</h3>{h1}</div>
<div class="box"><h3>🌡️ Heatmap DC Power</h3>{h2}</div>
<div class="box"><h3>📈 Total Yield par Pays</h3>{h3}</div>
<p class="foot">SolarDash — Python 3.12 · Dash · Plotly | SK</p>
</body></html>"""
        return dcc.send_string(report, "rapport_solaire.html")


    # ─── EXPORT PDF ──────────────────────────────────────────────────────────
    @app.callback(
        Output("download-pdf", "data"),
        Input("btn-export-pdf", "n_clicks"),
        State("store-filtered-data", "data"),
        prevent_initial_call=True,
    )
    def export_pdf(n_clicks, json_data):
        if not n_clicks or not json_data: raise PreventUpdate
        dff = read_store(json_data)
        if dff.empty: raise PreventUpdate

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                             Table, TableStyle, HRFlowable)
            from reportlab.lib.enums import TA_CENTER

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                     topMargin=2*cm, bottomMargin=2*cm,
                                     leftMargin=2*cm, rightMargin=2*cm)
            styles = getSampleStyleSheet()
            t_style = ParagraphStyle("T", parent=styles["Title"], fontSize=22,
                                      textColor=colors.HexColor("#F97316"),
                                      spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold")
            h2     = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14,
                                     textColor=colors.HexColor("#3B82F6"),
                                     spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold")
            body   = ParagraphStyle("B", parent=styles["Normal"], fontSize=10,
                                     textColor=colors.HexColor("#334155"), spaceAfter=4)
            foot   = ParagraphStyle("F", parent=styles["Normal"], fontSize=9,
                                     textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER)

            dff_a  = dff[dff["DC_Power"] > 0].copy()
            kpis   = {
                "Production DC Totale (kWh)":      f"{dff['DC_Power'].sum():,.1f}",
                "Production AC Totale (kWh)":      f"{dff['AC_Power'].sum():,.1f}",
                "Rendement AC/DC Moyen (%)":        f"{dff_a['Efficiency'].mean():.1f}%",
                "Irradiation Moyenne (kW/m²)":     f"{dff['Irradiation'].mean():.3f}",
                "Température Module Moyenne (°C)": f"{dff['Module_Temperature'].mean():.1f}",
                "Anomalies Détectées":             str(int(((dff["Hour"]>=8)&(dff["Hour"]<=18)&(dff["DC_Power"]==0)).sum())),
                "Nombre de mesures":               f"{len(dff):,}",
                "Pays analysés":                   ", ".join(sorted(dff["Country"].unique())),
            }
            stats  = dff.groupby("Country").agg(
                DC=("DC_Power","sum"), AC=("AC_Power","sum"),
                Ir=("Irradiation","mean")).reset_index()
            eff_s  = dff_a.groupby("Country")["Efficiency"].mean().reset_index(name="R")
            stats  = stats.merge(eff_s, on="Country", how="left")
            an_c   = dff[(dff["Hour"]>=8)&(dff["Hour"]<=18)&(dff["DC_Power"]==0)].groupby("Country").size().reset_index(name="A")
            stats  = stats.merge(an_c, on="Country", how="left").fillna(0)
            stats["Country"] = stats["Country"].map(COUNTRY_FLAGS).fillna(stats["Country"])

            story = []
            story.append(Paragraph("☀️ RAPPORT — PARC PHOTOVOLTAÏQUE", t_style))
            story.append(Paragraph("SolarDash · Analyse de Production Solaire · 2024", body))
            story.append(Paragraph("Réalisé par SK · Python 3.12 · Dash · Plotly", body))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#F97316")))
            story.append(Spacer(1, 0.4*cm))
            story.append(Paragraph("📊 Indicateurs Clés de Performance", h2))
            kd = [["Indicateur","Valeur"]] + [[k,v] for k,v in kpis.items()]
            kt = Table(kd, colWidths=[12*cm,5*cm])
            kt.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1E293B")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#F97316")),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),10),("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#F8FAFC"),colors.white]),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E1")),("ROWHEIGHT",(0,0),(-1,-1),22),
            ]))
            story.append(kt)
            story.append(Spacer(1, 0.6*cm))
            story.append(Paragraph("🌍 Performance par Pays", h2))
            sd = [["Pays","DC (kWh)","AC (kWh)","Rendement","Irrad.","Anomalies"]] + [
                [r["Country"],f"{r['DC']:,.0f}",f"{r['AC']:,.0f}",
                 f"{r['R']:.1f}%" if not pd.isna(r["R"]) else "—",
                 f"{r['Ir']:.3f}",str(int(r["A"]))]
                for _,r in stats.iterrows()
            ]
            st = Table(sd, colWidths=[4*cm,3*cm,3*cm,3*cm,2.5*cm,2.5*cm])
            st.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1E293B")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#3B82F6")),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),10),("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#F0F9FF"),colors.white]),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E1")),("ROWHEIGHT",(0,0),(-1,-1),22),
            ]))
            story.append(st)
            story.append(Spacer(1,0.5*cm))
            story.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor("#F97316")))
            story.append(Spacer(1,0.3*cm))
            story.append(Paragraph(
                "Les données couvrent 2024 sur 4 sites (Norvège, Brésil, Inde, Australie). "
                "Pic de production à 12h–13h, rendement AC/DC moyen > 90%. "
                "Anomalies concentrées en Norvège (conditions hivernales). "
                "Forte corrélation irradiation/production sur tous les sites.", body))
            story.append(Spacer(1,0.8*cm))
            story.append(Paragraph("SolarDash — Python 3.12 · Dash · Plotly | Auteur : SK", foot))

            doc.build(story)
            buffer.seek(0)
            return dcc.send_bytes(buffer.read(), "rapport_solaire.pdf")
        except ImportError:
            raise PreventUpdate
