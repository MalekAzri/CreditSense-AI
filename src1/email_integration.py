"""
MODULE D'INTÉGRATION EMAIL - CreditSense AI
============================================

Ce module montre comment le système s'intègre réellement avec une boîte email
pour automatiser la lecture, l'analyse et la réponse aux emails clients.

PRÉREQUIS :
-----------
1. Activer l'accès IMAP dans Gmail (Paramètres > Transfert et POP/IMAP)
2. Créer un mot de passe d'application (si 2FA activé)
3. Installer les dépendances : pip install secure-smtplib

FLUX COMPLET :
--------------
Email reçu → Lecture IMAP → Classification ML → Extraction info client 
→ Recherche BDD → Génération réponse → Envoi SMTP → Marquage traité
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import logging
from datetime import datetime
from agent_logic import CreditSenseAgent
import re

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_automation.log'),
        logging.StreamHandler()
    ]
)

class EmailAutomationSystem:
    """
    Système complet d'automatisation des emails pour CreditSense
    """
    
    def __init__(self, email_address, password, imap_server='imap.gmail.com', smtp_server='smtp.gmail.com'):
        """
        Initialisation du système
        
        Args:
            email_address: Adresse email du compte de service
            password: Mot de passe d'application
            imap_server: Serveur IMAP (défaut: Gmail)
            smtp_server: Serveur SMTP (défaut: Gmail)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        
        # Initialiser l'agent IA
        self.agent = CreditSenseAgent()
        
        logging.info("✅ Système d'automatisation initialisé")
    
    # ========================================================================
    # PHASE 1 : CONNEXION À LA BOÎTE EMAIL
    # ========================================================================
    
    def connect_imap(self):
        """
        ÉTAPE 1 : Connexion au serveur IMAP pour lire les emails
        """
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            logging.info(f"✅ Connecté à {self.imap_server}")
            return True
        except Exception as e:
            logging.error(f"❌ Erreur de connexion IMAP : {e}")
            return False
    
    # ========================================================================
    # PHASE 2 : RÉCUPÉRATION DES EMAILS NON TRAITÉS
    # ========================================================================
    
    def fetch_unread_emails(self):
        """
        ÉTAPE 2 : Récupérer tous les emails non lus de la boîte de réception
        
        Returns:
            Liste de tuples (email_id, email_object)
        """
        try:
            # Sélectionner la boîte de réception
            self.mail.select('INBOX')
            
            # Chercher les emails non lus
            status, messages = self.mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                logging.warning("Aucun email non lu trouvé")
                return []
            
            email_ids = messages[0].split()
            logging.info(f"📧 {len(email_ids)} email(s) non lu(s) trouvé(s)")
            
            emails = []
            for email_id in email_ids:
                # Récupérer l'email complet
                status, data = self.mail.fetch(email_id, '(RFC822)')
                
                if status == 'OK':
                    # Parser l'email
                    msg = email.message_from_bytes(data[0][1])
                    emails.append((email_id, msg))
            
            return emails
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des emails : {e}")
            return []
    
    # ========================================================================
    # PHASE 3 : EXTRACTION DU CONTENU DE L'EMAIL
    # ========================================================================
    
    def extract_email_content(self, msg):
        """
        ÉTAPE 3 : Extraire les informations importantes de l'email
        
        Args:
            msg: Objet email
            
        Returns:
            dict avec from, subject, body
        """
        # Extraire l'expéditeur
        from_header = msg.get('From', '')
        # Extraire juste l'adresse email
        from_match = re.search(r'[\w\.-]+@[\w\.-]+', from_header)
        from_email = from_match.group(0) if from_match else from_header
        
        # Extraire le sujet
        subject = msg.get('Subject', 'Sans sujet')
        
        # Extraire le corps de l'email
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return {
            'from': from_email,
            'subject': subject,
            'body': body.strip()
        }
    
    # ========================================================================
    # PHASE 4 : TRAITEMENT INTELLIGENT AVEC IA
    # ========================================================================
    
    def process_with_ai(self, email_content):
        """
        ÉTAPE 4 : Analyser l'email avec le modèle ML et générer une réponse
        
        Cette étape utilise votre agent_logic.py qui :
        - Classifie l'intention (status_request, document_request, etc.)
        - Extrait les infos client (email, numéro de dossier)
        - Recherche dans la base de données clients
        - Génère une réponse personnalisée
        
        Args:
            email_content: dict avec from, subject, body
            
        Returns:
            str: Réponse générée par l'IA
        """
        logging.info(f"🤖 Analyse IA de l'email de {email_content['from']}")
        
        # Utiliser l'agent IA pour traiter l'email
        response = self.agent.process_email(email_content['body'])
        
        logging.info(f"✅ Réponse générée par l'IA")
        return response
    
    # ========================================================================
    # PHASE 5 : ENVOI DE LA RÉPONSE AUTOMATIQUE
    # ========================================================================
    
    def send_response(self, to_email, subject, response_text):
        """
        ÉTAPE 5 : Envoyer la réponse automatique par email
        
        Args:
            to_email: Adresse du destinataire
            subject: Sujet de la réponse
            response_text: Corps de la réponse
        """
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = f"Re: {subject}"
            
            # Ajouter le corps du message
            msg.attach(MIMEText(response_text, 'plain', 'utf-8'))
            
            # Connexion SMTP et envoi
            with smtplib.SMTP_SSL(self.smtp_server, 465) as smtp:
                smtp.login(self.email_address, self.password)
                smtp.send_message(msg)
            
            logging.info(f"✅ Réponse envoyée à {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi de la réponse : {e}")
            return False
    
    # ========================================================================
    # PHASE 6 : MARQUAGE DE L'EMAIL COMME TRAITÉ
    # ========================================================================
    
    def mark_as_processed(self, email_id):
        """
        ÉTAPE 6 : Marquer l'email comme lu et traité
        
        Args:
            email_id: ID de l'email à marquer
        """
        try:
            # Marquer comme lu
            self.mail.store(email_id, '+FLAGS', '\\Seen')
            
            # Option : Déplacer vers un dossier "Traité" (si le dossier existe)
            # self.mail.copy(email_id, 'Processed')
            
            logging.info(f"✅ Email {email_id.decode()} marqué comme traité")
            
        except Exception as e:
            logging.error(f"❌ Erreur lors du marquage : {e}")
    
    # ========================================================================
    # BOUCLE PRINCIPALE : AUTOMATISATION COMPLÈTE
    # ========================================================================
    
    def run_automation_cycle(self):
        """
        CYCLE COMPLET D'AUTOMATISATION
        
        Cette fonction orchestre toutes les étapes :
        1. Connexion IMAP
        2. Récupération des emails non lus
        3. Pour chaque email :
           a. Extraction du contenu
           b. Traitement IA
           c. Envoi de la réponse
           d. Marquage comme traité
        """
        logging.info("🚀 Démarrage du cycle d'automatisation")
        
        # Étape 1 : Connexion
        if not self.connect_imap():
            return
        
        try:
            # Étape 2 : Récupérer les emails non lus
            emails = self.fetch_unread_emails()
            
            # Étape 3-6 : Traiter chaque email
            for email_id, msg in emails:
                try:
                    # Extraction du contenu
                    email_content = self.extract_email_content(msg)
                    
                    logging.info(f"\n{'='*60}")
                    logging.info(f"📧 Traitement de l'email de : {email_content['from']}")
                    logging.info(f"📋 Sujet : {email_content['subject']}")
                    logging.info(f"{'='*60}")
                    
                    # Traitement IA
                    response = self.process_with_ai(email_content)
                    
                    # Envoi de la réponse
                    if self.send_response(
                        email_content['from'],
                        email_content['subject'],
                        response
                    ):
                        # Marquer comme traité seulement si l'envoi a réussi
                        self.mark_as_processed(email_id)
                    
                except Exception as e:
                    logging.error(f"❌ Erreur lors du traitement de l'email : {e}")
                    continue
            
            logging.info(f"\n✅ Cycle terminé : {len(emails)} email(s) traité(s)")
            
        finally:
            # Déconnexion propre
            self.mail.close()
            self.mail.logout()
            logging.info("🔌 Déconnexion IMAP")
    
    # ========================================================================
    # MODE SURVEILLANCE CONTINUE
    # ========================================================================
    
    def run_continuous_monitoring(self, interval_seconds=60):
        """
        MODE PRODUCTION : Surveillance continue de la boîte email
        
        Args:
            interval_seconds: Intervalle entre chaque vérification (défaut: 60s)
        """
        logging.info(f"🔄 Démarrage de la surveillance continue (intervalle: {interval_seconds}s)")
        logging.info("Appuyez sur Ctrl+C pour arrêter")
        
        try:
            while True:
                self.run_automation_cycle()
                logging.info(f"⏳ Prochaine vérification dans {interval_seconds} secondes...\n")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logging.info("\n🛑 Arrêt de la surveillance demandé par l'utilisateur")


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    """
    CONFIGURATION POUR DÉMARRER LE SYSTÈME
    
    ⚠️ IMPORTANT : Remplacez les valeurs ci-dessous par vos vraies informations
    """
    
    # Configuration email (À PERSONNALISER)
    EMAIL_ADDRESS = "banque.2026@gmail.com"  # Adresse Gmail de la banque
    EMAIL_PASSWORD = "banqueHackathon2026"  # Mot de passe d'application recommandé
    
    # Créer le système
    system = EmailAutomationSystem(EMAIL_ADDRESS, EMAIL_PASSWORD)
    
    # OPTION 1 : Exécuter un seul cycle (pour tester)
    print("Mode : Cycle unique")
    system.run_automation_cycle()
    
    # OPTION 2 : Surveillance continue (pour production)
    # Décommentez les lignes ci-dessous pour activer
    # print("Mode : Surveillance continue")
    # system.run_continuous_monitoring(interval_seconds=60)
