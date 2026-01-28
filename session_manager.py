#!/usr/bin/env python3
"""
Gestionnaire de session persistante pour OneFlex
Sauvegarde et réutilise les cookies de session pour éviter la ré-authentification
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Gère la persistance de la session OneFlex via les cookies"""
    
    def __init__(self, session_file: str = "config/session.json"):
        """
        Initialise le gestionnaire de session
        
        Args:
            session_file: Chemin vers le fichier de session
        """
        self.session_file = Path(__file__).parent / session_file
        self.session_file.parent.mkdir(exist_ok=True)
    
    def save_cookies(self, cookies: list) -> bool:
        """
        Sauvegarde les cookies de session
        
        Args:
            cookies: Liste des cookies Selenium/navigateur
            
        Returns:
            bool: True si sauvegarde réussie
        """
        try:
            # Filtrer les cookies importants
            important_cookies = []
            for cookie in cookies:
                # Sauvegarder tous les cookies du domaine oneflex
                if 'myworldline.com' in cookie.get('domain', ''):
                    important_cookies.append({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain'),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False),
                        'httpOnly': cookie.get('httpOnly', False),
                        'expiry': cookie.get('expiry')
                    })
            
            # Sauvegarder dans le fichier
            import time
            with open(self.session_file, 'w') as f:
                json.dump({
                    'cookies': important_cookies,
                    'timestamp': time.time()
                }, f, indent=2)
            
            logger.info(f"💾 Session sauvegardée : {len(important_cookies)} cookies")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde de la session: {e}")
            return False
    
    def load_cookies(self) -> Optional[list]:
        """
        Charge les cookies de session sauvegardés
        
        Returns:
            Liste des cookies ou None si aucune session
        """
        try:
            if not self.session_file.exists():
                logger.warning("⚠️ Aucune session sauvegardée trouvée")
                return None
            
            with open(self.session_file, 'r') as f:
                data = json.load(f)
            
            cookies = data.get('cookies', [])
            logger.info(f"📂 Session chargée : {len(cookies)} cookies")
            return cookies
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de la session: {e}")
            return None
    
    def session_exists(self) -> bool:
        """
        Vérifie si une session sauvegardée existe
        
        Returns:
            bool: True si une session existe
        """
        return self.session_file.exists()
    
    def clear_session(self) -> bool:
        """
        Supprime la session sauvegardée
        
        Returns:
            bool: True si suppression réussie
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                logger.info("🗑️ Session supprimée")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression de la session: {e}")
            return False


def refresh_tokens_from_session(headless: bool = True, timeout: int = 30) -> Optional[Dict[str, str]]:
    """
    Récupère de nouveaux tokens en utilisant une session sauvegardée
    
    Args:
        headless: Mode headless du navigateur
        timeout: Timeout en secondes
        
    Returns:
        Dict avec access_token et refresh_token, ou None si échec
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time
    except ImportError:
        logger.error("❌ Selenium non installé")
        return None
    
    session_manager = SessionManager()
    
    # Vérifier si une session existe
    if not session_manager.session_exists():
        logger.warning("⚠️ Aucune session sauvegardée. Lancez d'abord auto_get_tokens.py")
        return None
    
    # Charger les cookies sauvegardés
    saved_cookies = session_manager.load_cookies()
    if not saved_cookies:
        return None
    
    # Configuration du navigateur
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        
        # Ouvrir OneFlex
        logger.info("🌐 Ouverture de OneFlex avec session sauvegardée...")
        driver.get('https://oneflex.myworldline.com')
        time.sleep(2)
        
        # Restaurer les cookies
        logger.info("🔄 Restauration des cookies de session...")
        for cookie in saved_cookies:
            try:
                # Supprimer les champs qui peuvent causer des problèmes
                cookie_to_add = {k: v for k, v in cookie.items() if k not in ['expiry', 'sameSite']}
                driver.add_cookie(cookie_to_add)
            except Exception as e:
                logger.debug(f"Cookie ignoré: {e}")
        
        # Recharger la page avec les cookies
        driver.get('https://oneflex.myworldline.com')
        time.sleep(5)  # Attendre que la page charge et rafraîchisse les tokens
        
        # Récupérer les nouveaux tokens après le refresh automatique
        logger.info("🔍 Récupération des tokens...")
        
        # Essayer d'abord le localStorage/sessionStorage (plus courant pour les SPAs)
        try:
            access_token = driver.execute_script("return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');")
            refresh_token = driver.execute_script("return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');")
            
            if access_token and refresh_token:
                logger.info("✅ Tokens récupérés depuis localStorage/sessionStorage")
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
        except Exception as e:
            logger.debug(f"Pas de tokens dans localStorage/sessionStorage: {e}")
        
        # Sinon, essayer les cookies
        for i in range(15):  # Augmenter le nombre de tentatives
            cookies = driver.get_cookies()
            access_token = None
            refresh_token = None
            
            for cookie in cookies:
                if cookie['name'] == 'access_token':
                    access_token = cookie['value']
                elif cookie['name'] == 'refresh_token':
                    refresh_token = cookie['value']
            
            if access_token and refresh_token:
                # Vérifier que le token n'est pas expiré en décodant le JWT
                import json
                import base64
                try:
                    # Décoder le payload du JWT (partie du milieu)
                    payload = access_token.split('.')[1]
                    # Ajouter du padding si nécessaire
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = json.loads(base64.b64decode(payload))
                    exp_time = decoded.get('exp', 0)
                    current_time = time.time()
                    
                    if exp_time > current_time + 60:  # Token valide pour au moins 1 minute
                        logger.info("✅ Tokens récupérés avec succès via session persistante")
                        return {
                            'access_token': access_token,
                            'refresh_token': refresh_token
                        }
                    else:
                        logger.debug(f"Token expiré ou expirant bientôt, attente... ({i+1}/15)")
                except Exception as e:
                    logger.debug(f"Erreur décodage JWT: {e}")
            
            time.sleep(2)  # Attendre plus longtemps entre les tentatives
        
        logger.error("❌ Session expirée ou invalide. Reconnectez-vous avec auto_get_tokens.py")
        # Supprimer la session invalide
        session_manager.clear_session()
        return None
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'utilisation de la session: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()
