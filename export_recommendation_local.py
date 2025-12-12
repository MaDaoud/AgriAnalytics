"""
Feralyx - Système de Recommandation d'Export
VERSION CORRIGÉE - Fonctionne SANS fichier .pkl
Utilise un système à règles expertes
"""

import json

# Base de données des cultures et marchés
MARKET_DATA = {
    'tomate': {
        'rendement_ha': 55,
        'cout_production_ha': 8000,
        'prix_export': {'France': 520, 'Allemagne': 580, 'Italie': 490, 'Espagne': 450},
        'demande': {'France': 'haute', 'Allemagne': 'très haute', 'Italie': 'moyenne'},
        'temp_min': 15, 'temp_max': 35, 'pluie_min': 400, 'pluie_max': 800
    },
    'pomme_de_terre': {
        'rendement_ha': 35,
        'cout_production_ha': 4500,
        'prix_export': {'France': 220, 'Allemagne': 240, 'Belgique': 230, 'Pays-Bas': 250},
        'demande': {'France': 'haute', 'Allemagne': 'très haute', 'Belgique': 'haute'},
        'temp_min': 10, 'temp_max': 25, 'pluie_min': 500, 'pluie_max': 700
    },
    'mais': {
        'rendement_ha': 12,
        'cout_production_ha': 3000,
        'prix_export': {'France': 200, 'Allemagne': 220, 'Italie': 210, 'Espagne': 190},
        'demande': {'France': 'haute', 'Allemagne': 'très haute', 'Italie': 'haute'},
        'temp_min': 18, 'temp_max': 32, 'pluie_min': 450, 'pluie_max': 650
    },
    'ble': {
        'rendement_ha': 8,
        'cout_production_ha': 2500,
        'prix_export': {'France': 240, 'Allemagne': 250, 'Italie': 235, 'Belgique': 245},
        'demande': {'France': 'très haute', 'Allemagne': 'haute', 'Italie': 'haute'},
        'temp_min': 12, 'temp_max': 28, 'pluie_min': 400, 'pluie_max': 600
    },
    'olivier': {
        'rendement_ha': 2.5,
        'cout_production_ha': 6000,
        'prix_export': {'Italie': 3200, 'France': 3000, 'Espagne': 2800, 'Grèce': 2900},
        'demande': {'Italie': 'très haute', 'France': 'haute', 'Grèce': 'haute'},
        'temp_min': 14, 'temp_max': 38, 'pluie_min': 300, 'pluie_max': 600
    },
    'vigne': {
        'rendement_ha': 9,
        'cout_production_ha': 12000,
        'prix_export': {'France': 2800, 'Italie': 2600, 'Allemagne': 2900, 'Suisse': 3200},
        'demande': {'France': 'très haute', 'Italie': 'haute', 'Allemagne': 'haute'},
        'temp_min': 15, 'temp_max': 35, 'pluie_min': 500, 'pluie_max': 800
    }
}

# Compatibilité sol-culture
SOIL_COMPATIBILITY = {
    'argileux': {'tomate': 85, 'pomme_de_terre': 60, 'mais': 90, 'ble': 95, 'olivier': 50, 'vigne': 70},
    'sableux': {'tomate': 60, 'pomme_de_terre': 90, 'mais': 70, 'ble': 65, 'olivier': 75, 'vigne': 85},
    'limoneux': {'tomate': 95, 'pomme_de_terre': 85, 'mais': 80, 'ble': 90, 'olivier': 80, 'vigne': 88}
}

# Adaptation région
REGION_BONUS = {
    'nord': {'ble': 1.1, 'pomme_de_terre': 1.15, 'mais': 1.0},
    'centre': {'tomate': 1.1, 'mais': 1.1, 'ble': 1.05, 'vigne': 1.0},
    'sud': {'olivier': 1.2, 'vigne': 1.15, 'tomate': 1.1}
}

# Climat régional
REGION_CLIMATE = {
    'nord': {'temp_moyenne': 18, 'pluie_annuelle': 600},
    'centre': {'temp_moyenne': 22, 'pluie_annuelle': 450},
    'sud': {'temp_moyenne': 26, 'pluie_annuelle': 200}
}


def evaluate_climate_risk(culture, region):
    """Évalue les risques climatiques"""
    climate = REGION_CLIMATE.get(region, {'temp_moyenne': 20, 'pluie_annuelle': 500})
    culture_data = MARKET_DATA[culture]
    
    risk_score = 0
    risks = []
    
    # Risque température
    if climate['temp_moyenne'] < culture_data['temp_min']:
        risks.append(f"Température trop basse ({climate['temp_moyenne']}°C)")
        risk_score += 30
    elif climate['temp_moyenne'] > culture_data['temp_max']:
        risks.append(f"Température trop élevée ({climate['temp_moyenne']}°C)")
        risk_score += 25
    
    # Risque pluviométrie
    if climate['pluie_annuelle'] < culture_data['pluie_min']:
        risks.append(f"Déficit pluviométrique ({climate['pluie_annuelle']}mm/an)")
        risk_score += 20
    elif climate['pluie_annuelle'] > culture_data['pluie_max']:
        risks.append(f"Excès de pluie ({climate['pluie_annuelle']}mm/an)")
        risk_score += 15
    
    return {
        'score': min(risk_score, 100),
        'niveau': 'faible' if risk_score < 20 else 'modéré' if risk_score < 50 else 'élevé',
        'details': risks if risks else ['Conditions favorables']
    }


