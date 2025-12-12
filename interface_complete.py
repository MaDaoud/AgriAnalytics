"""
Feralyx V2.0 - Interface Graphique Complète
Intégration de tous les modules : Satellite, IA, Heatmaps, Rapports
"""
from email_sender import EmailSender
from tkinter import messagebox


from feralyx import ask_chatbot
import threading



import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
import os
from datetime import datetime


















# Imports des modules Feralyx
try:
    from sentinel_analyzer import SentinelParcelAnalyzer
    from heatmap_generator import HeatmapGenerator
    from ai_models_advanced import AdvancedIrrigationModel, AdvancedDiseaseDetectionModel
    from export_recommendation_local import get_export_recommendation_local
    from report_generator import ReportGenerator
    from email_sender import EmailSender
    MODULES_AVAILABLE = True
except Exception as e:
    MODULES_AVAILABLE = False
    print(f"⚠️ Erreur chargement modules : {e}")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # ------------------------------
#   DESIGN MODERNE FERALYX
# ------------------------------


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class FeralyxApp:
    """Application graphique complète Feralyx"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🛰️ FERALYX V2.0 - Système IA Agricole Avancé")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e2e')
        
        # Style moderne
        self.setup_styles()
        
        # Variables
        self.current_analysis = None
        
        # Charger modules
        self.load_modules()
        
        # Créer interface
        self.create_interface()
        
        # Message de bienvenue
        self.log_message("🚀 Feralyx V2.0 initialisé avec succès !")
        self.log_message("📊 Tous les modules IA sont opérationnels")
    
    def setup_styles(self):
        """Configure les styles modernes"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs
        bg_dark = '#1e1e2e'
        bg_medium = '#2d2d44'
        accent = '#89b4fa'
        text_color = '#cdd6f4'
        
        # Configuration des styles
        style.configure('TFrame', background=bg_dark)
        style.configure('TLabel', background=bg_dark, foreground=text_color, font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground=accent)
        style.configure('TButton', font=('Segoe UI', 10), padding=10)
        style.map('TButton', background=[('active', accent)])
        style.configure('TNotebook', background=bg_dark, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10, 'bold'))
    
    def load_modules(self):
        """Charge tous les modules Feralyx"""
        self.modules = {}
        
        try:
            self.modules['sentinel'] = SentinelParcelAnalyzer()
            self.modules['heatmap'] = HeatmapGenerator()
            
            # Modèles IA
            self.modules['irrigation'] = AdvancedIrrigationModel()
            if os.path.exists('models/irrigation_model_advanced.pkl'):
                self.modules['irrigation'].load()
            
            self.modules['disease'] = AdvancedDiseaseDetectionModel()
            if os.path.exists('models/disease_model_advanced.pkl'):
                self.modules['disease'].load()
            
            self.modules['report'] = ReportGenerator()
            self.modules['email'] = EmailSender()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement modules : {e}")
    
    def create_interface(self):
        """Crée l'interface graphique"""
        
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(
            header,
            text="🛰️ FERALYX V2.0 - Intelligence Artificielle Agricole",
            style='Title.TLabel'
        ).pack(side='left')
        
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Onglets
        self.create_satellite_tab()
        self.create_ai_analysis_tab()
        self.create_heatmap_tab()
        self.create_reports_tab()
        
        
        # Ajouter onglet Chatbot
        tab_chat = ttk.Frame(self.notebook)
        self.notebook.add(tab_chat, text="💬 Chatbot")
        self.build_chat_ui(tab_chat)

        
        # Console de logs (bas de l'écran)
        self.create_log_console()
    
    def create_satellite_tab(self):
        """Onglet Analyse Satellite"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🛰️ Analyse Satellite")
        
        # Panneau gauche : Formulaire
        left_panel = ttk.Frame(tab)
        left_panel.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left_panel, text="📍 COORDONNÉES PARCELLE", style='Title.TLabel').pack(anchor='w', pady=10)
        
        # Latitude
        ttk.Label(left_panel, text="Latitude :").pack(anchor='w', pady=5)
        self.sat_lat = ttk.Entry(left_panel, font=('Segoe UI', 12), width=30)
        self.sat_lat.insert(0, "36.8")
        self.sat_lat.pack(anchor='w', pady=5)
        
        # Longitude
        ttk.Label(left_panel, text="Longitude :").pack(anchor='w', pady=5)
        self.sat_lon = ttk.Entry(left_panel, font=('Segoe UI', 12), width=30)
        self.sat_lon.insert(0, "10.2")
        self.sat_lon.pack(anchor='w', pady=5)
        
        # Taille
        ttk.Label(left_panel, text="Taille parcelle (km) :").pack(anchor='w', pady=5)
        self.sat_size = ttk.Entry(left_panel, font=('Segoe UI', 12), width=30)
        self.sat_size.insert(0, "0.5")
        self.sat_size.pack(anchor='w', pady=5)
        
        # Pays
        ttk.Label(left_panel, text="Pays :").pack(anchor='w', pady=5)
        self.sat_country = ttk.Combobox(left_panel, values=['tunisie', 'france', 'italie', 'espagne'], 
                                        font=('Segoe UI', 12), width=28, state='readonly')
        self.sat_country.set('tunisie')
        self.sat_country.pack(anchor='w', pady=5)
        
        # Région
        ttk.Label(left_panel, text="Région :").pack(anchor='w', pady=5)
        self.sat_region = ttk.Combobox(left_panel, values=['nord', 'centre', 'sud'], 
                                       font=('Segoe UI', 12), width=28, state='readonly')
        self.sat_region.set('centre')
        self.sat_region.pack(anchor='w', pady=5)
        
        # Bouton Analyser
        ttk.Button(
            left_panel,
            text="🚀 ANALYSER PARCELLE",
            command=self.analyze_parcel
        ).pack(pady=20, fill='x')
        
        # Panneau droit : Résultats
        right_panel = ttk.Frame(tab)
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_panel, text="📊 RÉSULTATS ANALYSE", style='Title.TLabel').pack(anchor='w', pady=10)
        
        self.sat_results = scrolledtext.ScrolledText(
            right_panel,
            font=('Consolas', 10),
            bg='#2d2d44',
            fg='#cdd6f4',
            height=30,
            wrap=tk.WORD
        )
        self.sat_results.pack(fill='both', expand=True)
    
    def create_ai_analysis_tab(self):
        """Onglet Analyses IA (Irrigation, Maladies, Export)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🤖 Analyses IA")
        
        # Sous-onglets
        sub_notebook = ttk.Notebook(tab)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Irrigation
        irr_tab = self.create_irrigation_subtab()
        sub_notebook.add(irr_tab, text="💧 Irrigation")
        
        # Maladies
        disease_tab = self.create_disease_subtab()
        sub_notebook.add(disease_tab, text="🦠 Maladies")
        
        # Export
        export_tab = self.create_export_subtab()
        sub_notebook.add(export_tab, text="🌍 Export")
    
    def create_irrigation_subtab(self):
        """Sous-onglet irrigation"""
        frame = ttk.Frame()
        
        left = ttk.Frame(frame)
        left.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left, text="💧 PRÉDICTION IRRIGATION", style='Title.TLabel').pack(anchor='w', pady=10)
        
        # Champs
        fields = [
            ("Humidité sol (%)", "irr_humidite", "25"),
            ("Température (°C)", "irr_temp", "35"),
            ("pH", "irr_ph", "6.5"),
            ("Ensoleillement (h)", "irr_sun", "10"),
            ("Âge culture (jours)", "irr_age", "45"),
            ("Précipitation prévue (mm)", "irr_rain", "5")
        ]
        
        self.irr_vars = {}
        for label, var_name, default in fields:
            ttk.Label(left, text=label).pack(anchor='w', pady=2)
            entry = ttk.Entry(left, font=('Segoe UI', 11), width=30)
            entry.insert(0, default)
            entry.pack(anchor='w', pady=2)
            self.irr_vars[var_name] = entry
        
        # Type sol
        ttk.Label(left, text="Type de sol :").pack(anchor='w', pady=2)
        self.irr_soil = ttk.Combobox(left, values=['argileux', 'sableux', 'limoneux'], 
                                     font=('Segoe UI', 11), width=28, state='readonly')
        self.irr_soil.set('limoneux')
        self.irr_soil.pack(anchor='w', pady=2)
        
        ttk.Button(left, text="🚀 PRÉDIRE", command=self.predict_irrigation).pack(pady=20, fill='x')
        
        # Résultats
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right, text="📊 RÉSULTAT", style='Title.TLabel').pack(anchor='w', pady=10)
        self.irr_result = scrolledtext.ScrolledText(right, font=('Consolas', 10), 
                                                     bg='#2d2d44', fg='#cdd6f4', height=25)
        self.irr_result.pack(fill='both', expand=True)
        
        return frame
    
    def create_disease_subtab(self):
        """Sous-onglet maladies"""
        frame = ttk.Frame()
        
        left = ttk.Frame(frame)
        left.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left, text="🦠 DIAGNOSTIC MALADIES", style='Title.TLabel').pack(anchor='w', pady=10)
        
        fields = [
            ("Température feuille (°C)", "dis_temp", "28"),
            ("Humidité feuille (%)", "dis_hum", "65"),
            ("Stress hydrique (%)", "dis_stress", "25"),
            ("pH sol", "dis_ph", "6.5"),
            ("Croissance (%)", "dis_growth", "8")
        ]
        
        self.dis_vars = {}
        for label, var_name, default in fields:
            ttk.Label(left, text=label).pack(anchor='w', pady=2)
            entry = ttk.Entry(left, font=('Segoe UI', 11), width=30)
            entry.insert(0, default)
            entry.pack(anchor='w', pady=2)
            self.dis_vars[var_name] = entry
        
        # Couleur feuille
        ttk.Label(left, text="Couleur feuille :").pack(anchor='w', pady=2)
        self.dis_color = ttk.Combobox(left, values=['Vert (sain)', 'Jaune', 'Brun'], 
                                      font=('Segoe UI', 11), width=28, state='readonly')
        self.dis_color.set('Vert (sain)')
        self.dis_color.pack(anchor='w', pady=2)
        
        ttk.Button(left, text="🚀 DIAGNOSTIQUER", command=self.diagnose_disease).pack(pady=20, fill='x')
        
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right, text="📊 DIAGNOSTIC", style='Title.TLabel').pack(anchor='w', pady=10)
        self.dis_result = scrolledtext.ScrolledText(right, font=('Consolas', 10), 
                                                     bg='#2d2d44', fg='#cdd6f4', height=25)
        self.dis_result.pack(fill='both', expand=True)
        
        return frame
    
    def create_export_subtab(self):
        """Sous-onglet export"""
        frame = ttk.Frame()
        
        left = ttk.Frame(frame)
        left.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left, text="🌍 RECOMMANDATION EXPORT", style='Title.TLabel').pack(anchor='w', pady=10)
        
        # Type sol
        ttk.Label(left, text="Type de sol :").pack(anchor='w', pady=5)
        self.exp_soil = ttk.Combobox(left, values=['argileux', 'sableux', 'limoneux'], 
                                     font=('Segoe UI', 11), width=28, state='readonly')
        self.exp_soil.set('limoneux')
        self.exp_soil.pack(anchor='w', pady=5)
        
        # Région
        ttk.Label(left, text="Région :").pack(anchor='w', pady=5)
        self.exp_region = ttk.Combobox(left, values=['nord', 'centre', 'sud'], 
                                       font=('Segoe UI', 11), width=28, state='readonly')
        self.exp_region.set('centre')
        self.exp_region.pack(anchor='w', pady=5)
        
        # Budget
        ttk.Label(left, text="Budget (€) :").pack(anchor='w', pady=5)
        self.exp_budget = ttk.Entry(left, font=('Segoe UI', 11), width=30)
        self.exp_budget.insert(0, "50000")
        self.exp_budget.pack(anchor='w', pady=5)
        
        # Surface
        ttk.Label(left, text="Surface (ha) :").pack(anchor='w', pady=5)
        self.exp_surface = ttk.Entry(left, font=('Segoe UI', 11), width=30)
        self.exp_surface.insert(0, "10")
        self.exp_surface.pack(anchor='w', pady=5)
        
        ttk.Button(left, text="🚀 RECOMMANDER", command=self.recommend_export).pack(pady=20, fill='x')
        
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right, text="📊 RECOMMANDATION", style='Title.TLabel').pack(anchor='w', pady=10)
        self.exp_result = scrolledtext.ScrolledText(right, font=('Consolas', 10), 
                                                     bg='#2d2d44', fg='#cdd6f4', height=25)
        self.exp_result.pack(fill='both', expand=True)
        
        return frame
    
    def create_heatmap_tab(self):
        """Onglet Heatmaps"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🗺️ Heatmaps")
        
        ttk.Label(tab, text="🗺️ GÉNÉRATION HEATMAPS INTERACTIVES", style='Title.TLabel').pack(pady=20)
        
        # Pays
        ttk.Label(tab, text="Sélectionnez le pays :").pack(pady=10)
        self.hm_country = ttk.Combobox(tab, values=['tunisie', 'france', 'italie', 'espagne'], 
                                       font=('Segoe UI', 12), width=30, state='readonly')
        self.hm_country.set('tunisie')
        self.hm_country.pack(pady=10)
        
        # Résolution
        ttk.Label(tab, text="Résolution (points) :").pack(pady=10)
        self.hm_resolution = ttk.Spinbox(tab, from_=10, to=50, font=('Segoe UI', 12), width=30)
        self.hm_resolution.set(20)
        self.hm_resolution.pack(pady=10)
        
        # Boutons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="🌟 Heatmap Opportunités", 
                  command=self.generate_opportunity_heatmap, width=30).pack(pady=10)
        
        ttk.Button(btn_frame, text="🌱 Heatmap Fertilité", 
                  command=self.generate_fertility_heatmap, width=30).pack(pady=10)
        
        ttk.Button(btn_frame, text="🗺️ Carte Multi-Couches", 
                  command=self.generate_multilayer_map, width=30).pack(pady=10)
    
    def create_reports_tab(self):
        """Onglet Rapports"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📄 Rapports")
        
        ttk.Label(tab, text="📄 GÉNÉRATION ET ENVOI RAPPORTS", style='Title.TLabel').pack(pady=20)
        
        # Boutons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📄 Générer Rapport Complet", 
                  command=self.generate_full_report, width=40).pack(pady=10)
        
        ttk.Button(btn_frame, text="📧 Envoyer par Email", 
                  command=self.send_email_report, width=40).pack(pady=10)
        
        ttk.Button(btn_frame, text="📁 Ouvrir Dossier Rapports", 
                  command=lambda: os.startfile('reports') if os.path.exists('reports') else None, width=40).pack(pady=10)
    
    def create_log_console(self):
        """Console de logs"""
        console_frame = ttk.Frame(self.root)
        console_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(console_frame, text="📋 CONSOLE", style='Title.TLabel').pack(anchor='w')
        
        self.log_console = scrolledtext.ScrolledText(
            console_frame,
            font=('Consolas', 9),
            bg='#181825',
            fg='#a6e3a1',
            height=8
        )
        self.log_console.pack(fill='x', pady=5)
    
    def log_message(self, message):
        """Ajoute message dans console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_console.see(tk.END)
    
    def analyze_parcel(self):
        """Analyse parcelle satellite"""
        def run_analysis():
            try:
                lat = float(self.sat_lat.get())
                lon = float(self.sat_lon.get())
                size = float(self.sat_size.get())
                country = self.sat_country.get()
                region = self.sat_region.get()
                
                self.log_message(f"🛰️ Analyse parcelle {lat}, {lon}...")
                
                result = self.modules['sentinel'].analyze_parcel_complete(
                    lat, lon, size, country, region
                )
                
                self.current_analysis = result
                
                # Afficher résultats
                output = f"""
