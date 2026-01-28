"""
Module de notification pour alertes OneFlex
"""
import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Service de notifications pour alerter en cas de problème"""
    
    def __init__(self):
        self.webhook_url = os.getenv('NOTIFICATION_WEBHOOK_URL')
        self.email_enabled = os.getenv('NOTIFICATION_EMAIL_ENABLED', 'false').lower() == 'true'
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        
        # Support Docker secrets pour le mot de passe
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        password_file = os.getenv('SMTP_PASSWORD_FILE')
        if not self.smtp_password and password_file and os.path.exists(password_file):
            with open(password_file, 'r') as f:
                self.smtp_password = f.read().strip()
        
        self.email_to = os.getenv('NOTIFICATION_EMAIL_TO')
    
    def send_token_expired_alert(self, error_message: str):
        """Envoie une alerte quand le token ne peut plus être rafraîchi"""
        message = f"""
⚠️ ALERTE ONEFLEX BOT ⚠️

Le token d'authentification a expiré et ne peut plus être rafraîchi.

Détails:
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Erreur: {error_message}

Actions requises:
1. Récupérez un nouveau token via: python auto_get_tokens.py
2. Mettez à jour votre fichier .env
3. Redémarrez le bot

Documentation: https://github.com/Kiwi41/oneflex-bot/blob/main/docs/TOKEN_MANAGEMENT.md
"""
        
        # Envoyer via webhook (Discord, Slack, etc.)
        if self.webhook_url:
            self._send_webhook(message)
        
        # Envoyer par email
        if self.email_enabled and self.email_to:
            self._send_email("🚨 OneFlex Bot - Token expiré", message)
    
    def send_booking_success(self, count: int, weeks: int = 1):
        """Notification de succès de réservation"""
        message = f"""
✅ OneFlex Bot - Réservations effectuées

- {count} réservation(s) créée(s) avec succès
- Période: {weeks} semaine(s)
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        logger.info(message)
        
        if self.webhook_url:
            self._send_webhook(message, is_success=True)
    
    def send_booking_failure(self, error_message: str):
        """Notification d'échec de réservation"""
        message = f"""
❌ OneFlex Bot - Échec de réservation

Erreur: {error_message}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Vérifiez les logs pour plus de détails.
"""
        logger.error(message)
        
        if self.webhook_url:
            self._send_webhook(message, is_error=True)
    
    def _send_webhook(self, message: str, is_success: bool = False, is_error: bool = False):
        """Envoie une notification via webhook"""
        try:
            # Format Discord/Slack
            color = 0x00FF00 if is_success else (0xFF0000 if is_error else 0xFFA500)
            
            payload = {
                "embeds": [{
                    "title": "OneFlex Bot Notification",
                    "description": message,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204 or response.status_code == 200:
                logger.debug("Notification webhook envoyée avec succès")
            else:
                logger.warning(f"Échec envoi webhook: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"Erreur lors de l'envoi du webhook: {e}")
    
    def _send_email(self, subject: str, body: str):
        """Envoie une notification par email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.email_to]):
                logger.debug("Configuration email incomplète, email non envoyé")
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email envoyé à {self.email_to}")
        
        except Exception as e:
            logger.warning(f"Erreur lors de l'envoi de l'email: {e}")


# Instance globale
notification_service = NotificationService()