def get_export_recommendation_local(soil_type, region, surface_ha, budget_eur, expected_harvest_tonnes):
    """
    Recommande la meilleure culture et pays d'export
    
    Args:
        soil_type: 'argileux', 'sableux', 'limoneux'
        region: 'nord', 'centre', 'sud'
        surface_ha: surface en hectares
        budget_eur: budget disponible
        expected_harvest_tonnes: (ignoré, calculé automatiquement)
    
    Returns:
        dict avec recommandation complète
    """
    
    best_culture = None
    best_score = -999999
    best_details = {}
    
    # Évaluer chaque culture
    for culture, data in MARKET_DATA.items():
        # 1. Vérifier budget
        cout_total = data['cout_production_ha'] * surface_ha
        if cout_total > budget_eur:
            continue
        
        # 2. Compatibilité sol
        soil_score = SOIL_COMPATIBILITY.get(soil_type, {}).get(culture, 50)
        
        # 3. Bonus région
        region_bonus = REGION_BONUS.get(region, {}).get(culture, 1.0)
        
        # 4. Risques climatiques
        climate_risk = evaluate_climate_risk(culture, region)
        climate_penalty = 1.0 - (climate_risk['score'] / 200)
        
        # 5. Rendement
        rendement = data['rendement_ha'] * surface_ha * region_bonus * climate_penalty
        
        # 6. Meilleur pays
        meilleur_pays = max(data['prix_export'].items(), key=lambda x: x[1])
        pays_nom = meilleur_pays[0]
        prix = meilleur_pays[1]
        
        # 7. Calculs financiers
        gain_brut = rendement * prix
        cout_transport = surface_ha * 400
        gain_net = gain_brut - cout_total - cout_transport
        roi = (gain_net / budget_eur * 100) if budget_eur > 0 else 0
        
        # 8. Score global
        score = soil_score * 0.3 + roi * 0.5 + (100 - climate_risk['score']) * 0.2
        
        if score > best_score:
            best_score = score
            best_culture = culture
            best_details = {
                'culture_recommandee': culture,
                'meilleur_pays_export': pays_nom,
                'gain_brut_eur': round(gain_brut, 2),
                'gain_net_eur': round(gain_net, 2),
                'ROI': round(roi, 2),
                'rendement_tonnes': round(rendement, 2),
                'cout_production': round(cout_total, 2),
                'cout_transport': round(cout_transport, 2),
                'score_global': round(score, 1),
                'compatibilite_sol': soil_score,
                'risque_climatique': climate_risk['niveau'],
                'details_risques': climate_risk['details'],
                'commentaire': 'Recommandation basée sur analyse multi-critères'
            }
    
    if best_culture is None:
        return {
            'culture_recommandee': None,
            'meilleur_pays_export': None,
            'gain_brut_eur': None,
            'gain_net_eur': None,
            'ROI': None,
            'commentaire': f'Budget insuffisant. Minimum requis: {min([d["cout_production_ha"] * surface_ha for d in MARKET_DATA.values()]):,.0f}€'
        }
    
    return best_details


# ------------------------
# TEST RAPIDE
# ------------------------
if __name__ == "__main__":
    print("="*70)
    print("🌍 SYSTÈME DE RECOMMANDATION D'EXPORT - VERSION CORRIGÉE")
    print("="*70)
    
    test_data = [
        {"soil": "limoneux", "region": "centre", "surface": 3, "budget": 15000, "harvest": 10},
        {"soil": "argileux", "region": "nord", "surface": 15, "budget": 50000, "harvest": 50},
        {"soil": "sableux", "region": "sud", "surface": 8, "budget": 25000, "harvest": 20},
    ]

    for i, data in enumerate(test_data, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i} : Sol {data['soil']}, Région {data['region']}, {data['surface']}ha, Budget {data['budget']}€")
        print(f"{'='*70}")
        
        result = get_export_recommendation_local(
            soil_type=data["soil"],
            region=data["region"],
            surface_ha=data["surface"],
            budget_eur=data["budget"],
            expected_harvest_tonnes=data["harvest"]
        )
        
        if result['culture_recommandee']:
            print(f"✅ Culture recommandée : {result['culture_recommandee'].upper()}")
            print(f"🌍 Meilleur pays : {result['meilleur_pays_export']}")
            print(f"💰 Gain brut : {result['gain_brut_eur']:,.0f}€")
            print(f"💵 Gain net : {result['gain_net_eur']:,.0f}€")
            print(f"📈 ROI : {result['ROI']:.1f}%")
            print(f"📦 Rendement : {result['rendement_tonnes']:.1f} tonnes")
            print(f"🌡️  Risque climatique : {result['risque_climatique'].upper()}")
            for risque in result['details_risques']:
                print(f"   - {risque}")
        else:
            print(f"❌ {result['commentaire']}")
    
    print(f"\n{'='*70}")
    print("✅ Tests terminés avec succès!")
    print("="*70)