╔══════════════════════════════════════════════════════════════╗
║              🛰️ ANALYSE SATELLITE COMPLÈTE                   ║
╚══════════════════════════════════════════════════════════════╝

📍 LOCALISATION :
   Latitude  : {lat}
   Longitude : {lon}
   Pays      : {country.upper()}
   Région    : {region.upper()}

{result['categorie']}

📊 SCORES :
   Score opportunité : {result['score_opportunite']:.1f}/100
   Fertilité         : {result['fertilite']:.1f}/100
   Santé végétation  : {result['sante_vegetation']}
   Disponibilité eau : {result['disponibilite_eau']}

💰 ESTIMATION FINANCIÈRE :
   Valeur totale  : {result['valeur_totale']:,.0f} €
   Valeur/hectare : {result['valeur_par_ha']:,.0f} €/ha

🌾 RECOMMANDATION CULTURE :
   Culture          : {result['culture_recommandee'].upper()}
   Rendement estimé : {result['rendement_estime']} t/ha
   Gain annuel brut : {result['gain_annuel_brut']:,.0f} €
   Gain annuel net  : {result['gain_annuel_net']:,.0f} €
   ROI annuel       : {result['roi_annuel']:.1f}%

⚠️ RISQUES IDENTIFIÉS :
"""
                for risque in result['risques']:
                    output += f"   • {risque}\n"
                
                self.sat_results.delete(1.0, tk.END)
                self.sat_results.insert(1.0, output)
                
                self.log_message("✅ Analyse terminée avec succès")
                
            except Exception as e:
                self.log_message(f"❌ Erreur : {e}")
                messagebox.showerror("Erreur", str(e))
        
        threading.Thread(target=run_analysis, daemon=True).start()
    
    def predict_irrigation(self):
        """Prédiction irrigation"""
        try:
            data = {
                'humidite': float(self.irr_vars['irr_humidite'].get()),
                'temperature': float(self.irr_vars['irr_temp'].get()),
                'type_sol': self.irr_soil.get(),
                'ph': float(self.irr_vars['irr_ph'].get()),
                'ensoleillement': float(self.irr_vars['irr_sun'].get()),
                'age_culture': int(self.irr_vars['irr_age'].get()),
                'precipitation_prevue': float(self.irr_vars['irr_rain'].get())
            }
            
            self.log_message("💧 Prédiction irrigation...")
            result = self.modules['irrigation'].predict(data)
            
            output = f"""
