"""
Configuration du bot OneFlex

Ce module charge toutes les variables de configuration depuis le fichier .env
Les variables d'environnement permettent de configurer le bot sans modifier le code
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHARGEMENT DU FICHIER .ENV
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Le fichier .env contient toutes les configurations sensibles (tokens, horaires, etc.)
# On cherche d'abord dans le dossier config/ (utilisé par Docker), sinon dans le dossier courant

env_path = Path(__file__).parent / 'config' / '.env'  # Chemin pour Docker
if not env_path.exists():
    env_path = Path('.env')  # Chemin pour exécution locale
load_dotenv(env_path)  # Charge les variables d'environnement depuis le fichier


class Config:
    """
    Classe de configuration centralisée
    
    Toutes les variables sont chargées depuis le fichier .env au démarrage.
    Cette approche permet de modifier la configuration sans toucher au code.
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUTHENTIFICATION ONEFLEX
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OneFlex utilise un système SSO (Single Sign-On) avec tokens
    # Les tokens expirent après 15 minutes et doivent être renouvelés manuellement
    
    EMAIL = os.getenv('ONEFLEX_EMAIL')  # Email OneFlex (non utilisé avec SSO)
    PASSWORD = os.getenv('ONEFLEX_PASSWORD')  # Mot de passe (non utilisé avec SSO)
    TOKEN = os.getenv('ONEFLEX_TOKEN')  # Token d'accès SSO (obligatoire)
    REFRESH_TOKEN = os.getenv('ONEFLEX_REFRESH_TOKEN')  # Token de rafraîchissement (stocké mais non utilisé)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FILTRES OPTIONNELS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Permettent de cibler un site/étage/zone spécifique (généralement pas nécessaire)
    
    SITE_ID = os.getenv('ONEFLEX_SITE_ID')  # ID du site (ex: "site-123")
    FLOOR_ID = os.getenv('ONEFLEX_FLOOR_ID')  # ID de l'étage (ex: "floor-456")
    ZONE_ID = os.getenv('ONEFLEX_ZONE_ID')  # ID de la zone (ex: "zone-789")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PARAMÈTRES DE RÉSERVATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Heure d'exécution quotidienne du bot (format HH:MM)
    # Exemple: "03:05" = le bot s'exécutera chaque jour à 3h05 du matin
    RESERVATION_TIME = os.getenv('RESERVATION_TIME', '09:00')
    
    # Nombre de jours à l'avance pour réserver (par défaut 7 jours)
    # Exemple: si RESERVATION_DAYS_AHEAD=28, réserve 28 jours à l'avance
    RESERVATION_DAYS_AHEAD = int(os.getenv('RESERVATION_DAYS_AHEAD', 7))
    
    # Jours de la semaine où réserver (1=Lundi, 2=Mardi, ..., 7=Dimanche)
    # Exemple: "1,2,3,4,5" = du lundi au vendredi
    RESERVATION_DAYS_OF_WEEK = os.getenv('RESERVATION_DAYS_OF_WEEK', '')
    
    # Nombre de semaines à réserver à l'avance en mode récurrent
    # Exemple: RECURRING_WEEKS=4 = réserve 4 semaines complètes d'avance
    # Si 0, le mode récurrent est désactivé
    RECURRING_WEEKS = int(os.getenv('RECURRING_WEEKS', 0))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GESTION DES VACANCES / ABSENCES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Périodes de vacances où ne PAS réserver
    # Format: "YYYY-MM-DD:YYYY-MM-DD,YYYY-MM-DD" (plages ou dates uniques séparées par des virgules)
    # Exemple: "2026-02-10:2026-02-14,2026-03-01" = vacances du 10 au 14 fév + 1er mars
    VACATION_DATES = os.getenv('VACATION_DATES', '')
    
    # Annuler automatiquement les réservations existantes pendant les vacances
    AUTO_CANCEL_VACATIONS = os.getenv('AUTO_CANCEL_VACATIONS', 'true').lower() == 'true'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # NOTIFICATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # URL du webhook Discord pour recevoir les notifications
    NOTIFICATION_WEBHOOK_URL = os.getenv('NOTIFICATION_WEBHOOK_URL', '')
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OPTIONS AVANCÉES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Désactiver la validation des credentials (utile pour tester le container)
    SKIP_VALIDATION = os.getenv('SKIP_VALIDATION', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """
        Vérifie que la configuration minimale est présente
        
        Pour que le bot fonctionne, il faut AU MINIMUM:
        - Soit un TOKEN (pour SSO)
        - Soit un EMAIL + PASSWORD (pour connexion classique)
        
        Returns:
            True si la configuration est valide
            
        Raises:
            ValueError: Si la configuration est incomplète
        """
        # Si la validation est désactivée, tout est OK
        if cls.SKIP_VALIDATION:
            return True
        
        # Vérifier qu'on a au moins TOKEN ou (EMAIL + PASSWORD)
        if not cls.TOKEN and (not cls.EMAIL or not cls.PASSWORD):
            raise ValueError(
                "❌ Configuration incomplète!\n"
                "Il faut définir dans .env:\n"
                "  - Soit ONEFLEX_TOKEN (pour SSO)\n"
                "  - Soit ONEFLEX_EMAIL + ONEFLEX_PASSWORD"
            )
        return True
