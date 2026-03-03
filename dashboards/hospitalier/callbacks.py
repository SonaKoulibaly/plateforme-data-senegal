from dash import Input, Output, State, dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64

def register_callbacks(app, df):
    
    # ============================================================================
    # CALLBACK 1 : INITIALISER LES DROPDOWNS
    # ============================================================================
    @app.callback(
        [Output('dept-filter', 'options'),
         Output('disease-filter', 'options'),
         Output('treatment-filter', 'options')],
        Input('dept-filter', 'id')
    )
    def initialize_dropdowns(_):
        dept_options = [{'label': dept, 'value': dept} for dept in sorted(df['Departement'].unique())]
        disease_options = [{'label': disease, 'value': disease} for disease in sorted(df['Maladie'].unique())]
        treatment_options = [{'label': treatment, 'value': treatment} for treatment in sorted(df['Traitement'].unique())]
        
        return dept_options, disease_options, treatment_options
    
    # ============================================================================
    # CALLBACK 2 : RÉINITIALISER LES FILTRES
    # ============================================================================
    @app.callback(
        [Output('dept-filter', 'value'),
         Output('disease-filter', 'value'),
         Output('treatment-filter', 'value'),
         Output('age-filter', 'value')],
        Input('reset-filters', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_filters(n_clicks):
        return None, None, None, [0, 100]
    
    # ============================================================================
    # FONCTION : GÉNÉRER DES INSIGHTS AUTOMATIQUES
    # ============================================================================
    def generate_insights(filtered_df, df_full):
        insights = []
        
        # Insight 1 : Comparaison avec dataset complet
        if len(filtered_df) < len(df_full):
            percentage = (len(filtered_df) / len(df_full)) * 100
            insights.append({
                'type': 'info',
                'icon': 'fas fa-filter',
                'title': 'Sélection active',
                'text': f"Vous analysez {len(filtered_df)} patients ({percentage:.1f}% du total)"
            })
        
        # Insight 2 : Coût élevé
        avg_cost = filtered_df['Cout'].mean()
        overall_avg = df_full['Cout'].mean()
        diff_cost = ((avg_cost - overall_avg) / overall_avg) * 100
        
        if abs(diff_cost) > 10:
            if diff_cost > 0:
                insights.append({
                    'type': 'warning',
                    'icon': 'fas fa-exclamation-triangle',
                    'title': '⚠️ Coûts élevés',
                    'text': f"Le coût moyen est {abs(diff_cost):.1f}% supérieur à la moyenne générale ({avg_cost:,.0f}€ vs {overall_avg:,.0f}€)"
                })
            else:
                insights.append({
                    'type': 'success',
                    'icon': 'fas fa-check-circle',
                    'title': '✅ Coûts optimisés',
                    'text': f"Le coût moyen est {abs(diff_cost):.1f}% inférieur à la moyenne ({avg_cost:,.0f}€ vs {overall_avg:,.0f}€)"
                })
        
        # Insight 3 : Durée de séjour
        avg_duration = filtered_df['DureeSejour'].mean()
        overall_duration = df_full['DureeSejour'].mean()
        diff_duration = ((avg_duration - overall_duration) / overall_duration) * 100
        
        if abs(diff_duration) > 15:
            if diff_duration > 0:
                insights.append({
                    'type': 'warning',
                    'icon': 'fas fa-clock',
                    'title': '⏱️ Séjours prolongés',
                    'text': f"La durée moyenne est {abs(diff_duration):.1f}% plus longue ({avg_duration:.1f} jours vs {overall_duration:.1f} jours)"
                })
            else:
                insights.append({
                    'type': 'success',
                    'icon': 'fas fa-check-circle',
                    'title': '✅ Séjours courts',
                    'text': f"La durée moyenne est {abs(diff_duration):.1f}% plus courte ({avg_duration:.1f} jours)"
                })
        
        # Insight 4 : Pathologie dominante
        if len(filtered_df) > 0:
            top_disease = filtered_df['Maladie'].value_counts().iloc[0]
            top_disease_name = filtered_df['Maladie'].value_counts().index[0]
            disease_pct = (top_disease / len(filtered_df)) * 100
            
            if disease_pct > 30:
                insights.append({
                    'type': 'info',
                    'icon': 'fas fa-disease',
                    'title': f'🏥 Pathologie dominante : {top_disease_name}',
                    'text': f"Représente {disease_pct:.1f}% des cas ({top_disease} patients)"
                })
        
        # Insight 5 : Profil d'âge
        age_60_plus = len(filtered_df[filtered_df['Age'] >= 60])
        if age_60_plus > 0:
            age_60_pct = (age_60_plus / len(filtered_df)) * 100
            if age_60_pct > 50:
                insights.append({
                    'type': 'info',
                    'icon': 'fas fa-user-friends',
                    'title': '👴 Population âgée dominante',
                    'text': f"{age_60_pct:.1f}% des patients ont 60 ans ou plus ({age_60_plus} patients)"
                })
        
        # Insight 6 : Recommandation basée sur les données
        if avg_duration > 8 and avg_cost > 4000:
            insights.append({
                'type': 'primary',
                'icon': 'fas fa-lightbulb',
                'title': '💡 RECOMMANDATION',
                'text': "Durée et coûts élevés : Envisager des protocoles de sortie précoce ou hospitalisation à domicile"
            })
        
        # Insight 7 : Top département
        if len(filtered_df) > 0:
            top_dept = filtered_df['Departement'].value_counts().iloc[0]
            top_dept_name = filtered_df['Departement'].value_counts().index[0]
            dept_pct = (top_dept / len(filtered_df)) * 100
            
            if dept_pct > 25:
                insights.append({
                    'type': 'info',
                    'icon': 'fas fa-hospital',
                    'title': f'🏥 Département le plus sollicité : {top_dept_name}',
                    'text': f"{dept_pct:.1f}% des admissions ({top_dept} patients)"
                })
        
        return insights
    
    # ============================================================================
    # CALLBACK 3 : DASHBOARD PRINCIPAL + INSIGHTS
    # ============================================================================
    @app.callback(
        [Output('total-patients', 'children'),
         Output('avg-duration', 'children'),
         Output('avg-cost', 'children'),
         Output('total-cost', 'children'),
         Output('trend-patients', 'children'),
         Output('trend-duration', 'children'),
         Output('trend-cost', 'children'),
         Output('trend-total', 'children'),
         Output('insights-content', 'children'),
         Output('dept-chart', 'figure'),
         Output('disease-chart', 'figure'),
         Output('treatment-cost-chart', 'figure'),
         Output('duration-disease-chart', 'figure'),
         Output('age-gender-chart', 'figure'),
         Output('monthly-admissions-chart', 'figure'),
         Output('cost-duration-scatter', 'figure'),
         Output('admission-vs-sortie-chart', 'figure'),
         Output('sortie-weekday-chart', 'figure')],
        [Input('dept-filter', 'value'),
         Input('disease-filter', 'value'),
         Input('treatment-filter', 'value'),
         Input('age-filter', 'value')]
    )
    def update_dashboard(dept_values, disease_values, treatment_values, age_range):
        # Filtrer les données
        filtered_df = df.copy()
        
        if dept_values:
            filtered_df = filtered_df[filtered_df['Departement'].isin(dept_values)]
        
        if disease_values:
            filtered_df = filtered_df[filtered_df['Maladie'].isin(disease_values)]
        
        if treatment_values:
            filtered_df = filtered_df[filtered_df['Traitement'].isin(treatment_values)]
        
        if age_range:
            filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & 
                                     (filtered_df['Age'] <= age_range[1])]
        
        # KPIs
        total_patients = f"{len(filtered_df):,}"
        avg_duration = f"{filtered_df['DureeSejour'].mean():.1f}"
        avg_cost = f"{filtered_df['Cout'].mean():,.0f}"
        total_cost = f"{filtered_df['Cout'].sum():,.0f}"
        
        # Tendances (comparaison avec dataset complet)
        trend_patients = ""
        trend_duration = ""
        trend_cost = ""
        trend_total = ""
        
        if len(filtered_df) < len(df):
            pct = (len(filtered_df) / len(df)) * 100
            trend_patients = f"📊 {pct:.0f}% du total"
            
            avg_dur_filtered = filtered_df['DureeSejour'].mean()
            avg_dur_full = df['DureeSejour'].mean()
            diff_dur = ((avg_dur_filtered - avg_dur_full) / avg_dur_full) * 100
            if diff_dur > 0:
                trend_duration = f"↗️ +{diff_dur:.0f}% vs moyenne"
            else:
                trend_duration = f"↘️ {diff_dur:.0f}% vs moyenne"
            
            avg_cost_filtered = filtered_df['Cout'].mean()
            avg_cost_full = df['Cout'].mean()
            diff_cost = ((avg_cost_filtered - avg_cost_full) / avg_cost_full) * 100
            if diff_cost > 0:
                trend_cost = f"↗️ +{diff_cost:.0f}% vs moyenne"
            else:
                trend_cost = f"↘️ {diff_cost:.0f}% vs moyenne"
            
            total_cost_filtered = filtered_df['Cout'].sum()
            total_cost_full = df['Cout'].sum()
            pct_total = (total_cost_filtered / total_cost_full) * 100
            trend_total = f"📊 {pct_total:.0f}% du total"
        
        # Générer les insights
        insights = generate_insights(filtered_df, df)
        insights_html = []
        
        if insights:
            for insight in insights:
                color_map = {
                    'success': 'success',
                    'warning': 'warning',
                    'info': 'info',
                    'primary': 'primary'
                }
                color = color_map.get(insight['type'], 'secondary')
                
                insights_html.append(
                    html.Div([
                        html.I(className=f"{insight['icon']} me-2"),
                        html.Strong(insight['title'] + ": ", className='me-1'),
                        html.Span(insight['text'])
                    ], className=f'alert alert-{color} mb-2')
                )
        else:
            insights_html = [html.P("Aucun insight particulier pour cette sélection.", 
                                   className='text-muted text-center')]
        
        # Couleurs modernes
        color_palette = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', 
                        '#fa709a', '#fee140', '#30cfd0', '#a8edea', '#fed6e3']
        
        # Graphiques (code identique à avant)
        # 1. Département
        dept_data = filtered_df['Departement'].value_counts().reset_index()
        dept_data.columns = ['Departement', 'Count']
        
        fig_dept = px.bar(
            dept_data,
            x='Departement',
            y='Count',
            color='Departement',
            color_discrete_sequence=color_palette,
            title=""
        )
        fig_dept.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        fig_dept.update_traces(hovertemplate='<b>%{x}</b><br>Patients: %{y}<extra></extra>')
        
        # 2. Pathologie
        disease_data = filtered_df['Maladie'].value_counts().reset_index()
        disease_data.columns = ['Maladie', 'Count']
        
        fig_disease = px.pie(
            disease_data,
            names='Maladie',
            values='Count',
            hole=0.5,
            color_discrete_sequence=color_palette,
            title=""
        )
        fig_disease.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        fig_disease.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Patients: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )
        
        # 3. Coût par traitement
        treatment_cost = filtered_df.groupby('Traitement')['Cout'].mean().reset_index()
        treatment_cost = treatment_cost.sort_values('Cout', ascending=True)
        
        fig_treatment = px.bar(
            treatment_cost,
            y='Traitement',
            x='Cout',
            orientation='h',
            color='Cout',
            color_continuous_scale='Viridis',
            title=""
        )
        fig_treatment.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Coût Moyen (€)'),
            yaxis=dict(showgrid=False, title=''),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        fig_treatment.update_traces(hovertemplate='<b>%{y}</b><br>Coût moyen: %{x:,.0f}€<extra></extra>')
        
        # 4. Durée par pathologie
        duration_disease = filtered_df.groupby('Maladie')['DureeSejour'].mean().reset_index()
        duration_disease = duration_disease.sort_values('DureeSejour', ascending=False)
        
        fig_duration = px.bar(
            duration_disease,
            x='Maladie',
            y='DureeSejour',
            color='DureeSejour',
            color_continuous_scale='RdYlGn_r',
            title=""
        )
        fig_duration.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=False, title=''),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Durée Moyenne (jours)'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        fig_duration.update_traces(hovertemplate='<b>%{x}</b><br>Durée moyenne: %{y:.1f} jours<extra></extra>')
        
        # 5. Âge et sexe
        fig_age_gender = px.histogram(
            filtered_df,
            x='Age',
            color='Sexe',
            nbins=20,
            color_discrete_map={'M': '#667eea', 'F': '#f093fb'},
            title=""
        )
        fig_age_gender.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=False, title='Âge'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Nombre de patients'),
            legend=dict(title='Sexe', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            barmode='group'
        )
        
        # 6. Évolution mensuelle
        filtered_df['Mois'] = filtered_df['DateAdmission'].dt.to_period('M').astype(str)
        monthly_data = filtered_df.groupby('Mois').size().reset_index(name='Admissions')
        
        fig_monthly = px.line(
            monthly_data,
            x='Mois',
            y='Admissions',
            markers=True,
            title=""
        )
        fig_monthly.update_traces(
            line_color='#667eea',
            line_width=3,
            marker=dict(size=8, color='#764ba2'),
            hovertemplate='<b>%{x}</b><br>Admissions: %{y}<extra></extra>'
        )
        fig_monthly.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=False, title='Mois'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title="Nombre d'admissions"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        
        # 7. Scatter Coût vs Durée
        fig_scatter = px.scatter(
            filtered_df,
            x='DureeSejour',
            y='Cout',
            color='Departement',
            size='Age',
            hover_data=['Maladie', 'Traitement', 'Age', 'Sexe'],
            color_discrete_sequence=color_palette,
            title=""
        )
        fig_scatter.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Durée de Séjour (jours)'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Coût (€)'),
            legend=dict(title='Département', orientation='v'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=400
        )
        
        # 8. Flux Admissions vs Sorties
        filtered_df['MoisAdmission'] = filtered_df['DateAdmission'].dt.to_period('M').astype(str)
        filtered_df['MoisSortie'] = filtered_df['DateSortie'].dt.to_period('M').astype(str)
        
        admissions_monthly = filtered_df.groupby('MoisAdmission').size().reset_index(name='Admissions')
        sorties_monthly = filtered_df.groupby('MoisSortie').size().reset_index(name='Sorties')
        
        admissions_monthly.columns = ['Mois', 'Admissions']
        sorties_monthly.columns = ['Mois', 'Sorties']
        
        flux_data = admissions_monthly.merge(sorties_monthly, on='Mois', how='outer').fillna(0)
        
        fig_flux = go.Figure()
        fig_flux.add_trace(go.Scatter(
            x=flux_data['Mois'],
            y=flux_data['Admissions'],
            mode='lines+markers',
            name='Admissions',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea')
        ))
        fig_flux.add_trace(go.Scatter(
            x=flux_data['Mois'],
            y=flux_data['Sorties'],
            mode='lines+markers',
            name='Sorties',
            line=dict(color='#43e97b', width=3),
            marker=dict(size=8, color='#43e97b')
        ))
        
        fig_flux.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=False, title='Mois'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Nombre de patients'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            hovermode='x unified'
        )
        
        # 9. Jours de sortie
        filtered_df['JourSortie'] = filtered_df['DateSortie'].dt.day_name()
        
        jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        sortie_weekday = filtered_df['JourSortie'].value_counts().reindex(jours_ordre, fill_value=0).reset_index()
        sortie_weekday.columns = ['Jour', 'Count']
        sortie_weekday['JourFR'] = jours_fr
        
        fig_weekday = px.bar(
            sortie_weekday,
            x='JourFR',
            y='Count',
            color='Count',
            color_continuous_scale='Viridis',
            title=""
        )
        fig_weekday.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2d3748', size=12),
            xaxis=dict(showgrid=False, title='Jour de la semaine'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', title='Nombre de sorties'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        fig_weekday.update_traces(hovertemplate='<b>%{x}</b><br>Sorties: %{y}<extra></extra>')
        
        return (total_patients, avg_duration, avg_cost, total_cost,
                trend_patients, trend_duration, trend_cost, trend_total,
                insights_html,
                fig_dept, fig_disease, fig_treatment, fig_duration,
                fig_age_gender, fig_monthly, fig_scatter, fig_flux, fig_weekday)
    
    # ============================================================================
    # CALLBACK 4 : TÉLÉCHARGER EXCEL
    # ============================================================================
    @app.callback(
        Output("download-excel", "data"),
        Input("btn-download-excel", "n_clicks"),
        [State('dept-filter', 'value'),
         State('disease-filter', 'value'),
         State('treatment-filter', 'value'),
         State('age-filter', 'value')],
        prevent_initial_call=True
    )
    def download_excel(n_clicks, dept_values, disease_values, treatment_values, age_range):
        # Filtrer les données
        filtered_df = df.copy()
        
        if dept_values:
            filtered_df = filtered_df[filtered_df['Departement'].isin(dept_values)]
        
        if disease_values:
            filtered_df = filtered_df[filtered_df['Maladie'].isin(disease_values)]
        
        if treatment_values:
            filtered_df = filtered_df[filtered_df['Traitement'].isin(treatment_values)]
        
        if age_range:
            filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & 
                                     (filtered_df['Age'] <= age_range[1])]
        
        # Créer un buffer en mémoire
        output = io.BytesIO()
        
        # Créer le fichier Excel avec pandas
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='Données', index=False)
            
            # Créer une feuille de statistiques
            stats_df = pd.DataFrame({
                'Indicateur': ['Nombre de patients', 'Durée moyenne (jours)', 'Coût moyen (€)', 'Coût total (€)'],
                'Valeur': [
                    len(filtered_df),
                    f"{filtered_df['DureeSejour'].mean():.1f}",
                    f"{filtered_df['Cout'].mean():,.0f}",
                    f"{filtered_df['Cout'].sum():,.0f}"
                ]
            })
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
        
        output.seek(0)
        
        return dcc.send_bytes(output.getvalue(), 
                             f"hospital_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    
    # ============================================================================
    # CALLBACK 5 : TÉLÉCHARGER HTML
    # ============================================================================
    @app.callback(
        Output("download-html", "data"),
        Input("btn-download-html", "n_clicks"),
        [State('dept-filter', 'value'),
         State('disease-filter', 'value'),
         State('treatment-filter', 'value'),
         State('age-filter', 'value')],
        prevent_initial_call=True
    )
    def download_html(n_clicks, dept_values, disease_values, treatment_values, age_range):
        # Filtrer les données
        filtered_df = df.copy()
        
        if dept_values:
            filtered_df = filtered_df[filtered_df['Departement'].isin(dept_values)]
        
        if disease_values:
            filtered_df = filtered_df[filtered_df['Maladie'].isin(disease_values)]
        
        if treatment_values:
            filtered_df = filtered_df[filtered_df['Traitement'].isin(treatment_values)]
        
        if age_range:
            filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & 
                                     (filtered_df['Age'] <= age_range[1])]
        
        # Générer statistiques
        stats_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Rapport DATA CARE - {datetime.now().strftime('%d/%m/%Y %H:%M')}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                       margin: 40px; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); 
                         gap: 20px; margin: 30px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 10px; 
                             box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #666; margin-top: 10px; }}
                table {{ width: 100%; border-collapse: collapse; background: white; 
                        border-radius: 10px; overflow: hidden; margin-top: 20px; }}
                th {{ background: #667eea; color: white; padding: 15px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #f9f9f9; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 RAPPORT DATA CARE</h1>
                <p>Analyse des Données Hospitalières</p>
                <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{len(filtered_df)}</div>
                    <div class="stat-label">👥 Patients</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{filtered_df['DureeSejour'].mean():.1f}</div>
                    <div class="stat-label">📅 Durée Moyenne (jours)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{filtered_df['Cout'].mean():,.0f}€</div>
                    <div class="stat-label">💶 Coût Moyen</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{filtered_df['Cout'].sum():,.0f}€</div>
                    <div class="stat-label">💰 Coût Total</div>
                </div>
            </div>
            
            <h2>📋 Données Détaillées</h2>
            {filtered_df.to_html(index=False, classes='data-table')}
            
            <div class="footer">
                <p>© 2025 DATA CARE - Optimizing Patient Care with Data Intelligence</p>
            </div>
        </body>
        </html>
        """
        
        return dict(content=stats_html, 
                   filename=f"rapport_hospital_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    
    # ============================================================================
    # CALLBACK 6 : TÉLÉCHARGER PDF (avec reportlab)
    # ============================================================================
    @app.callback(
        Output("download-pdf", "data"),
        Input("btn-download-pdf", "n_clicks"),
        [State('dept-filter', 'value'),
         State('disease-filter', 'value'),
         State('treatment-filter', 'value'),
         State('age-filter', 'value')],
        prevent_initial_call=True
    )
    def download_pdf(n_clicks, dept_values, disease_values, treatment_values, age_range):
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Filtrer les données
            filtered_df = df.copy()
            
            if dept_values:
                filtered_df = filtered_df[filtered_df['Departement'].isin(dept_values)]
            
            if disease_values:
                filtered_df = filtered_df[filtered_df['Maladie'].isin(disease_values)]
            
            if treatment_values:
                filtered_df = filtered_df[filtered_df['Traitement'].isin(treatment_values)]
            
            if age_range:
                filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & 
                                         (filtered_df['Age'] <= age_range[1])]
            
            # Créer un buffer
            buffer = io.BytesIO()
            
            # Créer le PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Titre
            elements.append(Paragraph("RAPPORT DATA CARE", title_style))
            elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}", 
                                     styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Statistiques
            stats_data = [
                ['Indicateur', 'Valeur'],
                ['Nombre de patients', f"{len(filtered_df)}"],
                ['Durée moyenne (jours)', f"{filtered_df['DureeSejour'].mean():.1f}"],
                ['Coût moyen (€)', f"{filtered_df['Cout'].mean():,.0f}"],
                ['Coût total (€)', f"{filtered_df['Cout'].sum():,.0f}"]
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Tableau de données (limité aux 50 premières lignes pour le PDF)
            elements.append(Paragraph("Données (50 premières lignes)", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Sélectionner quelques colonnes clés
            df_pdf = filtered_df[['PatientID', 'Age', 'Sexe', 'Departement', 'Maladie', 
                                 'DureeSejour', 'Cout']].head(50)
            
            # Convertir en liste pour le tableau
            data = [df_pdf.columns.tolist()] + df_pdf.values.tolist()
            
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            elements.append(table)
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("© 2025 DATA CARE - Optimizing Patient Care with Data Intelligence", 
                                     styles['Normal']))
            
            # Construire le PDF
            doc.build(elements)
            
            buffer.seek(0)
            
            return dcc.send_bytes(buffer.getvalue(), 
                                 f"rapport_hospital_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        except ImportError:
            # Si reportlab n'est pas installé, retourner un message
            message = """
            ⚠️ ERREUR : reportlab n'est pas installé
            
            Pour générer des PDF, installez :
            pip install reportlab
            
            Puis relancez l'application.
            """
            
            return dict(content=message, 
                       filename=f"erreur_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")