╔══════════════════════════════════════════════════════════════╗
║              💧 PRÉDICTION IRRIGATION                        ║
╚══════════════════════════════════════════════════════════════╝

📊 DONNÉES D'ENTRÉE :
   Humidité sol    : {data['humidite']}%
   Température     : {data['temperature']}°C
   Type de sol     : {data['type_sol']}
   pH              : {data['ph']}
   Ensoleillement  : {data['ensoleillement']}h
   Âge culture     : {data['age_culture']} jours
   Précipitation   : {data['precipitation_prevue']}mm

🎯 RÉSULTAT :
"""
            
            if result['irriguer'] == 1:
                output += f"""
   ✅ IRRIGATION NÉCESSAIRE
   
   💧 Débit recommandé : {result['debit_eau']} L/s
   ⏱️  Durée           : {result['duree_minutes']} minutes
   📈 Confiance        : {result['confiance']:.1f}%
   
   💡 Volume total : {result['debit_eau'] * result['duree_minutes'] * 60:.0f} litres
"""
            else:
                output += f"""
   ❌ PAS D'IRRIGATION NÉCESSAIRE
   
   📈 Confiance : {result['confiance']:.1f}%
   
   💡 Les conditions actuelles sont satisfaisantes.
"""
            
            self.irr_result.delete(1.0, tk.END)
            self.irr_result.insert(1.0, output)
            
            self.log_message("✅ Prédiction irrigation terminée")
            
        except Exception as e:
            self.log_message(f"❌ Erreur : {e}")
            messagebox.showerror("Erreur", str(e))
    
    def diagnose_disease(self):
        """Diagnostic maladies"""
        try:
            color_map = {'Vert (sain)': 0, 'Jaune': 1, 'Brun': 2}
            
            data = {
                'temperature_feuille': float(self.dis_vars['dis_temp'].get()),
                'humidite_feuille': float(self.dis_vars['dis_hum'].get()),
                'couleur': color_map[self.dis_color.get()],
                'stress_hydrique': float(self.dis_vars['dis_stress'].get()),
                'ph_sol': float(self.dis_vars['dis_ph'].get()),
                'croissance_pct': float(self.dis_vars['dis_growth'].get())
            }
            
            self.log_message("🦠 Diagnostic maladies...")
            result = self.modules['disease'].predict(data)
            
            maladie = result['maladie']
            confiance = result['confiance']
            
            output = f"""
