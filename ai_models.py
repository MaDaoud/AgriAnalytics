import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

class IrrigationModel:
    """Modèle IA pour prédire l'irrigation"""
    
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.regressor = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
        self.label_encoder = LabelEncoder()
        self.is_trained = False
    
    def train(self, data_path='data/irrigation_dataset.csv'):
        """Entraîne le modèle sur le dataset"""
        print("🌊 Entraînement du modèle d'irrigation...")
        
        # Chargement des données
        df = pd.read_csv(data_path)
        
        # Encodage du type de sol
        df['type_sol_encoded'] = self.label_encoder.fit_transform(df['type_sol'])
        
        # Features
        X = df[['humidite', 'temperature', 'type_sol_encoded', 'ph', 
                'ensoleillement', 'age_culture', 'precipitation_prevue']]
        
        # Target pour classification (irriguer ou non)
        y_classifier = df['irriguer']
        
        # Target pour régression (débit et durée)
        y_regressor = df[['debit_eau', 'duree_minutes']]
        
        # Entraînement du classifier
        X_train, X_test, y_train, y_test = train_test_split(X, y_classifier, test_size=0.2, random_state=42)
        self.classifier.fit(X_train, y_train)
        score_clf = self.classifier.score(X_test, y_test)
        
        # Entraînement du regressor (seulement sur les cas où irrigation = 1)
        df_irrigate = df[df['irriguer'] == 1]
        X_irrigate = df_irrigate[['humidite', 'temperature', 'type_sol_encoded', 'ph', 
                                   'ensoleillement', 'age_culture', 'precipitation_prevue']]
        y_irrigate = df_irrigate[['debit_eau', 'duree_minutes']]
        
        if len(X_irrigate) > 0:
            X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
                X_irrigate, y_irrigate, test_size=0.2, random_state=42
            )
            self.regressor.fit(X_train_reg, y_train_reg)
            score_reg = self.regressor.score(X_test_reg, y_test_reg)
        else:
            score_reg = 0
        
        self.is_trained = True
        
        print(f"   ✅ Précision classification: {score_clf*100:.1f}%")
        print(f"   ✅ Précision régression: {score_reg*100:.1f}%")
        
        return score_clf, score_reg
    
    def predict(self, input_data):
        """Prédit l'irrigation pour de nouvelles données"""
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné. Appelez d'abord .train()")
        
        # Encodage du type de sol
        type_sol_map = {'argileux': 0, 'sableux': 1, 'limoneux': 2}
        input_data['type_sol_encoded'] = type_sol_map.get(input_data['type_sol'], 0)
        
        # Préparer les features
        X = np.array([[
            input_data['humidite'],
            input_data['temperature'],
            input_data['type_sol_encoded'],
            input_data['ph'],
            input_data['ensoleillement'],
            input_data['age_culture'],
            input_data['precipitation_prevue']
        ]])
        
        # Prédiction irrigation (0 ou 1)
        irriguer = self.classifier.predict(X)[0]
        
        # Si irrigation nécessaire, prédire débit et durée
        if irriguer == 1:
            predictions = self.regressor.predict(X)[0]
            debit_eau = max(0.5, predictions[0])
            duree_minutes = max(10, predictions[1])
        else:
            debit_eau = 0
            duree_minutes = 0
        
        return {
            'irriguer': int(irriguer),
            'debit_eau': round(debit_eau, 2),
            'duree_minutes': round(duree_minutes, 1)
        }
    
    def save(self, path='models/irrigation_model.pkl'):
        """Sauvegarde le modèle"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'classifier': self.classifier,
                'regressor': self.regressor,
                'label_encoder': self.label_encoder,
                'is_trained': self.is_trained
            }, f)
        print(f"   💾 Modèle sauvegardé: {path}")
    
    def load(self, path='models/irrigation_model.pkl'):
        """Charge le modèle"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.classifier = data['classifier']
            self.regressor = data['regressor']
            self.label_encoder = data['label_encoder']
            self.is_trained = data['is_trained']
        print(f"   📂 Modèle chargé: {path}")


