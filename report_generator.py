import os
from datetime import datetime

def generate_combined_report(satellite=None, irrigation=None, disease=None, export=None, heatmaps=[]):
    """
    Génère un rapport HTML complet avec toutes les sections.
    
    satellite : dict contenant les résultats de l'analyse satellite
    irrigation : dict du dernier calcul irrigation
    disease : dict du dernier diagnostic maladies
    export : dict de la recommandation export
    heatmaps : liste des chemins vers les images heatmaps
    """
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join('reports', f'report_complete_{timestamp}.html')
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Rapport Feralyx Complet</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #1e1e2e; margin: 0; padding: 0; }}
            h1, h2 {{ color: #0b3d91; }}
            h1 {{ text-align: center; padding: 20px; background-color: #e0e0e0; margin: 0; }}
            section {{ padding: 20px; margin: 10px 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0px 0px 5px #aaa; }}
            img {{ max-width: 100%; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }}
            pre {{ background-color: #2d2d44; color: #cdd6f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>FERALYX V2.0 - Rapport Complet</h1>
    """

    # Section Analyse Satellite
    if satellite:
        html += "<section><h2>🛰️ Analyse Satellite</h2><pre>"
        for k, v in satellite.items():
            html += f"{k} : {v}\n"
        html += "</pre></section>"

    # Section Heatmaps
    if heatmaps:
        html += "<section><h2>🗺️ Heatmaps</h2>"
        for hm in heatmaps:
            if os.path.exists(hm):
                html += f"<img src='{hm}' alt='Heatmap'>"
            else:
                html += f"<p>Heatmap non trouvée : {hm}</p>"
        html += "</section>"

    # Section Prédiction Irrigation
    if irrigation:
        html += "<section><h2>💧 Prédiction Irrigation</h2><pre>"
        for k, v in irrigation.items():
            html += f"{k} : {v}\n"
        html += "</pre></section>"

    # Section Diagnostic Maladies
    if disease:
        html += "<section><h2>🦠 Diagnostic Maladies</h2><pre>"
        for k, v in disease.items():
            html += f"{k} : {v}\n"
        html += "</pre></section>"

    # Section Recommandation Export
    if export:
        html += "<section><h2>🌍 Recommandation Export</h2><pre>"
        for k, v in export.items():
            html += f"{k} : {v}\n"
        html += "</pre></section>"

    html += "</body></html>"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return report_path
