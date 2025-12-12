import pandas as pd
import numpy as np
import os

def generate_irrigation_dataset(n_samples=800):
    """Génère un dataset synthétique pour l'irrigation"""
    np.random.seed(42)
    
    # Génération des features
    humidite = np.random.uniform(5, 95, n_samples)
    temperature = np.random.uniform(10, 45, n_samples)
    type_sol = np.random.choice(['argileux', 'sableux', 'limoneux'], n_samples)
    ph = np.random.uniform(4.5, 8.5, n_samples)
    ensoleillement = np.random.uniform(0, 12, n_samples)
    age_culture = np.random.randint(1, 180, n_samples)
    precipitation_prevue = np.random.uniform(0, 50, n_samples)
    
    # Logique de décision pour irrigation
    irriguer = np.zeros(n_samples)
    debit_eau = np.zeros(n_samples)
    duree_minutes = np.zeros(n_samples)
    
    for i in range(n_samples):
        # Décision d'irrigation basée sur plusieurs facteurs
        score_irrigation = 0
        
        # Humidité faible = besoin d'irrigation
        if humidite[i] < 30:
            score_irrigation += 3
        elif humidite[i] < 50:
            score_irrigation += 1
        
        # Température élevée = besoin d'irrigation
        if temperature[i] > 30:
            score_irrigation += 2
        elif temperature[i] > 25:
            score_irrigation += 1
        
        # Précipitation prévue faible = besoin d'irrigation
        if precipitation_prevue[i] < 5:
            score_irrigation += 2
        elif precipitation_prevue[i] < 10:
            score_irrigation += 1
        
        # Ensoleillement élevé = besoin d'irrigation
        if ensoleillement[i] > 8:
            score_irrigation += 1
        
        # Décision finale
        if score_irrigation >= 4:
            irriguer[i] = 1
            
            # Calcul débit et durée
            base_debit = 2.0
            base_duree = 30
            
            # Ajustement selon type de sol
            if type_sol[i] == 'sableux':
                base_debit *= 1.3
                base_duree *= 0.8
            elif type_sol[i] == 'argileux':
                base_debit *= 0.7
                base_duree *= 1.2
            
            # Ajustement selon humidité
            if humidite[i] < 15:
                base_debit *= 1.5
                base_duree *= 1.5
            elif humidite[i] < 30:
                base_debit *= 1.2
                base_duree *= 1.2
            
            debit_eau[i] = np.clip(base_debit + np.random.normal(0, 0.3), 0.5, 5.0)
            duree_minutes[i] = np.clip(base_duree + np.random.normal(0, 5), 10, 120)
    
    # Création du DataFrame
    df = pd.DataFrame({
        'humidite': humidite,
        'temperature': temperature,
        'type_sol': type_sol,
        'ph': ph,
        'ensoleillement': ensoleillement,
        'age_culture': age_culture,
        'precipitation_prevue': precipitation_prevue,
        'irriguer': irriguer.astype(int),
        'debit_eau': debit_eau,
        'duree_minutes': duree_minutes
    })
    
    return df

def generate_disease_dataset(n_samples=500):
    """Génère un dataset synthétique pour la détection de maladies"""
    np.random.seed(42)
    
    maladies = ['sain', 'oïdium', 'rouille', 'mildiou', 'carence_azote']
    
    data = []
    
    for _ in range(n_samples):
        maladie = np.random.choice(maladies)
        
        if maladie == 'sain':
            temp_feuille = np.random.uniform(18, 28)
            hum_feuille = np.random.uniform(40, 70)
            couleur = 0  # vert
            stress_hydrique = np.random.uniform(0, 30)
            ph_sol = np.random.uniform(6.0, 7.5)
            croissance = np.random.uniform(5, 20)
            
        elif maladie == 'oïdium':
            temp_feuille = np.random.uniform(20, 30)
            hum_feuille = np.random.uniform(60, 90)
            couleur = np.random.choice([0, 1])  # vert ou jaune
            stress_hydrique = np.random.uniform(20, 60)
            ph_sol = np.random.uniform(6.5, 8.0)
            croissance = np.random.uniform(-5, 5)
            
        elif maladie == 'rouille':
            temp_feuille = np.random.uniform(15, 25)
            hum_feuille = np.random.uniform(70, 95)
            couleur = np.random.choice([1, 2])  # jaune ou brun
            stress_hydrique = np.random.uniform(30, 70)
            ph_sol = np.random.uniform(5.5, 7.0)
            croissance = np.random.uniform(-10, 3)
            
        elif maladie == 'mildiou':
            temp_feuille = np.random.uniform(12, 22)
            hum_feuille = np.random.uniform(80, 100)
            couleur = 2  # brun
            stress_hydrique = np.random.uniform(40, 80)
            ph_sol = np.random.uniform(5.0, 6.5)
            croissance = np.random.uniform(-15, 0)
            
        else:  # carence_azote
            temp_feuille = np.random.uniform(15, 30)
            hum_feuille = np.random.uniform(30, 70)
            couleur = 1  # jaune
            stress_hydrique = np.random.uniform(10, 50)
            ph_sol = np.random.uniform(7.0, 8.5)
            croissance = np.random.uniform(-8, 2)
        
        data.append({
            'temperature_feuille': temp_feuille,
            'humidite_feuille': hum_feuille,
            'couleur': couleur,
            'stress_hydrique': stress_hydrique,
            'ph_sol': ph_sol,
            'croissance_pct': croissance,
            'maladie': maladie
        })
    
    df = pd.DataFrame(data)
    return df

