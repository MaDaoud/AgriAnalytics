"""
Feralyx V2.0 - Générateur Heatmaps Interactives
Cartes de chaleur pour fertilité, opportunités, risques
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np
import pandas as pd
from datetime import datetime
import os
import json
from branca.colormap import LinearColormap

try:
    from sentinel_analyzer import SentinelParcelAnalyzer
    SENTINEL_AVAILABLE = True
except:
    SENTINEL_AVAILABLE = False

class HeatmapGenerator:
    """Génère heatmaps interactives pour analyses agricoles"""
    
    def __init__(self):
        if SENTINEL_AVAILABLE:
            self.analyzer = SentinelParcelAnalyzer()
        else:
            self.analyzer = None
        
        # Définir zones d'intérêt
        self.regions = {
            'tunisie': {
                'center': [35.5, 9.5],
                'zoom': 7,
                'bounds': [[33.0, 7.5], [37.5, 11.5]]
            },
            'france': {
                'center': [46.5, 2.0],
                'zoom': 6,
                'bounds': [[42.0, -5.0], [51.0, 8.0]]
            },
            'italie': {
                'center': [42.5, 12.5],
                'zoom': 6,
                'bounds': [[36.0, 6.0], [47.0, 18.5]]
            },
            'espagne': {
                'center': [40.0, -4.0],
                'zoom': 6,
                'bounds': [[36.0, -9.3], [43.8, 3.3]]
            }
        }
        
        print("🗺️ Générateur de heatmaps initialisé")
    
    def generate_opportunity_heatmap(self, country='tunisie', resolution=20, output_file=None):
        """
        Génère heatmap d'opportunités d'investissement
        
        Args:
            country: Pays à analyser
            resolution: Nombre de points par axe
            output_file: Fichier HTML de sortie
        
        Returns:
            Chemin du fichier HTML généré
        """
        print(f"\n🗺️ Génération heatmap opportunités : {country.upper()}")
        
        region = self.regions.get(country, self.regions['tunisie'])
        bounds = region['bounds']
        
        # Créer grille de points
        print(f"   📊 Génération grille {resolution}x{resolution} points...")
        lats = np.linspace(bounds[0][0], bounds[1][0], resolution)
        lons = np.linspace(bounds[0][1], bounds[1][1], resolution)
        
        # Analyser chaque point
        data_points = []
        scores = []
        
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                # Simuler analyse (pour démo rapide)
                score = self._simulate_opportunity_score(lat, lon, country)
                
                data_points.append({
                    'lat': lat,
                    'lon': lon,
                    'score': score,
                    'fertilite': score * np.random.uniform(0.8, 1.2),
                    'culture': self._get_best_culture(score)
                })
                scores.append([lat, lon, score])
        
        print(f"   ✅ {len(data_points)} points analysés")
        
        # Créer carte Folium
        print("   🗺️ Création carte interactive...")
        m = folium.Map(
            location=region['center'],
            zoom_start=region['zoom'],
            tiles='OpenStreetMap'
        )
        
        # Ajouter heatmap
        heat_data = [[point['lat'], point['lon'], point['score']] for point in data_points]
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_opacity=0.8,
            radius=25,
            blur=20,
            gradient={
                0.0: 'blue',
                0.3: 'cyan',
                0.5: 'lime',
                0.7: 'yellow',
                1.0: 'red'
            }
        ).add_to(m)
        
        # Ajouter marqueurs pour points à fort potentiel
        top_opportunities = sorted(data_points, key=lambda x: x['score'], reverse=True)[:10]
        
        marker_cluster = MarkerCluster().add_to(m)
        
        for point in top_opportunities:
            folium.Marker(
                location=[point['lat'], point['lon']],
                popup=self._create_popup(point),
                icon=folium.Icon(color='red' if point['score'] > 80 else 'orange', icon='star')
            ).add_to(marker_cluster)
        
        # Ajouter légende
        colormap = LinearColormap(
            colors=['blue', 'cyan', 'lime', 'yellow', 'red'],
            vmin=0, vmax=100,
            caption='Score d\'opportunité (0-100)'
        )
        colormap.add_to(m)
        
        # Sauvegarder
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"heatmap_opportunities_{country}_{timestamp}.html"
        
        output_path = os.path.join('reports', output_file)
        os.makedirs('reports', exist_ok=True)
        m.save(output_path)
        
        print(f"   💾 Heatmap sauvegardée : {output_path}")
        
        # Générer statistiques
        stats = self._generate_statistics(data_points, country)
        self._save_statistics(stats, output_path.replace('.html', '_stats.json'))
        
        return output_path
    
    def generate_fertility_heatmap(self, country='tunisie', resolution=20, output_file=None):
        """Génère heatmap de fertilité des sols"""
        print(f"\n🌱 Génération heatmap fertilité : {country.upper()}")
        
        region = self.regions.get(country, self.regions['tunisie'])
        bounds = region['bounds']
        
        # Grille de points
        lats = np.linspace(bounds[0][0], bounds[1][0], resolution)
        lons = np.linspace(bounds[0][1], bounds[1][1], resolution)
        
        data_points = []
        
        for lat in lats:
            for lon in lons:
                fertility = self._simulate_fertility(lat, lon, country)
                data_points.append({
                    'lat': lat,
                    'lon': lon,
                    'fertility': fertility,
                    'category': 'Élevée' if fertility > 70 else 'Moyenne' if fertility > 40 else 'Faible'
                })
        
        print(f"   ✅ {len(data_points)} points analysés")
        
        # Créer carte
        m = folium.Map(
            location=region['center'],
            zoom_start=region['zoom'],
            tiles='OpenStreetMap'
        )
        
        # Heatmap fertilité
        heat_data = [[p['lat'], p['lon'], p['fertility']] for p in data_points]
        HeatMap(
            heat_data,
            min_opacity=0.4,
            radius=25,
            blur=20,
            gradient={
                0.0: 'red',
                0.4: 'orange',
                0.7: 'yellow',
                1.0: 'green'
            }
        ).add_to(m)
        
        # Légende
        colormap = LinearColormap(
            colors=['red', 'orange', 'yellow', 'green'],
            vmin=0, vmax=100,
            caption='Fertilité du sol (0-100)'
        )
        colormap.add_to(m)
        
        # Sauvegarder
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"heatmap_fertility_{country}_{timestamp}.html"
        
        output_path = os.path.join('reports', output_file)
        m.save(output_path)
        
        print(f"   💾 Heatmap fertilité sauvegardée : {output_path}")
        return output_path
    
    def generate_multi_layer_map(self, country='tunisie', output_file=None):
        """Génère carte multi-couches (opportunités + fertilité + risques)"""
        print(f"\n🗺️ Génération carte multi-couches : {country.upper()}")
        
        region = self.regions.get(country, self.regions['tunisie'])
        
        # Créer carte de base
        m = folium.Map(
            location=region['center'],
            zoom_start=region['zoom'],
            tiles='OpenStreetMap'
        )
        
        # Layer 1: Opportunités
        opportunity_layer = folium.FeatureGroup(name='🌟 Opportunités', show=True)
        opp_data = self._generate_layer_data(country, 'opportunity', resolution=15)
        HeatMap(
            opp_data,
            name='Opportunités',
            min_opacity=0.3,
            gradient={0.0: 'blue', 0.5: 'yellow', 1.0: 'red'}
        ).add_to(opportunity_layer)
        opportunity_layer.add_to(m)
        
        # Layer 2: Fertilité
        fertility_layer = folium.FeatureGroup(name='🌱 Fertilité', show=False)
        fert_data = self._generate_layer_data(country, 'fertility', resolution=15)
        HeatMap(
            fert_data,
            name='Fertilité',
            min_opacity=0.3,
            gradient={0.0: 'red', 0.5: 'yellow', 1.0: 'green'}
        ).add_to(fertility_layer)
        fertility_layer.add_to(m)
        
        # Layer 3: Risques
        risk_layer = folium.FeatureGroup(name='⚠️ Risques', show=False)
        risk_data = self._generate_layer_data(country, 'risk', resolution=15)
        HeatMap(
            risk_data,
            name='Risques',
            min_opacity=0.3,
            gradient={0.0: 'green', 0.5: 'orange', 1.0: 'darkred'}
        ).add_to(risk_layer)
        risk_layer.add_to(m)
        
        # Ajouter contrôle des couches
        folium.LayerControl(collapsed=False).add_to(m)
        
        # Ajouter titre
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h3>🛰️ Feralyx - Analyse Multi-Critères</h3>
        <p>Sélectionnez les couches à afficher :<br>
        🌟 Opportunités | 🌱 Fertilité | ⚠️ Risques</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Sauvegarder
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"heatmap_multilayer_{country}_{timestamp}.html"
        
        output_path = os.path.join('reports', output_file)
        m.save(output_path)
        
        print(f"   💾 Carte multi-couches sauvegardée : {output_path}")
        return output_path
    
    def _simulate_opportunity_score(self, lat, lon, country):
        """Simule score d'opportunité basé sur géolocalisation"""
        # Seed pour cohérence
        seed = int((lat * 1000 + lon * 1000) % 100000)
        np.random.seed(seed)
        
        # Score de base selon pays
        base_scores = {
            'tunisie': 65,
            'france': 75,
            'italie': 72,
            'espagne': 70
        }
        base = base_scores.get(country, 65)
        
        # Variation géographique
        score = base + np.random.normal(0, 15)
        
        # Zones premium (simulées)
        if country == 'tunisie' and 36.5 < lat < 37.0 and 9.8 < lon < 10.5:
            score += 15  # Nord fertile
        elif country == 'france' and 43.0 < lat < 44.0 and 3.5 < lon < 4.5:
            score += 20  # Région viticole
        
        return np.clip(score, 0, 100)
    
    def _simulate_fertility(self, lat, lon, country):
        """Simule fertilité du sol"""
        seed = int((lat * 1000 + lon * 1000) % 100000)
        np.random.seed(seed)
        
        # Fertilité selon latitude (plus fertile vers zones tempérées)
        if 35 < lat < 45:
            base_fertility = 70
        elif lat < 35:
            base_fertility = 55  # Zones arides
        else:
            base_fertility = 60  # Zones froides
        
        fertility = base_fertility + np.random.normal(0, 12)
        return np.clip(fertility, 20, 95)
    
    def _get_best_culture(self, score):
        """Détermine meilleure culture selon score"""
        if score > 80:
            return 'tomate'
        elif score > 60:
            return 'mais'
        elif score > 40:
            return 'ble'
        else:
            return 'olivier'
    
    def _create_popup(self, point):
        """Crée popup HTML pour marqueur"""
        return f"""
        <div style="width:200px">
        <h4>📊 Analyse Parcelle</h4>
        <b>Score opportunité:</b> {point['score']:.1f}/100<br>
        <b>Fertilité:</b> {point['fertilite']:.1f}/100<br>
        <b>Culture recommandée:</b> {point['culture'].upper()}<br>
        <br>
        <b>Coordonnées:</b><br>
        Lat: {point['lat']:.4f}<br>
        Lon: {point['lon']:.4f}
        </div>
        """
    
    def _generate_layer_data(self, country, layer_type, resolution=15):
        """Génère données pour une couche spécifique"""
        region = self.regions.get(country, self.regions['tunisie'])
        bounds = region['bounds']
        
        lats = np.linspace(bounds[0][0], bounds[1][0], resolution)
        lons = np.linspace(bounds[0][1], bounds[1][1], resolution)
        
        data = []
        for lat in lats:
            for lon in lons:
                if layer_type == 'opportunity':
                    value = self._simulate_opportunity_score(lat, lon, country)
                elif layer_type == 'fertility':
                    value = self._simulate_fertility(lat, lon, country)
                else:  # risk
                    value = 100 - self._simulate_opportunity_score(lat, lon, country)
                
                data.append([lat, lon, value])
        
        return data
    
    def _generate_statistics(self, data_points, country):
        """Génère statistiques de la zone analysée"""
        df = pd.DataFrame(data_points)
        
        stats = {
            'country': country,
            'total_points': len(data_points),
            'avg_score': float(df['score'].mean()),
            'max_score': float(df['score'].max()),
            'min_score': float(df['score'].min()),
            'high_opportunity_zones': int((df['score'] > 80).sum()),
            'medium_opportunity_zones': int(((df['score'] >= 60) & (df['score'] <= 80)).sum()),
            'low_opportunity_zones': int((df['score'] < 60).sum()),
            'top_culture': df['culture'].mode()[0] if len(df) > 0 else 'N/A',
            'analysis_date': datetime.now().isoformat()
        }
        
        return stats
    
    def _save_statistics(self, stats, filepath):
        """Sauvegarde statistiques en JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n   📊 STATISTIQUES :")
        print(f"      Score moyen : {stats['avg_score']:.1f}/100")
        print(f"      Zones haute opportunité : {stats['high_opportunity_zones']}")
        print(f"      Culture dominante : {stats['top_culture'].upper()}")


# Tests et démonstration
if __name__ == "__main__":
    print("="*70)
    print("🗺️ FERALYX V2.0 - GÉNÉRATEUR HEATMAPS INTERACTIVES")
    print("="*70)
    
    generator = HeatmapGenerator()
    
    # Test 1 : Heatmap opportunités Tunisie
    print("\n🎯 TEST 1 : Heatmap opportunités Tunisie")
    map1 = generator.generate_opportunity_heatmap('tunisie', resolution=20)
    
    # Test 2 : Heatmap fertilité France
    print("\n🎯 TEST 2 : Heatmap fertilité France")
    map2 = generator.generate_fertility_heatmap('france', resolution=15)
    
    # Test 3 : Carte multi-couches Espagne
    print("\n🎯 TEST 3 : Carte multi-couches Espagne")
    map3 = generator.generate_multi_layer_map('espagne')
    
    print("\n" + "="*70)
    print("✅ Génération terminée avec succès !")
    print("   📁 Ouvrez les fichiers HTML dans votre navigateur")
    print("="*70)