"""
Feralyx V2.0 - Analyseur Satellite avec Sentinel Hub API
Données réelles Sentinel-2 pour analyse agricole avancée
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import pickle

# Pour Sentinel Hub (si installé)
try:
    from sentinelhub import SHConfig, BBox, CRS, MimeType, SentinelHubRequest, DataCollection, bbox_to_dimensions
    SENTINEL_AVAILABLE = True
except ImportError:
    SENTINEL_AVAILABLE = False
    print("⚠️ sentinelhub non installé - Mode simulation activé")

from satellite_analyzer import SatelliteParcelAnalyzer

class SentinelParcelAnalyzer:
    """
    Analyse parcelles avec vraies données Sentinel-2
    + Fallback mode simulation si API non disponible
    """
    
    def __init__(self, client_id=None, client_secret=None):
        """
        Args:
            client_id: ID client Sentinel Hub (optionnel)
            client_secret: Secret client Sentinel Hub (optionnel)
        """
        self.use_sentinel = SENTINEL_AVAILABLE and client_id and client_secret
        
        if self.use_sentinel:
            self.config = SHConfig()
            self.config.sh_client_id = client_id
            self.config.sh_client_secret = client_secret
            print("🛰️ Mode Sentinel Hub RÉEL activé")
        else:
            print("🛰️ Mode SIMULATION activé (données synthétiques réalistes)")
        
        # Charger analyseur IA
        self.ai_analyzer = SatelliteParcelAnalyzer()
        if os.path.exists('models/satellite_analyzer.pkl'):
            self.ai_analyzer.load()
        else:
            print("📊 Entraînement modèles IA...")
            self.ai_analyzer.train_models()
    
    def get_sentinel_data(self, bbox, date_from, date_to, resolution=10):
        """
        Récupère données Sentinel-2 réelles
        
        Args:
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
            date_from: Date début (datetime)
            date_to: Date fin (datetime)
            resolution: Résolution en mètres (10, 20, 60)
        
        Returns:
            dict avec bandes spectrales
        """
        if not self.use_sentinel:
            return self._simulate_sentinel_data(bbox)
        
        try:
            # Créer bbox Sentinel Hub
            bbox_sh = BBox(bbox=bbox, crs=CRS.WGS84)
            size = bbox_to_dimensions(bbox_sh, resolution=resolution)
            
            # Script pour récupérer bandes
            evalscript = """
            //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["B02", "B03", "B04", "B08", "B11", "B12"],
                        units: "DN"
                    }],
                    output: {
                        bands: 6,
                        sampleType: "INT16"
                    }
                };
            }
            
            function evaluatePixel(sample) {
                return [sample.B02, sample.B03, sample.B04, 
                        sample.B08, sample.B11, sample.B12];
            }
            """
            
            # Requête
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(date_from, date_to),
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response('default', MimeType.TIFF)
                ],
                bbox=bbox_sh,
                size=size,
                config=self.config
            )
            
            # Récupérer données
            data = request.get_data()[0]
            
            # Extraire bandes
            blue = data[:, :, 0] / 10000.0
            green = data[:, :, 1] / 10000.0
            red = data[:, :, 2] / 10000.0
            nir = data[:, :, 3] / 10000.0
            swir1 = data[:, :, 4] / 10000.0
            swir2 = data[:, :, 5] / 10000.0
            
            # Calculer indices
            ndvi = (nir - red) / (nir + red + 1e-10)
            ndwi = (green - nir) / (green + nir + 1e-10)
            ndmi = (nir - swir1) / (nir + swir1 + 1e-10)  # Moisture index
            
            return {
                'ndvi': np.nanmean(ndvi),
                'ndwi': np.nanmean(ndwi),
                'ndmi': np.nanmean(ndmi),
                'blue': np.nanmean(blue),
                'green': np.nanmean(green),
                'red': np.nanmean(red),
                'nir': np.nanmean(nir),
                'swir1': np.nanmean(swir1),
                'swir2': np.nanmean(swir2),
                'source': 'sentinel-2'
            }
            
        except Exception as e:
            print(f"⚠️ Erreur Sentinel Hub : {e}")
            print("   Utilisation données simulées...")
            return self._simulate_sentinel_data(bbox)
    
    def _simulate_sentinel_data(self, bbox):
        """Simule données satellite réalistes"""
        # Générer valeurs cohérentes basées sur localisation
        lat_center = (bbox[1] + bbox[3]) / 2
        lon_center = (bbox[0] + bbox[2]) / 2
        
        # Seed basé sur position pour cohérence
        seed = int((lat_center * 1000 + lon_center * 1000) % 1000000)
        np.random.seed(seed)
        
        # NDVI basé sur latitude (plus végétation vers équateur)
        ndvi_base = 0.7 - abs(lat_center - 35) * 0.02
        ndvi = np.clip(ndvi_base + np.random.normal(0, 0.1), -0.2, 0.95)
        
        # NDWI (eau) - plus élevé près côtes
        ndwi = np.clip(np.random.uniform(0.2, 0.6), -0.3, 0.8)
        
        # NDMI (humidité)
        ndmi = np.clip(ndvi * 0.8 + np.random.normal(0, 0.1), -0.2, 0.8)
        
        return {
            'ndvi': ndvi,
            'ndwi': ndwi,
            'ndmi': ndmi,
            'blue': np.random.uniform(0.05, 0.15),
            'green': np.random.uniform(0.08, 0.18),
            'red': np.random.uniform(0.06, 0.16),
            'nir': np.random.uniform(0.25, 0.45),
            'swir1': np.random.uniform(0.15, 0.30),
            'swir2': np.random.uniform(0.10, 0.25),
            'source': 'simulation'
        }
    
    def analyze_parcel_complete(self, lat, lon, size_km=1.0, pays='tunisie', region='centre'):
        """
        Analyse complète d'une parcelle avec Sentinel + IA
        
        Args:
            lat: Latitude centre parcelle
            lon: Longitude centre parcelle
            size_km: Taille parcelle en km (pour bbox)
            pays: Pays
            region: Région
        
        Returns:
            dict avec analyse complète
        """
        print(f"\n🛰️ Analyse parcelle : {lat:.4f}, {lon:.4f}")
        
        # Créer bounding box
        delta = size_km / 111.0  # 1 degré ≈ 111km
        bbox = [
            lon - delta/2,  # min_lon
            lat - delta/2,  # min_lat
            lon + delta/2,  # max_lon
            lat + delta/2   # max_lat
        ]
        
        # Récupérer données satellite (derniers 30 jours)
        date_to = datetime.now()
        date_from = date_to - timedelta(days=30)
        
        print("   📡 Récupération données satellite...")
        sentinel_data = self.get_sentinel_data(bbox, date_from, date_to)
        
        print(f"   ✅ Données reçues (source: {sentinel_data['source']})")
        print(f"      NDVI: {sentinel_data['ndvi']:.3f}")
        print(f"      NDWI: {sentinel_data['ndwi']:.3f}")
        
        # Enrichir données pour analyseur IA
        surface_ha = (size_km * size_km) * 100  # km² → ha
        
        parcel_data = {
            'pays': pays,
            'region': region,
            'lat': lat,
            'lon': lon,
            'ndvi': sentinel_data['ndvi'],
            'ndwi': sentinel_data['ndwi'],
            'temp_surface': self._estimate_temperature(lat, sentinel_data),
            'albedo': (sentinel_data['red'] + sentinel_data['green'] + sentinel_data['blue']) / 3,
            'soil_texture': 1.0 - sentinel_data['ndmi'],  # Texture basée sur humidité
            'slope': np.random.exponential(5),  # Simulé (nécessiterait DEM)
            'altitude': self._estimate_altitude(lat, lon),
            'distance_water': self._estimate_water_distance(sentinel_data['ndwi']),
            'distance_road': np.random.exponential(3),  # Simulé
            'surface': surface_ha
        }
        
        # Analyse IA
        print("   🤖 Analyse IA en cours...")
        ai_result = self.ai_analyzer.analyze_parcel(parcel_data)
        
        # Combiner résultats
        result = {
            **ai_result,
            'sentinel_data': sentinel_data,
            'coordinates': {'lat': lat, 'lon': lon},
            'bbox': bbox,
            'analyzed_date': datetime.now().isoformat()
        }
        
        # Affichage résumé
        self._print_analysis_summary(result)
        
        return result
    
    def _estimate_temperature(self, lat, sentinel_data):
        """Estime température surface"""
        # Température basée sur latitude et saison
        month = datetime.now().month
        
        # Base température selon latitude
        if lat < 35:
            base_temp = 32
        elif lat < 42:
            base_temp = 26
        else:
            base_temp = 20
        
        # Ajustement saison
        if month in [6, 7, 8]:  # Été
            temp = base_temp + 5
        elif month in [12, 1, 2]:  # Hiver
            temp = base_temp - 8
        else:  # Printemps/Automne
            temp = base_temp
        
        # Ajustement selon végétation (NDVI élevé = température réduite)
        temp -= sentinel_data['ndvi'] * 5
        
        return np.clip(temp, 10, 45)
    
    def _estimate_altitude(self, lat, lon):
        """Estime altitude (simulée)"""
        # Altitude basée sur position géographique
        if lat > 45:  # Zones montagneuses Europe
            return np.random.uniform(200, 800)
        elif lat < 35:  # Zones désertiques
            return np.random.uniform(50, 400)
        else:
            return np.random.uniform(0, 600)
    
    def _estimate_water_distance(self, ndwi):
        """Estime distance à l'eau basé sur NDWI"""
        # NDWI élevé = eau proche
        if ndwi > 0.5:
            return np.random.uniform(0.5, 2)
        elif ndwi > 0.3:
            return np.random.uniform(2, 5)
        elif ndwi > 0.1:
            return np.random.uniform(5, 10)
        else:
            return np.random.uniform(10, 20)
    
    def _print_analysis_summary(self, result):
        """Affiche résumé de l'analyse"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ ANALYSE PARCELLE")
        print("="*60)
        print(f"\n{result['categorie']}")
        print(f"📊 Score opportunité : {result['score_opportunite']:.1f}/100")
        print(f"🌱 Fertilité : {result['fertilite']:.1f}/100")
        print(f"🌿 Santé végétation : {result['sante_vegetation']}")
        print(f"💧 Disponibilité eau : {result['disponibilite_eau']}")
        print(f"\n💰 ESTIMATION FINANCIÈRE :")
        print(f"   Valeur parcelle : {result['valeur_totale']:,.0f}€")
        print(f"   Valeur/hectare : {result['valeur_par_ha']:,.0f}€/ha")
        print(f"\n🌾 RECOMMANDATION :")
        print(f"   Culture : {result['culture_recommandee'].upper()}")
        print(f"   Rendement estimé : {result['rendement_estime']} t/ha")
        print(f"   Gain annuel net : {result['gain_annuel_net']:,.0f}€")
        print(f"   ROI annuel : {result['roi_annuel']:.1f}%")
        
        if result['risques'] and result['risques'][0] != 'Aucun risque majeur identifié':
            print(f"\n⚠️ RISQUES IDENTIFIÉS :")
            for risque in result['risques']:
                print(f"   • {risque}")
        
        print("="*60)
    
    def save_analysis(self, result, filename=None):
        """Sauvegarde analyse en JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{result['coordinates']['lat']:.4f}_{result['coordinates']['lon']:.4f}_{timestamp}.json"
        
        filepath = os.path.join('reports', filename)
        os.makedirs('reports', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Analyse sauvegardée : {filepath}")
        return filepath


# Tests et démonstrations
if __name__ == "__main__":
    print("="*70)
    print("🛰️ FERALYX V2.0 - ANALYSEUR SATELLITE SENTINEL")
    print("="*70)
    
    # Initialisation (sans clés API = mode simulation)
    analyzer = SentinelParcelAnalyzer()
    
    # Pour utiliser vraies données Sentinel, décommentez :
    # analyzer = SentinelParcelAnalyzer(
    #     client_id="votre_client_id",
    #     client_secret="votre_client_secret"
    # )
    
    print("\n🎯 DÉMONSTRATION : Analyse de 3 parcelles")
    
    # Test 1 : Parcelle Tunisie (bonne opportunité)
    print("\n" + "="*70)
    print("TEST 1 : Parcelle Tunisie Nord (région agricole)")
    print("="*70)
    
    result1 = analyzer.analyze_parcel_complete(
        lat=36.8,
        lon=10.2,
        size_km=0.5,
        pays='tunisie',
        region='nord'
    )
    analyzer.save_analysis(result1)
    
    # Test 2 : Parcelle France (région viticole)
    print("\n" + "="*70)
    print("TEST 2 : Parcelle France Sud (région viticole)")
    print("="*70)
    
    result2 = analyzer.analyze_parcel_complete(
        lat=43.6,
        lon=3.9,
        size_km=0.3,
        pays='france',
        region='sud'
    )
    analyzer.save_analysis(result2)
    
    # Test 3 : Parcelle Espagne (région aride)
    print("\n" + "="*70)
    print("TEST 3 : Parcelle Espagne Sud (zone aride)")
    print("="*70)
    
    result3 = analyzer.analyze_parcel_complete(
        lat=37.2,
        lon=-2.5,
        size_km=0.8,
        pays='espagne',
        region='sud'
    )
    analyzer.save_analysis(result3)
    
    print("\n" + "="*70)
    print("✅ Démonstration terminée avec succès !")
    print("   📁 Analyses sauvegardées dans reports/")
    print("="*70)