╔══════════════════════════════════════════════════════════════╗
║              🦠 DIAGNOSTIC MALADIES                          ║
╚══════════════════════════════════════════════════════════════╝

📊 DONNÉES D'ENTRÉE :
   Température feuille : {data['temperature_feuille']}°C
   Humidité feuille    : {data['humidite_feuille']}%
   Couleur feuille     : {self.dis_color.get()}
   Stress hydrique     : {data['stress_hydrique']}%
   pH sol              : {data['ph_sol']}
   Croissance          : {data['croissance_pct']}%

🎯 DIAGNOSTIC :
"""
            
            if maladie == 'sain':
                output += f"""
   ✅ PLANTE SAINE
   
   📈 Confiance : {confiance:.1f}%
   
   💡 Aucune maladie détectée. Continuez le suivi régulier.
"""
            else:
                output += f"""
   ⚠️ MALADIE DÉTECTÉE : {maladie.upper().replace('_', ' ')}
   
   📈 Confiance : {confiance:.1f}%
   
   💡 ACTIONS RECOMMANDÉES :
"""
                if maladie == 'oidium':
                    output += "      • Traiter au soufre ou fongicide spécifique\n"
                    output += "      • Améliorer aération des plants\n"
                    output += "      • Réduire humidité ambiante\n"
                elif maladie == 'rouille':
                    output += "      • Traiter avec fongicide cuivrique\n"
                    output += "      • Éliminer feuilles atteintes\n"
                    output += "      • Espacer davantage les plants\n"
                elif maladie == 'mildiou':
                    output += "      • Traitement fongicide urgent\n"
                    output += "      • Éviter arrosage sur feuillage\n"
                    output += "      • Détruire plants très atteints\n"
                elif maladie == 'carence_azote':
                    output += "      • Apporter engrais azoté\n"
                    output += "      • Vérifier pH du sol\n"
                    output += "      • Améliorer fertilité du sol\n"
            
            self.dis_result.delete(1.0, tk.END)
            self.dis_result.insert(1.0, output)
            
            self.log_message("✅ Diagnostic terminé")
            
        except Exception as e:
            self.log_message(f"❌ Erreur : {e}")
            messagebox.showerror("Erreur", str(e))
    
    def recommend_export(self):
        """Recommandation export"""
        try:
            soil = self.exp_soil.get()
            region = self.exp_region.get()
            budget = int(self.exp_budget.get())
            surface = float(self.exp_surface.get())
            
            self.log_message("🌍 Recommandation export...")
            
            result = get_export_recommendation_local(
                soil_type=soil,
                region=region,
                surface_ha=surface,
                budget_eur=budget,
                expected_harvest_tonnes=0
            )
            
            output = f"""