class DiseaseDetectionModel:
    """Modèle IA pour détecter les maladies"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def train(self, data_path='data/disease_dataset.csv'):
        """Entraîne le modèle sur le dataset"""
        print("🦠 Entraînement du modèle de détection de maladies...")
        
        # Chargement des données
        df = pd.read_csv(data_path)
        
        # Features
        X = df[['temperature_feuille', 'humidite_feuille', 'couleur', 
                'stress_hydrique', 'ph_sol', 'croissance_pct']]
        
        # Target
        y = df['maladie']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entraînement
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        
        self.is_trained = True
        
        print(f"   ✅ Précision: {score*100:.1f}%")
        
        return score
    
    def predict(self, input_data):
        """Prédit la maladie pour de nouvelles données"""
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné. Appelez d'abord .train()")
        
        # Préparer les features
        X = np.array([[
            input_data['temperature_feuille'],
            input_data['humidite_feuille'],
            input_data['couleur'],
            input_data['stress_hydrique'],
            input_data['ph_sol'],
            input_data['croissance_pct']
        ]])
        
        # Prédiction
        maladie = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Confiance
        confidence = max(probabilities) * 100
        
        return {
            'maladie': maladie,
            'confiance': round(confidence, 1)
        }
    
    def save(self, path='models/disease_model.pkl'):
        """Sauvegarde le modèle"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'is_trained': self.is_trained
            }, f)
        print(f"   💾 Modèle sauvegardé: {path}")
    
    def load(self, path='models/disease_model.pkl'):
        """Charge le modèle"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.is_trained = data['is_trained']
        print(f"   📂 Modèle chargé: {path}")


class ExportRecommendationModel:
    """Modèle pour recommander cultures et exports"""
    
    def __init__(self):
        self.culture_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.pays_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder_sol = LabelEncoder()
        self.label_encoder_region = LabelEncoder()
        self.label_encoder_culture = LabelEncoder()
        self.is_trained = False
    
    def train(self, data_path='data/export_dataset.csv'):
        """Entraîne le modèle sur le dataset"""
        print("🌍 Entraînement du modèle de recommandation d'export...")
        
        # Chargement des données
        df = pd.read_csv(data_path)
        
        # Encodage
        df['type_sol_encoded'] = self.label_encoder_sol.fit_transform(df['type_sol'])
        df['region_encoded'] = self.label_encoder_region.fit_transform(df['region'])
        df['culture_encoded'] = self.label_encoder_culture.fit_transform(df['culture'])
        
        # Features pour culture
        X_culture = df[['type_sol_encoded', 'region_encoded', 'budget', 'surface']]
        y_culture = df['culture']
        
        # Features pour pays (incluant la culture)
        X_pays = df[['type_sol_encoded', 'region_encoded', 'budget', 'surface', 'culture_encoded']]
        y_pays = df['pays_export']
        
        # Entraînement culture
        X_train, X_test, y_train, y_test = train_test_split(X_culture, y_culture, test_size=0.2, random_state=42)
        self.culture_model.fit(X_train, y_train)
        score_culture = self.culture_model.score(X_test, y_test)
        
        # Entraînement pays
        X_train, X_test, y_train, y_test = train_test_split(X_pays, y_pays, test_size=0.2, random_state=42)
        self.pays_model.fit(X_train, y_train)
        score_pays = self.pays_model.score(X_test, y_test)
        
        self.is_trained = True
        
        print(f"   ✅ Précision culture: {score_culture*100:.1f}%")
        print(f"   ✅ Précision pays: {score_pays*100:.1f}%")
        
        # Stocker les données pour calcul de gains
        self.df_reference = df
        
        return score_culture, score_pays
    
    def predict(self, input_data):
        """Prédit la meilleure culture et pays d'export"""
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné. Appelez d'abord .train()")
        
        # Encodage
        type_sol_map = {label: i for i, label in enumerate(self.label_encoder_sol.classes_)}
        region_map = {label: i for i, label in enumerate(self.label_encoder_region.classes_)}
        
        type_sol_encoded = type_sol_map.get(input_data['type_sol'], 0)
        region_encoded = region_map.get(input_data['region'], 0)
        
        # Prédire culture
        X_culture = np.array([[type_sol_encoded, region_encoded, input_data['budget'], input_data['surface']]])
        culture = self.culture_model.predict(X_culture)[0]
        
        # Encoder la culture prédite
        culture_encoded = self.label_encoder_culture.transform([culture])[0]
        
        # Prédire pays
        X_pays = np.array([[type_sol_encoded, region_encoded, input_data['budget'], input_data['surface'], culture_encoded]])
        pays = self.pays_model.predict(X_pays)[0]
        
        # Calculer gains estimés
        gains = self._calculate_gains(culture, input_data['surface'], input_data['budget'])
        
        return {
            'culture': culture,
            'pays': pays,
            'gain_brut': gains['gain_brut'],
            'gain_net': gains['gain_net']
        }
    
    def _calculate_gains(self, culture, surface, budget):
        """Calcule les gains estimés"""
        # Prix moyens par culture (€/tonne)
        prix_base = {
            'tomate': 500,
            'pomme_de_terre': 200,
            'mais': 180,
            'ble': 220,
            'olivier': 3000,
            'vigne': 2500
        }
        
        # Rendement moyen par hectare (tonnes)
        rendement_base = {
            'tomate': 50,
            'pomme_de_terre': 30,
            'mais': 10,
            'ble': 7,
            'olivier': 2,
            'vigne': 8
        }
        
        # Calcul
        rendement = rendement_base.get(culture, 10) * surface
        prix = prix_base.get(culture, 300)
        gain_brut = rendement * prix
        
        # Coûts estimés (35% du gain brut en moyenne)
        gain_net = gain_brut * 0.65
        
        return {
            'gain_brut': round(gain_brut, 2),
            'gain_net': round(gain_net, 2)
        }
    
    def save(self, path='models/export_model.pkl'):
        """Sauvegarde le modèle"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'culture_model': self.culture_model,
                'pays_model': self.pays_model,
                'label_encoder_sol': self.label_encoder_sol,
                'label_encoder_region': self.label_encoder_region,
                'label_encoder_culture': self.label_encoder_culture,
                'is_trained': self.is_trained
            }, f)
        print(f"   💾 Modèle sauvegardé: {path}")
    
    def load(self, path='models/export_model.pkl'):
        """Charge le modèle"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.culture_model = data['culture_model']
            self.pays_model = data['pays_model']
            self.label_encoder_sol = data['label_encoder_sol']
            self.label_encoder_region = data['label_encoder_region']
            self.label_encoder_culture = data['label_encoder_culture']
            self.is_trained = data['is_trained']
        print(f"   📂 Modèle chargé: {path}")


def train_all_models():
    """Entraîne tous les modèles et les sauvegarde"""
    print("\n🤖 === ENTRAÎNEMENT DE TOUS LES MODÈLES ===\n")
    
    # Modèle irrigation
    irrigation_model = IrrigationModel()
    irrigation_model.train()
    irrigation_model.save()
    
    print()
    
    # Modèle maladies
    disease_model = DiseaseDetectionModel()
    disease_model.train()
    disease_model.save()
    
    print()
    
    # Modèle export
    export_model = ExportRecommendationModel()
    export_model.train()
    export_model.save()
    
    print("\n✅ Tous les modèles ont été entraînés et sauvegardés!")

if __name__ == "__main__":
    train_all_models()