def generate_export_dataset(n_samples=300):
    """Génère un dataset synthétique pour les recommandations d'export"""
    np.random.seed(42)
    
    cultures = ['tomate', 'pomme_de_terre', 'mais', 'ble', 'olivier', 'vigne']
    types_sol = ['argileux', 'sableux', 'limoneux']
    regions = ['nord', 'centre', 'sud']
    pays_export = ['France', 'Italie', 'Espagne', 'Allemagne', 'Pays-Bas']
    
    data = []
    
    # Prix de base par culture (€/tonne)
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
    
    for _ in range(n_samples):
        type_sol = np.random.choice(types_sol)
        region = np.random.choice(regions)
        budget = np.random.uniform(5000, 100000)
        surface = np.random.uniform(0.5, 20)
        
        # Sélection de la culture en fonction du sol
        if type_sol == 'argileux':
            culture = np.random.choice(['ble', 'mais', 'tomate'], p=[0.4, 0.4, 0.2])
        elif type_sol == 'sableux':
            culture = np.random.choice(['pomme_de_terre', 'vigne'], p=[0.6, 0.4])
        else:  # limoneux
            culture = np.random.choice(['tomate', 'mais', 'olivier'], p=[0.4, 0.3, 0.3])
        
        # Calcul du rendement avec variations
        rendement = rendement_base[culture] * surface * np.random.uniform(0.8, 1.2)
        
        # Pays d'export (influencé par la culture)
        if culture in ['olivier', 'vigne']:
            pays = np.random.choice(['France', 'Italie', 'Espagne'], p=[0.4, 0.4, 0.2])
        else:
            pays = np.random.choice(pays_export)
        
        # Calcul gains
        prix_vente = prix_base[culture] * np.random.uniform(0.9, 1.3)
        gain_brut = rendement * prix_vente
        
        # Coûts (30-50% du gain brut)
        couts = gain_brut * np.random.uniform(0.3, 0.5)
        gain_net = gain_brut - couts
        
        data.append({
            'type_sol': type_sol,
            'region': region,
            'budget': budget,
            'surface': surface,
            'recolte_prevue': rendement,
            'culture': culture,
            'pays_export': pays,
            'gain_brut': gain_brut,
            'gain_net': gain_net
        })
    
    df = pd.DataFrame(data)
    return df

def main():
    """Génère tous les datasets et les sauvegarde"""
    os.makedirs('data', exist_ok=True)
    
    print("🌱 Génération des datasets Feralyx...")
    
    # Dataset irrigation
    print("  📊 Dataset irrigation (800 lignes)...")
    df_irrigation = generate_irrigation_dataset(800)
    df_irrigation.to_csv('data/irrigation_dataset.csv', index=False)
    print(f"     ✅ Sauvegardé : {len(df_irrigation)} lignes")
    
    # Dataset maladies
    print("  🦠 Dataset maladies (500 lignes)...")
    df_disease = generate_disease_dataset(500)
    df_disease.to_csv('data/disease_dataset.csv', index=False)
    print(f"     ✅ Sauvegardé : {len(df_disease)} lignes")
    
    # Dataset export
    print("  🌍 Dataset export (300 lignes)...")
    df_export = generate_export_dataset(300)
    df_export.to_csv('data/export_dataset.csv', index=False)
    print(f"     ✅ Sauvegardé : {len(df_export)} lignes")
    
    print("\n✅ Tous les datasets ont été générés avec succès!")
    print(f"   📁 Emplacement : {os.path.abspath('data/')}")

if __name__ == "__main__":
    main()