╔══════════════════════════════════════════════════════════════╗
║              🌍 RECOMMANDATION D'EXPORT                       ║
╚══════════════════════════════════════════════════════════════╝

📊 PROFIL :
   Type de sol : {soil}
   Région      : {region}
   Budget      : {budget:,} €
   Surface     : {surface} ha

🎯 RECOMMANDATION :
"""
            
            if result['culture_recommandee']:
                output += f"""
   🌾 Culture       : {result['culture_recommandee'].upper()}
   🌍 Pays d'export : {result['meilleur_pays_export']}
   
💰 ESTIMATION FINANCIÈRE :
   Gain brut    : {result['gain_brut_eur']:,.0f} €
   Gain net     : {result['gain_net_eur']:,.0f} €
   ROI          : {result['ROI']:.1f}%
   Rendement    : {result.get('rendement_tonnes', 0):.1f} tonnes
   
🌡️ RISQUE CLIMATIQUE :
   Niveau : {result.get('risque_climatique', 'N/A').upper()}
"""
                if 'details_risques' in result:
                    output += "\n⚠️ RISQUES :\n"
                    for risque in result['details_risques']:
                        output += f"   • {risque}\n"
            else:
                output += f"\n   ❌ {result['commentaire']}\n"
            
            self.exp_result.delete(1.0, tk.END)
            self.exp_result.insert(1.0, output)
            
            self.log_message("✅ Recommandation terminée")
            
        except Exception as e:
            self.log_message(f"❌ Erreur : {e}")
            messagebox.showerror("Erreur", str(e))
    
    def generate_opportunity_heatmap(self):
        """Génère heatmap opportunités"""
        def generate():
            try:
                country = self.hm_country.get()
                resolution = int(self.hm_resolution.get())
                
                self.log_message(f"🗺️ Génération heatmap opportunités {country}...")
                
                filepath = self.modules['heatmap'].generate_opportunity_heatmap(
                    country, resolution
                )
                
                self.log_message(f"✅ Heatmap générée : {filepath}")
                webbrowser.open(filepath)
                
            except Exception as e:
                self.log_message(f"❌ Erreur : {e}")
                messagebox.showerror("Erreur", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_fertility_heatmap(self):
        """Génère heatmap fertilité"""
        def generate():
            try:
                country = self.hm_country.get()
                resolution = int(self.hm_resolution.get())
                
                self.log_message(f"🗺️ Génération heatmap fertilité {country}...")
                
                filepath = self.modules['heatmap'].generate_fertility_heatmap(
                    country, resolution
                )
                
                self.log_message(f"✅ Heatmap générée : {filepath}")
                webbrowser.open(filepath)
                
            except Exception as e:
                self.log_message(f"❌ Erreur : {e}")
                messagebox.showerror("Erreur", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_multilayer_map(self):
        """Génère carte multi-couches"""
        def generate():
            try:
                country = self.hm_country.get()
                
                self.log_message(f"🗺️ Génération carte multi-couches {country}...")
                
                filepath = self.modules['heatmap'].generate_multi_layer_map(country)
                
                self.log_message(f"✅ Carte générée : {filepath}")
                webbrowser.open(filepath)
                
            except Exception as e:
                self.log_message(f"❌ Erreur : {e}")
                messagebox.showerror("Erreur", str(e))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def generate_full_report(self):
        """Génère rapport complet"""
        self.log_message("📄 Génération rapport complet...")
        
        if self.current_analysis:
            messagebox.showinfo("Rapport", "Rapport généré avec dernière analyse satellite")
        else:
            messagebox.showinfo("Rapport", "Effectuez d'abord une analyse satellite")
            
            
            
            
            
            
            
            
            
            
    def generate_combined_report(self):
        """Crée un rapport HTML complet avec toutes les analyses"""
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join('reports', f'report_{timestamp}.html')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("<html><head><meta charset='UTF-8'><title>Rapport Feralyx</title></head><body>")
            f.write("<h1>📊 Rapport Complet Feralyx</h1>")
            
            # Analyse Satellite
            if self.current_analysis:
                f.write("<h2>🛰️ Analyse Satellite</h2>")
                f.write(f"<pre>{self.sat_results.get(1.0, tk.END)}</pre>")
            
            # Irrigation
            if hasattr(self, 'dernier_irrigation') and self.dernier_irrigation:
                f.write("<h2>💧 Prédiction Irrigation</h2>")
                f.write(f"<pre>{self.irr_result.get(1.0, tk.END)}</pre>")
            
            # Maladies
            if hasattr(self, 'dernier_diagnostic') and self.dernier_diagnostic:
                f.write("<h2>🦠 Diagnostic Maladies</h2>")
                f.write(f"<pre>{self.dis_result.get(1.0, tk.END)}</pre>")
            
            # Export
            if hasattr(self, 'derniere_export') and self.derniere_export:
                f.write("<h2>🌍 Recommandation Export</h2>")
                f.write(f"<pre>{self.exp_result.get(1.0, tk.END)}</pre>")
            
            # Heatmaps
            f.write("<h2>🗺️ Heatmaps</h2>")
            f.write("<p>Les heatmaps générées sont disponibles dans le dossier 'reports'</p>")
            
            f.write("</body></html>")
        
        self.log_message(f"✅ Rapport HTML complet généré : {report_path}")
        return report_path

    
    def send_email_report(self, event=None):
        """
        Envoie le dernier rapport HTML par email via EmailSender.
        Heatmaps non inclus.
        """
        try:
            from email_sender import EmailSender
        except ImportError:
            print("❌ Module EmailSender non trouvé. Vérifiez email_sender.py")
            return

        email_sender = EmailSender()
        email_sender.configure(
            provider='gmail',
            email='daoudmohamedali2@gmail.com',
            password='adedmsbpjfpfvbfo'
        )

        reports_dir = 'reports'
        if os.path.exists(reports_dir):
            reports = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
            if reports:
                latest_report = os.path.join(reports_dir, sorted(reports)[-1])
                print(f"📄 Rapport trouvé : {latest_report}")
            else:
                print("⚠️ Aucun rapport HTML trouvé dans 'reports'.")
                return
        else:
            print("⚠️ Dossier 'reports' introuvable.")
            return

        # Fichiers additionnels excluent heatmaps
        additional_files = [
            f for f in os.listdir(reports_dir)
            if f.endswith('.pdf') or f.endswith('.csv')  # Exclut heatmaps images .png ou .jpg
        ]
        additional_files = [os.path.join(reports_dir, f) for f in additional_files]

        success = email_sender.send_report(
            recipient_email='daoudmohamedali2@gmail.com',
            report_path=latest_report,
            additional_files=additional_files,
            irrigation_prediction={'irriguer': 1, 'debit_eau': 2.5, 'duree_minutes': 45},
            disease_diagnosis={'maladie': 'sain', 'confiance': 95.5},
            export_recommendation={'culture_recommandee': 'tomate', 'meilleur_pays_export': 'France', 'ROI': 45.2}
        )

        if success:
            print("✅ Email envoyé avec succès !")
        else:
            print("❌ L'envoi de l'email a échoué.")
            
            
            
            
    def build_chat_ui(self, parent):
        frame_chat = ttk.LabelFrame(parent, text="Chatbot Feralyx", padding=10)
        frame_chat.pack(fill='both', expand=True)

        self.chat_display = scrolledtext.ScrolledText(frame_chat, wrap=tk.WORD, height=20, state='disabled')
        self.chat_display.pack(fill='both', expand=True, padx=5, pady=5)

        self.user_input = ttk.Entry(frame_chat)
        self.user_input.pack(fill='x', padx=5, pady=5)
        self.user_input.bind("<Return>", self.send_message)

        ttk.Button(frame_chat, text="Envoyer", command=self.send_message).pack(pady=5)

    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self._update_chat(f"Vous : {user_text}\n")
        self.user_input.delete(0, tk.END)

        # Thread pour ne pas bloquer l'interface
        threading.Thread(target=self._run_chat, args=(user_text,), daemon=True).start()

    def _run_chat(self, user_text):
        try:
            response = ask_chatbot(user_text)  # Appel réel à OpenAI
            self._update_chat(f"Chatbot : {response}\n")
        except Exception as e:
            self._update_chat(f"❌ Erreur chatbot : {str(e)}\n")

    def _update_chat(self, message):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, message)
        self.chat_display.see(tk.END)
        self.chat_display.configure(state='disabled')
        
        
        
        
        
    
    from tkinter import ttk

def apply_modern_style(root):
    style = ttk.Style(root)

    # Thème de base
    style.theme_use("clam")

    # Couleur principale
    primary = "#2A6DB0"      # bleu moderne
    secondary = "#F5F7FA"    # fond clair
    text_color = "#1E1E1E"   # texte

    # Onglets
    style.configure("TNotebook", background=secondary, borderwidth=0)
    style.configure("TNotebook.Tab", 
                    background="#DDE3EB", 
                    padding=(15, 8),
                    font=("Segoe UI", 11, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", primary)],
              foreground=[("selected", "white")])

    # Frames
    style.configure("TFrame", background=secondary)
    style.configure("TLabelframe", background=secondary)
    style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    # Labels
    style.configure("TLabel", background=secondary, foreground=text_color, font=("Segoe UI", 10))

    # Boutons
    style.configure("TButton",
                    background=primary,
                    foreground="white",
                    padding=10,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0)
    style.map("TButton",
              background=[("active", "#1F5A8A")])

    # Champs texte
    style.configure("TEntry", padding=6)







def main():
    """Lance l'application"""
    import tkinter as tk

    root = tk.Tk()
    app = FeralyxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
