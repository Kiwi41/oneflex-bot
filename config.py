"""
Configuration du bot OneFlex
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger .env depuis config/ ou depuis le répertoire courant
env_path = Path(__file__).parent / 'config' / '.env'
if not env_path.exists():
    env_path = Path('.env')
load_dotenv(env_path)


class Config:
    """Configuration chargée depuis les variables d'environnement"""
    
    # Credentials OneFlex
    EMAIL = os.getenv('ONEFLEX_EMAIL')
    PASSWORD = os.getenv('ONEFLEX_PASSWORD')
    TOKEN = os.getenv('ONEFLEX_TOKEN')  # Pour SSO
    REFRESH_TOKEN = os.getenv('ONEFLEX_REFRESH_TOKEN')  # Pour rafraîchir le token
    
    # IDs optionnels pour filtrer
    SITE_ID = os.getenv('ONEFLEX_SITE_ID')
    FLOOR_ID = os.getenv('ONEFLEX_FLOOR_ID')
    ZONE_ID = os.getenv('ONEFLEX_ZONE_ID')
    
    # Paramètres de réservation
    RESERVATION_TIME = os.getenv('RESERVATION_TIME', '09:00')
    RESERVATION_DAYS_AHEAD = int(os.getenv('RESERVATION_DAYS_AHEAD', 7))
    RESERVATION_DAYS_OF_WEEK = os.getenv('RESERVATION_DAYS_OF_WEEK', '')  # Ex: 1,3,5 pour Lundi, Mercredi, Vendredi
    RECURRING_WEEKS = int(os.getenv('RECURRING_WEEKS', 0))  # Nombre de semaines pour les réservations récurrentes
    
    # Gestion des vacances/absences
    VACATION_DATES = os.getenv('VACATION_DATES', '')  # Format: 2026-02-10:2026-02-14,2026-03-01:2026-03-07
    AUTO_CANCEL_VACATIONS = os.getenv('AUTO_CANCEL_VACATIONS', 'true').lower() == 'true'
    
    # Désactiver la validation (utile pour tester le container sans credentials)
    SKIP_VALIDATION = os.getenv('SKIP_VALIDATION', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Valide que la configuration minimale est présente"""
        if cls.SKIP_VALIDATION:
            return True
        if not cls.TOKEN and (not cls.EMAIL or not cls.PASSWORD):
            raise ValueError("TOKEN ou (EMAIL + PASSWORD) sont requis dans le fichier .env")
        return True
