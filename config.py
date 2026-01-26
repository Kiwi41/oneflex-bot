"""
Configuration du bot OneFlex
"""
import os
from dotenv import load_dotenv

load_dotenv()


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
    
    @classmethod
    def validate(cls):
        """Valide que la configuration minimale est présente"""
        if not cls.TOKEN and (not cls.EMAIL or not cls.PASSWORD):
            raise ValueError("TOKEN ou (EMAIL + PASSWORD) sont requis dans le fichier .env")
        return True
        return True
