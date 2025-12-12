"""
Feralyx - Système d'Envoi d'Emails
Envoie les rapports par email avec pièces jointes
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class EmailSender:
    """Gère l'envoi d'emails avec pièces jointes"""
    
    def __init__(self, smtp_server=None, smtp_port=None, email=None, password=None):
        """
        Initialise le système d'envoi d'emails
        
        Args:
            smtp_server: Serveur SMTP (ex: smtp.gmail.com)
            smtp_port: Port SMTP (587 pour Gmail)
            email: Adresse email d'envoi
            password: Mot de passe d'application
        
        Configuration recommandée pour Gmail:
        1. Aller sur myaccount.google.com
        2. Sécurité → Validation en 2 étapes (activer)
        3. Mots de passe d'application → Créer un mot de passe
        """
        self.smtp_server = smtp_server or 'smtp.gmail.com'
        self.smtp_port = smtp_port or 587
        self.email = email
        self.password = password
        
        # Configuration par défaut pour différents fournisseurs
        self.smtp_configs = {
            'gmail': {'server': 'smtp.gmail.com', 'port': 587},
            'outlook': {'server': 'smtp-mail.outlook.com', 'port': 587},
            'yahoo': {'server': 'smtp.mail.yahoo.com', 'port': 587},
            'icloud': {'server': 'smtp.mail.me.com', 'port': 587}
        }
    
    def configure(self, provider='gmail', email=None, password=None):
        """
        Configure rapidement pour un fournisseur connu
        
        Args:
            provider: 'gmail', 'outlook', 'yahoo', 'icloud'
            email: Votre adresse email
            password: Votre mot de passe d'application
        """
        if provider in self.smtp_configs:
            config = self.smtp_configs[provider]
            self.smtp_server = config['server']
            self.smtp_port = config['port']
        
        if email:
            self.email = email
        if password:
            self.password = password
        
        print(f"✅ Configuration email : {provider}")
        print(f"   Serveur : {self.smtp_server}:{self.smtp_port}")
        print(f"   Email : {self.email}")
    
    def send_report(self, recipient_email, report_path, subject=None, 
                    additional_files=None, include_summary=True,
                    irrigation_prediction=None, disease_diagnosis=None, 
                    export_recommendation=None):
        """
        Envoie un rapport par email
        
        Args:
            recipient_email: Email du destinataire
            report_path: Chemin vers le fichier rapport HTML
            subject: Sujet de l'email (auto-généré si None)
            additional_files: Liste de fichiers supplémentaires à joindre
            include_summary: Inclure un résumé dans le corps de l'email
            irrigation_prediction: Dict de prédiction irrigation
            disease_diagnosis: Dict de diagnostic
            export_recommendation: Dict de recommandation export
        
        Returns:
            bool: True si succès, False sinon
        """
        
        if not self.email or not self.password:
            print("❌ Configuration email manquante. Utilisez .configure() d'abord.")
            return False
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            
            # Sujet
            if subject is None:
                date_str = datetime.now().strftime("%d/%m/%Y")
                subject = f"🌾 Rapport Feralyx - {date_str}"
            
            msg['From'] = self.email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Corps de l'email
            if include_summary:
                body = self._create_email_body(
                    irrigation_prediction, 
                    disease_diagnosis, 
                    export_recommendation
                )
            else:
                body = """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #2E86AB;">Rapport Feralyx</h2>
                    <p>Veuillez trouver ci-joint votre rapport d'analyse agricole complet.</p>
                    <p>Cordialement,<br>L'équipe Feralyx</p>
                </body>
                </html>
                """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Joindre le rapport principal
            if os.path.exists(report_path):
                self._attach_file(msg, report_path)
            else:
                print(f"⚠️ Fichier rapport introuvable : {report_path}")
            
            # Joindre fichiers additionnels
            if additional_files:
                for file_path in additional_files:
                    if os.path.exists(file_path):
                        self._attach_file(msg, file_path)
            
            # Envoi
            print(f"📧 Connexion au serveur SMTP {self.smtp_server}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            print(f"🔐 Authentification...")
            server.login(self.email, self.password)
            
            print(f"📨 Envoi de l'email à {recipient_email}...")
            text = msg.as_string()
            server.sendmail(self.email, recipient_email, text)
            server.quit()
            
            print(f"✅ Email envoyé avec succès !")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Erreur d'authentification. Vérifiez votre email et mot de passe.")
            print("   Pour Gmail, utilisez un 'Mot de passe d'application'")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Erreur SMTP : {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue : {str(e)}")
            return False
    
    def _attach_file(self, msg, file_path):
        """Attache un fichier au message"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
            print(f"   📎 Fichier joint : {filename}")
        except Exception as e:
            print(f"   ⚠️ Impossible de joindre {file_path} : {str(e)}")
    
    def _create_email_body(self, irrigation_prediction, disease_diagnosis, export_recommendation):
        """Crée un corps d'email avec résumé"""
        
        body = """
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2E86AB 0%, #06D6A0 100%); 
                          color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                .section {{ background: #f8f9fa; padding: 20px; margin: 20px 0; 
                           border-radius: 10px; border-left: 5px solid #2E86AB; }}
                .section h3 {{ color: #2E86AB; margin-bottom: 15px; }}
                .result {{ background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; 
                         font-weight: bold; margin: 5px 0; }}
                .badge-success {{ background: #28a745; color: white; }}
                .badge-danger {{ background: #dc3545; color: white; }}
                .badge-info {{ background: #17a2b8; color: white; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌾 Rapport Feralyx</h1>
                    <p>Analyse Agricole Intelligente</p>
                </div>
        """
        
        # Section Irrigation
        if irrigation_prediction:
            irriguer = irrigation_prediction.get('irriguer', 0)
            badge = 'badge-success' if irriguer == 1 else 'badge-info'
            status = 'IRRIGATION NÉCESSAIRE' if irriguer == 1 else 'PAS D\'IRRIGATION'
            
            body += f"""
                <div class="section">
                    <h3>💧 Irrigation</h3>
                    <div class="result">
                        <span class="badge {badge}">{status}</span>
            """
            
            if irriguer == 1:
                body += f"""
                        <p><strong>Débit :</strong> {irrigation_prediction.get('debit_eau', 0):.2f} L/s</p>
                        <p><strong>Durée :</strong> {irrigation_prediction.get('duree_minutes', 0):.1f} minutes</p>
                """
            
            body += """
                    </div>
                </div>
            """
        
        # Section Maladie
        if disease_diagnosis:
            maladie = disease_diagnosis.get('maladie', 'N/A')
            confiance = disease_diagnosis.get('confiance', 0)
            badge = 'badge-success' if maladie == 'sain' else 'badge-danger'
            
            body += f"""
                <div class="section">
                    <h3>🦠 Diagnostic</h3>
                    <div class="result">
                        <p><strong>État :</strong> <span class="badge {badge}">{maladie.upper().replace('_', ' ')}</span></p>
                        <p><strong>Confiance :</strong> {confiance:.1f}%</p>
                    </div>
                </div>
            """
        
        # Section Export
        if export_recommendation:
            culture = export_recommendation.get('culture_recommandee', 'N/A')
            pays = export_recommendation.get('meilleur_pays_export', 'N/A')
            roi = export_recommendation.get('ROI', 0)
            
            body += f"""
                <div class="section">
                    <h3>🌍 Recommandation d'Export</h3>
                    <div class="result">
                        <p><strong>Culture :</strong> <span class="badge badge-success">{culture.upper()}</span></p>
                        <p><strong>Pays d'export :</strong> {pays}</p>
                        <p><strong>ROI estimé :</strong> {roi:.1f}%</p>
                    </div>
                </div>
            """
        
        body += """
                <div class="footer">
                    <p><strong>📄 Rapport détaillé en pièce jointe</strong></p>
                    <p>Ce rapport a été généré automatiquement par le système Feralyx</p>
                    <p>© 2024 Feralyx - Tous droits réservés</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return body
    
    def test_connection(self):
        """Teste la connexion SMTP"""
        if not self.email or not self.password:
            print("❌ Configuration manquante")
            return False
        
        try:
            print(f"🔍 Test de connexion à {self.smtp_server}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.quit()
            print("✅ Connexion réussie !")
            return True
        except Exception as e:
            print(f"❌ Échec : {str(e)}")
            return False


# Exemple d'utilisation
if __name__ == "__main__":
    print("="*70)
    print("🌾 FERALYX - SYSTÈME D'ENVOI D'EMAILS")
    print("="*70)
    print("\n📧 CONFIGURATION")
    print("Pour utiliser ce module, vous devez configurer vos identifiants email.")
    print("\nPour Gmail:")
    print("1. Activez la validation en 2 étapes")
    print("2. Créez un 'Mot de passe d'application'")
    print("3. Utilisez ce mot de passe (pas votre mot de passe habituel)")
    print("\n" + "="*70)
    
    # Configuration avec VOS identifiants
    sender = EmailSender()
    
    sender.configure(
        provider='gmail',
        email='daoudmohamedali2@gmail.com',
        password='adedmsbpjfpfvbfo'  # Sans espaces
    )
    
    # Test de connexion
    print("\n📡 TEST DE CONNEXION...")
    sender.test_connection()
    
    # Envoi d'un rapport (optionnel - décommentez pour tester)
    print("\n📧 ENVOI D'UN RAPPORT DE TEST...")
    
    # Vérifier si un rapport existe
    reports_dir = 'reports'
    if os.path.exists(reports_dir):
        reports = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
        if reports:
            latest_report = os.path.join(reports_dir, sorted(reports)[-1])
            print(f"   Rapport trouvé : {latest_report}")
            
            sender.send_report(
                recipient_email='daoudmohamedali2@gmail.com',  # Changez si besoin
                report_path=latest_report,
                irrigation_prediction={'irriguer': 1, 'debit_eau': 2.5, 'duree_minutes': 45, 'confiance': 98.5},
                disease_diagnosis={'maladie': 'sain', 'confiance': 95.5},
                export_recommendation={'culture_recommandee': 'tomate', 'meilleur_pays_export': 'France', 'ROI': 45.2}
            )
        else:
            print("   ⚠️ Aucun rapport trouvé. Générez d'abord un rapport avec:")
            print("   python report_generator.py")
    else:
        print("   ⚠️ Dossier 'reports' introuvable. Générez d'abord un rapport avec:")
        print("   python report_generator.py")
    
    print("\n" + "="*70)
    print("✅ Module email opérationnel.")
    print("="*70)