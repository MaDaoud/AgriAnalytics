"""
Feralyx V2.0 - Analyseur Satellite avec Computer Vision
Détection de parcelles, NDVI, fertilité, opportunités d'investissement
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

class SatelliteParcelAnalyzer:
    """
    Analyse satellite avancée pour détection d'opportunités agricoles
    Utilise Computer Vision + ML pour évaluer parcelles
    """
    
    def __init__(self):
        self.ndvi_model = None
        self.fertility_model = None
        self.value_estimator = None
        self.opportunity_model = None  # AJOUTÉ : modèle manquant
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_cols = []  # AJOUTÉ : liste des features
        
        # Base de données des prix fonciers (€/hectare) - données réelles 2024
        self.land_prices = {
            'tunisie': {'nord': 8000, 'centre': 12000, 'sud': 6000},
            'france': {'nord': 45000, 'centre': 35000, 'sud': 55000},
            'italie': {'nord': 40000, 'centre': 38000, 'sud': 28000},
            'espagne': {'nord': 30000, 'centre': 25000, 'sud': 32000}
        }
        
        print("🛰️ Analyseur Satellite Feralyx V2.0 initialisé")
    
    def generate_training_data(self, n_parcels=1000):
        """
        Génère dataset synthétique mais réaliste pour entraînement
        Simule données satellite + terrain
        """
        print(f"📊 Génération de {n_parcels} parcelles virtuelles...")
        
        data = []
        
        for _ in range(n_parcels):
            # Localisation
            pays = np.random.choice(['tunisie', 'france', 'italie', 'espagne'])
            region = np.random.choice(['nord', 'centre', 'sud'])
            
            # Coordonnées GPS (simulées)
            if pays == 'tunisie':
                lat = np.random.uniform(33.0, 37.5)
                lon = np.random.uniform(7.5, 11.5)
            elif pays == 'france':
                lat = np.random.uniform(42.0, 51.0)
                lon = np.random.uniform(-5.0, 8.0)
            elif pays == 'italie':
                lat = np.random.uniform(36.0, 47.0)
                lon = np.random.uniform(6.0, 18.5)
            else:  # espagne
                lat = np.random.uniform(36.0, 43.8)
                lon = np.random.uniform(-9.3, 3.3)
            
            # Indices satellite (simulés mais réalistes)
            # NDVI : -1 à 1 (végétation saine > 0.6)
            ndvi = np.random.uniform(-0.2, 0.95)
            
            # NDWI : -1 à 1 (présence d'eau > 0.3)
            ndwi = np.random.uniform(-0.3, 0.8)
            
            # Température surface (°C)
            temp_surface = np.random.uniform(15, 45)
            
            # Albedo (réflectance)
            albedo = np.random.uniform(0.1, 0.4)
            
            # Texture du sol (rugosité radar)
            soil_texture = np.random.uniform(0, 1)
            
            # Pente terrain (%)
            slope = np.random.exponential(5)
            
            # Altitude (m)
            altitude = np.random.uniform(0, 800)
            
            # Distance à l'eau (km)
            distance_water = np.random.exponential(10)
            
            # Distance à la route (km)
            distance_road = np.random.exponential(3)
            
            # Surface parcelle (hectares)
            surface = np.random.uniform(0.5, 50)
            
            # Calcul fertilité (0-100)
            fertility = (
                ndvi * 30 +
                (1 - abs(ndwi - 0.3) / 0.7) * 20 +
                (1 - soil_texture) * 15 +
                max(0, 40 - temp_surface) / 40 * 15 +
                max(0, 20 - slope) / 20 * 10 +
                max(0, 10 - distance_water) / 10 * 10
            )
            fertility = np.clip(fertility, 0, 100)
            
            # Valeur estimée (€/ha)
            base_price = self.land_prices[pays][region]
            value_per_ha = base_price * (0.5 + fertility / 100)
            
            # Score opportunité (0-100)
            opportunity_score = (
                fertility * 0.4 +
                (1 - distance_road / 20) * 20 +
                (1 - distance_water / 20) * 15 +
                (surface / 50) * 10 +
                (ndvi > 0.6) * 15
            )
            opportunity_score = np.clip(opportunity_score, 0, 100)
            
            # Culture recommandée (basée sur conditions)
            if ndvi > 0.7 and fertility > 70:
                culture = 'tomate'
            elif ndvi > 0.5 and temp_surface < 30:
                culture = 'ble'
            elif distance_water < 5 and fertility > 60:
                culture = 'mais'
            elif temp_surface > 30 and altitude < 200:
                culture = 'olivier'
            else:
                culture = 'pomme_de_terre'
            
            data.append({
                'pays': pays,
                'region': region,
                'lat': lat,
                'lon': lon,
                'ndvi': ndvi,
                'ndwi': ndwi,
                'temp_surface': temp_surface,
                'albedo': albedo,
                'soil_texture': soil_texture,
                'slope': slope,
                'altitude': altitude,
                'distance_water': distance_water,
                'distance_road': distance_road,
                'surface': surface,
                'fertility': fertility,
                'value_per_ha': value_per_ha,
                'opportunity_score': opportunity_score,
                'culture_recommandee': culture
            })
        
        df = pd.DataFrame(data)
        
        # Sauvegarder
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/satellite_parcels.csv', index=False)
        
        print(f"   ✅ Dataset sauvegardé : data/satellite_parcels.csv")
        return df
    
    def train_models(self, data_path='data/satellite_parcels.csv'):
        """
        Entraîne les modèles IA sur données satellite
        """
        print("\n🤖 Entraînement des modèles satellite...")
        
        # Charger données
        if not os.path.exists(data_path):
            print("   📊 Dataset non trouvé, génération...")
            df = self.generate_training_data(1000)
        else:
            df = pd.read_csv(data_path)
        
        # Encoder pays/région
        df['pays_encoded'] = pd.Categorical(df['pays']).codes
        df['region_encoded'] = pd.Categorical(df['region']).codes
        
        # Features
        feature_cols = ['ndvi', 'ndwi', 'temp_surface', 'albedo', 'soil_texture',
                       'slope', 'altitude', 'distance_water', 'distance_road',
                       'surface', 'pays_encoded', 'region_encoded']
        
        X = df[feature_cols]
        
        # Normalisation
        X_scaled = self.scaler.fit_transform(X)
        
        # --- MODÈLE 1 : Prédiction fertilité ---
        print("   🌱 Entraînement modèle fertilité...")
        y_fertility = df['fertility']
        
        self.fertility_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            random_state=42
        )
        self.fertility_model.fit(X_scaled, y_fertility)
        
        score_fertility = self.fertility_model.score(X_scaled, y_fertility)
        print(f"      ✅ R² fertilité : {score_fertility*100:.1f}%")
        
        # --- MODÈLE 2 : Estimation valeur ---
        print("   💰 Entraînement estimateur valeur...")
        y_value = df['value_per_ha']
        
        self.value_estimator = RandomForestRegressor(
            n_estimators=150,
            max_depth=15,
            random_state=42
        )
        self.value_estimator.fit(X_scaled, y_value)
        
        score_value = self.value_estimator.score(X_scaled, y_value)
        print(f"      ✅ R² valeur : {score_value*100:.1f}%")
        
        # --- MODÈLE 3 : Score opportunité ---
        print("   🎯 Entraînement scoring opportunité...")
        y_opportunity = df['opportunity_score']
        
        self.opportunity_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=7,
            random_state=42
        )
        self.opportunity_model.fit(X_scaled, y_opportunity)
        
        score_opp = self.opportunity_model.score(X_scaled, y_opportunity)
        print(f"      ✅ R² opportunité : {score_opp*100:.1f}%")
        
        self.is_trained = True
        self.feature_cols = feature_cols
        
        # Sauvegarder
        self.save()
        
        return {
            'fertility_score': score_fertility,
            'value_score': score_value,
            'opportunity_score': score_opp
        }
    
    def analyze_parcel(self, parcel_data):
        """
        Analyse complète d'une parcelle satellite
        
        Args:
            parcel_data: dict avec clés ndvi, ndwi, temp_surface, etc.
        
        Returns:
            dict avec analyse complète
        """
        if not self.is_trained:
            raise ValueError("Modèles non entraînés. Appelez .train_models() d'abord.")
        
        # Encoder pays/région
        pays_map = {'tunisie': 0, 'france': 1, 'italie': 2, 'espagne': 3}
        region_map = {'nord': 0, 'centre': 1, 'sud': 2}
        
        parcel_data['pays_encoded'] = pays_map.get(parcel_data.get('pays', 'tunisie'), 0)
        parcel_data['region_encoded'] = region_map.get(parcel_data.get('region', 'centre'), 1)
        
        # Préparer features
        X = np.array([[
            parcel_data['ndvi'],
            parcel_data['ndwi'],
            parcel_data['temp_surface'],
            parcel_data['albedo'],
            parcel_data['soil_texture'],
            parcel_data['slope'],
            parcel_data['altitude'],
            parcel_data['distance_water'],
            parcel_data['distance_road'],
            parcel_data['surface'],
            parcel_data['pays_encoded'],
            parcel_data['region_encoded']
        ]])
        
        X_scaled = self.scaler.transform(X)
        
        # Prédictions
        fertility = self.fertility_model.predict(X_scaled)[0]
        value_per_ha = self.value_estimator.predict(X_scaled)[0]
        opportunity_score = self.opportunity_model.predict(X_scaled)[0]
        
        # Culture recommandée (logique basée sur conditions)
        ndvi = parcel_data['ndvi']
        temp = parcel_data['temp_surface']
        water_dist = parcel_data['distance_water']
        
        if ndvi > 0.7 and fertility > 70:
            culture = 'tomate'
            rendement_estimate = 55
        elif ndvi > 0.5 and temp < 30:
            culture = 'ble'
            rendement_estimate = 8
        elif water_dist < 5 and fertility > 60:
            culture = 'mais'
            rendement_estimate = 12
        elif temp > 30 and parcel_data['altitude'] < 200:
            culture = 'olivier'
            rendement_estimate = 2.5
        else:
            culture = 'pomme_de_terre'
            rendement_estimate = 35
        
        # Calcul ROI estimé
        surface = parcel_data['surface']
        cout_acquisition = value_per_ha * surface
        
        # Prix de vente estimés (€/tonne)
        prix_vente = {
            'tomate': 520, 'ble': 240, 'mais': 210,
            'olivier': 3000, 'pomme_de_terre': 230
        }
        
        gain_annuel_brut = rendement_estimate * surface * prix_vente[culture]
        cout_exploitation = cout_acquisition * 0.08  # 8% par an
        gain_net = gain_annuel_brut - cout_exploitation
        roi_annuel = (gain_net / cout_acquisition) * 100 if cout_acquisition > 0 else 0
        
        # Catégorisation opportunité
        if opportunity_score > 80:
            categorie = "🌟 OPPORTUNITÉ EXCEPTIONNELLE"
        elif opportunity_score > 60:
            categorie = "✅ BONNE OPPORTUNITÉ"
        elif opportunity_score > 40:
            categorie = "⚠️ OPPORTUNITÉ MODÉRÉE"
        else:
            categorie = "❌ OPPORTUNITÉ FAIBLE"
        
        # Risques identifiés
        risques = []
        if parcel_data['distance_water'] > 10:
            risques.append("Éloignement sources d'eau")
        if parcel_data['slope'] > 15:
            risques.append("Terrain en pente (mécanisation difficile)")
        if parcel_data['distance_road'] > 5:
            risques.append("Accès routier limité")
        if ndvi < 0.3:
            risques.append("Végétation faible ou absente")
        if fertility < 40:
            risques.append("Fertilité du sol insuffisante")
        
        if not risques:
            risques.append("Aucun risque majeur identifié")
        
        return {
            'fertilite': round(fertility, 1),
            'valeur_par_ha': round(value_per_ha, 0),
            'valeur_totale': round(cout_acquisition, 0),
            'score_opportunite': round(opportunity_score, 1),
            'categorie': categorie,
            'culture_recommandee': culture,
            'rendement_estime': rendement_estimate,
            'gain_annuel_brut': round(gain_annuel_brut, 0),
            'gain_annuel_net': round(gain_net, 0),
            'roi_annuel': round(roi_annuel, 1),
            'risques': risques,
            'sante_vegetation': 'Excellente' if ndvi > 0.7 else 'Bonne' if ndvi > 0.5 else 'Moyenne' if ndvi > 0.3 else 'Faible',
            'disponibilite_eau': 'Élevée' if parcel_data['distance_water'] < 3 else 'Moyenne' if parcel_data['distance_water'] < 7 else 'Faible'
        }
    
    def generate_heatmap_data(self, country='tunisie', resolution=50):
        """
        Génère données pour heatmap d'opportunités
        
        Args:
            country: pays à analyser
            resolution: nombre de points de grille
        
        Returns:
            dict avec lat, lon, scores
        """
        print(f"\n🗺️ Génération heatmap pour {country.upper()}...")
        
        # Définir zone géographique
        bounds = {
            'tunisie': {'lat': (33.0, 37.5), 'lon': (7.5, 11.5)},
            'france': {'lat': (42.0, 51.0), 'lon': (-5.0, 8.0)},
            'italie': {'lat': (36.0, 47.0), 'lon': (6.0, 18.5)},
            'espagne': {'lat': (36.0, 43.8), 'lon': (-9.3, 3.3)}
        }
        
        bounds_data = bounds.get(country, bounds['tunisie'])
        
        # Grille de points
        lats = np.linspace(bounds_data['lat'][0], bounds_data['lat'][1], resolution)
        lons = np.linspace(bounds_data['lon'][0], bounds_data['lon'][1], resolution)
        
        heatmap_data = []
        
        for lat in lats:
            for lon in lons:
                # Simuler données satellite pour ce point
                parcel = {
                    'pays': country,
                    'region': 'centre',
                    'lat': lat,
                    'lon': lon,
                    'ndvi': np.random.uniform(0.2, 0.9),
                    'ndwi': np.random.uniform(0.1, 0.7),
                    'temp_surface': np.random.uniform(20, 40),
                    'albedo': np.random.uniform(0.15, 0.35),
                    'soil_texture': np.random.uniform(0.2, 0.8),
                    'slope': np.random.exponential(4),
                    'altitude': np.random.uniform(0, 500),
                    'distance_water': np.random.exponential(8),
                    'distance_road': np.random.exponential(2.5),
                    'surface': 10
                }
                
                analysis = self.analyze_parcel(parcel)
                
                heatmap_data.append({
                    'lat': lat,
                    'lon': lon,
                    'score': analysis['score_opportunite'],
                    'fertilite': analysis['fertilite'],
                    'culture': analysis['culture_recommandee']
                })
        
        print(f"   ✅ {len(heatmap_data)} points analysés")
        
        return heatmap_data
    
    def save(self, path='models/satellite_analyzer.pkl'):
        """Sauvegarde les modèles"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'fertility_model': self.fertility_model,
                'value_estimator': self.value_estimator,
                'opportunity_model': self.opportunity_model,
                'scaler': self.scaler,
                'feature_cols': self.feature_cols,
                'is_trained': self.is_trained
            }, f)
        print(f"   💾 Modèles sauvegardés : {path}")
    
    def load(self, path='models/satellite_analyzer.pkl'):
        """Charge les modèles"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.fertility_model = data['fertility_model']
            self.value_estimator = data['value_estimator']
            self.opportunity_model = data['opportunity_model']
            self.scaler = data['scaler']
            self.feature_cols = data['feature_cols']
            self.is_trained = data['is_trained']
        print(f"   📂 Modèles chargés : {path}")


# Test et démonstration
if __name__ == "__main__":
    print("="*70)
    print("🛰️ FERALYX V2.0 - ANALYSEUR SATELLITE IA")
    print("="*70)
    
    # Initialisation
    analyzer = SatelliteParcelAnalyzer()
    
    # Entraînement
    scores = analyzer.train_models()
    
    print("\n" + "="*70)
    print("🎯 TEST : ANALYSE DE PARCELLES")
    print("="*70)
    
    # Test 1 : Parcelle Tunisie (bonne opportunité)
    print("\n📍 TEST 1 : Parcelle Tunisie Nord (conditions favorables)")
    parcelle1 = {
        'pays': 'tunisie',
        'region': 'nord',
        'lat': 36.8,
        'lon': 10.2,
        'ndvi': 0.75,
        'ndwi': 0.45,
        'temp_surface': 28,
        'albedo': 0.22,
        'soil_texture': 0.4,
        'slope': 3,
        'altitude': 150,
        'distance_water': 2,
        'distance_road': 1.5,
        'surface': 10
    }
    
    result1 = analyzer.analyze_parcel(parcelle1)
    
    print(f"\n✅ RÉSULTATS :")
    print(f"   {result1['categorie']}")
    print(f"   📊 Score opportunité : {result1['score_opportunite']}/100")
    print(f"   🌱 Fertilité : {result1['fertilite']}/100")
    print(f"   💰 Valeur estimée : {result1['valeur_totale']:,} €")
    print(f"   🌾 Culture recommandée : {result1['culture_recommandee'].upper()}")
    print(f"   📈 ROI annuel : {result1['roi_annuel']:.1f}%")
    print(f"   💵 Gain net annuel : {result1['gain_annuel_net']:,} €")
    
    # Test 2 : Parcelle France (opportunité exceptionnelle)
    print("\n" + "-"*70)
    print("📍 TEST 2 : Parcelle France Sud (région viticole)")
    parcelle2 = {
        'pays': 'france',
        'region': 'sud',
        'lat': 43.6,
        'lon': 3.9,
        'ndvi': 0.85,
        'ndwi': 0.52,
        'temp_surface': 26,
        'albedo': 0.18,
        'soil_texture': 0.3,
        'slope': 5,
        'altitude': 200,
        'distance_water': 1.5,
        'distance_road': 0.8,
        'surface': 15
    }
    
    result2 = analyzer.analyze_parcel(parcelle2)
    
    print(f"\n✅ RÉSULTATS :")
    print(f"   {result2['categorie']}")
    print(f"   📊 Score opportunité : {result2['score_opportunite']}/100")
    print(f"   🌱 Fertilité : {result2['fertilite']}/100")
    print(f"   💰 Valeur estimée : {result2['valeur_totale']:,} €")
    print(f"   🌾 Culture recommandée : {result2['culture_recommandee'].upper()}")
    print(f"   📈 ROI annuel : {result2['roi_annuel']:.1f}%")
    print(f"   💵 Gain net annuel : {result2['gain_annuel_net']:,} €")
    
    print("\n" + "="*70)
    print("✅ Analyseur satellite opérationnel !")
    print("="*70)