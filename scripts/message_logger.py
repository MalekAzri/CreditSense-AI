"""
Module de logging centralisé pour le suivi des messages.
Enregistre tous les événements de récupération de messages dans logs/fetch.log
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class MessageLogger:
    """Gestionnaire de logs pour les messages de la plateforme de crédit."""
    
    def __init__(self, log_dir=None):
        """
        Initialise le logger.
        
        Args:
            log_dir: Répertoire des logs. Par défaut: ../logs depuis le dossier scripts
        """
        if log_dir is None:
            script_dir = Path(__file__).parent
            self.log_dir = script_dir.parent / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        # Créer le répertoire logs s'il n'existe pas
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurer le logger
        self.logger = logging.getLogger('credit_platform')
        self.logger.setLevel(logging.INFO)
        
        # Éviter les doublons de handlers
        if not self.logger.handlers:
            # Handler pour le fichier fetch.log
            fetch_log_path = self.log_dir / "fetch.log"
            file_handler = logging.FileHandler(fetch_log_path, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Handler pour la console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format des logs
            formatter = logging.Formatter(
                '[%(asctime)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_message(self, source, sender, status, attachments_count=0, error_msg=None, **kwargs):
        """
        Enregistre un message traité.
        
        Args:
            source: Source du message (gmail, whatsapp, bank_platform)
            sender: Expéditeur du message
            status: Statut (success, error, pending)
            attachments_count: Nombre de pièces jointes
            error_msg: Message d'erreur si status=error
            **kwargs: Paramètres additionnels (client_id, subject, etc.)
        """
        # Construire le message de log
        log_parts = [
            f"SOURCE: {source}",
            f"sender: {sender}",
            f"status: {status}",
            f"attachments: {attachments_count}"
        ]
        
        # Ajouter les informations optionnelles
        if kwargs.get('client_id'):
            log_parts.insert(2, f"client_id: {kwargs['client_id']}")
        
        if kwargs.get('subject'):
            log_parts.insert(2, f"subject: {kwargs['subject']}")
        
        if error_msg:
            log_parts.append(f"error: {error_msg}")
        
        # Joindre toutes les parties
        log_message = ", ".join(log_parts)
        
        # Logger selon le statut
        if status == "error":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
    
    def log_fetch_start(self, source, count=None):
        """
        Enregistre le début d'une récupération de messages.
        
        Args:
            source: Source (gmail, whatsapp, bank_platform)
            count: Nombre de messages à traiter (si connu)
        """
        if count is not None:
            msg = f"FETCH_START: {source}, messages_to_process: {count}"
        else:
            msg = f"FETCH_START: {source}"
        
        self.logger.info(msg)
    
    def log_fetch_complete(self, source, success_count, error_count=0, total_time=None):
        """
        Enregistre la fin d'une récupération de messages.
        
        Args:
            source: Source (gmail, whatsapp, bank_platform)
            success_count: Nombre de messages traités avec succès
            error_count: Nombre d'erreurs
            total_time: Temps total en secondes
        """
        log_parts = [
            f"FETCH_COMPLETE: {source}",
            f"success: {success_count}",
            f"errors: {error_count}"
        ]
        
        if total_time is not None:
            log_parts.append(f"duration: {total_time:.2f}s")
        
        msg = ", ".join(log_parts)
        self.logger.info(msg)
    
    def log_api_call(self, endpoint, status_code, response_time=None):
        """
        Enregistre un appel à l'API FastAPI.
        
        Args:
            endpoint: Endpoint appelé
            status_code: Code de réponse HTTP
            response_time: Temps de réponse en ms
        """
        log_parts = [
            f"API_CALL: {endpoint}",
            f"status: {status_code}"
        ]
        
        if response_time is not None:
            log_parts.append(f"response_time: {response_time}ms")
        
        msg = ", ".join(log_parts)
        
        if status_code >= 400:
            self.logger.error(msg)
        else:
            self.logger.info(msg)
    
    def log_error(self, source, error_type, error_msg, **kwargs):
        """
        Enregistre une erreur générale.
        
        Args:
            source: Source de l'erreur
            error_type: Type d'erreur (auth_error, download_error, etc.)
            error_msg: Message d'erreur
            **kwargs: Informations additionnelles
        """
        log_parts = [
            f"ERROR: {source}",
            f"type: {error_type}",
            f"message: {error_msg}"
        ]
        
        for key, value in kwargs.items():
            log_parts.append(f"{key}: {value}")
        
        msg = ", ".join(log_parts)
        self.logger.error(msg)


# Instance globale du logger
message_logger = MessageLogger()


def log_message(source, sender, status, attachments_count=0, **kwargs):
    """
    Fonction helper pour logger rapidement un message.
    
    Args:
        source: Source du message
        sender: Expéditeur
        status: Statut
        attachments_count: Nombre de pièces jointes
        **kwargs: Paramètres additionnels
    """
    message_logger.log_message(source, sender, status, attachments_count, **kwargs)


def log_fetch_start(source, count=None):
    """Fonction helper pour logger le début d'un fetch."""
    message_logger.log_fetch_start(source, count)


def log_fetch_complete(source, success_count, error_count=0, total_time=None):
    """Fonction helper pour logger la fin d'un fetch."""
    message_logger.log_fetch_complete(source, success_count, error_count, total_time)


if __name__ == "__main__":
    # Test du module
    print("🧪 Test du système de logging...")
    
    logger = MessageLogger()
    
    # Simuler quelques logs
    logger.log_fetch_start("gmail", count=3)
    
    logger.log_message(
        source="gmail",
        sender="client@example.com",
        status="success",
        attachments_count=2,
        subject="Demande de crédit",
        client_id="CLIENT001"
    )
    
    logger.log_message(
        source="whatsapp",
        sender="+212600000000",
        status="success",
        attachments_count=1
    )
    
    logger.log_message(
        source="bank_platform",
        sender="system",
        status="error",
        attachments_count=0,
        error_msg="Connection timeout"
    )
    
    logger.log_fetch_complete("gmail", success_count=2, error_count=1, total_time=5.23)
    
    print(f"\n✅ Logs créés dans: {logger.log_dir / 'fetch.log'}")
    print("✅ Module message_logger opérationnel!")
