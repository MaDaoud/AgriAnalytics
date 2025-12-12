import sqlite3
import os
from datetime import datetime

class FeralyxDatabase:
    def __init__(self, db_path="data/feralyx.db"):
        """Initialise la base de données SQLite"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Crée toutes les tables nécessaires"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table mesures_sol
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesures_sol (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_mesure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                humidite REAL,
                temperature REAL,
                type_sol TEXT,
                ph REAL,
                ensoleillement REAL,
                age_culture INTEGER,
                precipitation_prevue REAL,
                parcelle_id TEXT
            )
        ''')
        
        # Table irrigation_predictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irrigation_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mesure_id INTEGER,
                irriguer INTEGER,
                debit_eau REAL,
                duree_minutes REAL,
                FOREIGN KEY (mesure_id) REFERENCES mesures_sol(id)
            )
        ''')
        
        # Table diagnostic_maladie
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_maladie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_diagnostic TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                temperature_feuille REAL,
                humidite_feuille REAL,
                couleur INTEGER,
                stress_hydrique REAL,
                ph_sol REAL,
                croissance_pct REAL,
                maladie_detectee TEXT
            )
        ''')
        
        # Table export_recommendation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_recommendation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_recommandation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type_sol TEXT,
                region TEXT,
                budget REAL,
                surface REAL,
                recolte_prevue REAL,
                culture_recommandee TEXT,
                pays_export TEXT,
                gain_brut REAL,
                gain_net REAL
            )
        ''')
        
        # Table logs_chatbot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_chatbot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                question TEXT,
                reponse TEXT
            )
        ''')
        
        # Table alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type_alerte TEXT,
                severite TEXT,
                message TEXT,
                resolu INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée avec succès!")
    
    def insert_mesure_sol(self, data):
        """Insère une mesure de sol"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mesures_sol 
            (humidite, temperature, type_sol, ph, ensoleillement, age_culture, precipitation_prevue, parcelle_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['humidite'], data['temperature'], data['type_sol'], data['ph'],
              data['ensoleillement'], data['age_culture'], data['precipitation_prevue'], 
              data.get('parcelle_id', 'P001')))
        conn.commit()
        mesure_id = cursor.lastrowid
        conn.close()
        return mesure_id
    
    def insert_irrigation_prediction(self, mesure_id, prediction):
        """Insère une prédiction d'irrigation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO irrigation_predictions 
            (mesure_id, irriguer, debit_eau, duree_minutes)
            VALUES (?, ?, ?, ?)
        ''', (mesure_id, prediction['irriguer'], prediction['debit_eau'], prediction['duree_minutes']))
        conn.commit()
        conn.close()
    
    def insert_diagnostic_maladie(self, data, maladie):
        """Insère un diagnostic de maladie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostic_maladie 
            (temperature_feuille, humidite_feuille, couleur, stress_hydrique, ph_sol, croissance_pct, maladie_detectee)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['temperature_feuille'], data['humidite_feuille'], data['couleur'],
              data['stress_hydrique'], data['ph_sol'], data['croissance_pct'], maladie))
        conn.commit()
        conn.close()
    
    def insert_export_recommendation(self, data, recommendation):
        """Insère une recommandation d'export"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO export_recommendation 
            (type_sol, region, budget, surface, recolte_prevue, culture_recommandee, pays_export, gain_brut, gain_net)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['type_sol'], data['region'], data['budget'], data['surface'], data['recolte_prevue'],
              recommendation['culture'], recommendation['pays'], recommendation['gain_brut'], recommendation['gain_net']))
        conn.commit()
        conn.close()
    
    def insert_alerte(self, type_alerte, severite, message):
        """Insère une alerte"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alertes (type_alerte, severite, message)
            VALUES (?, ?, ?)
        ''', (type_alerte, severite, message))
        conn.commit()
        conn.close()
    
    def get_recent_mesures(self, limit=10):
        """Récupère les mesures récentes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM mesures_sol 
            ORDER BY date_mesure DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_alertes_actives(self):
        """Récupère les alertes non résolues"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM alertes 
            WHERE resolu = 0 
            ORDER BY date_alerte DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows