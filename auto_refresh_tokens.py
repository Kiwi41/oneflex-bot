#!/usr/bin/env python3
"""
Script automatisé pour rafraîchir les tokens OneFlex via Selenium (headless)
Utilise les credentials stockés dans .env pour se connecter automatiquement
"""
import time
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger .env depuis config/ ou depuis le répertoire courant
env_path = Path(__file__).parent / 'config' / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ Selenium non installé. Installez-le avec: pip install selenium")
    sys.exit(1)


def auto_refresh_tokens(sso_email: str, sso_password: str, headless: bool = True, timeout: int = 60) -> dict:
    """
    Se connecte automatiquement à OneFlex via SSO et récupère les tokens
    
    Args:
        sso_email: Email pour l'authentification SSO
        sso_password: Mot de passe pour l'authentification SSO
        headless: Si True, le navigateur s'ouvre en mode invisible
        timeout: Temps d'attente maximum en secondes
    
    Returns:
        dict: {'access_token': str, 'refresh_token': str} ou None si échec
    """
    # Configuration du navigateur
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        # Initialiser le driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        
        # Ouvrir OneFlex
        driver.get('https://oneflex.myworldline.com')
        
        # Attendre le bouton de connexion SSO
        wait = WebDriverWait(driver, timeout)
        
        # Cliquer sur "Se connecter" si présent
        try:
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Se connecter') or contains(., 'Login')]"))
            )
            login_button.click()
            time.sleep(2)
        except TimeoutException:
            # Déjà sur la page SSO ou déjà connecté
            pass
        
        # Remplir le formulaire SSO (adapté à votre SSO Worldline)
        # ATTENTION: Ces sélecteurs peuvent varier selon votre SSO
        try:
            # Attendre le champ email
            email_field = wait.until(EC.presence_of_element_located((By.ID, "i0116")))
            email_field.clear()
            email_field.send_keys(sso_email)
            
            # Cliquer sur "Suivant"
            next_button = driver.find_element(By.ID, "idSIButton9")
            next_button.click()
            time.sleep(2)
            
            # Attendre le champ mot de passe
            password_field = wait.until(EC.presence_of_element_located((By.ID, "i0118")))
            password_field.clear()
            password_field.send_keys(sso_password)
            
            # Cliquer sur "Se connecter"
            signin_button = driver.find_element(By.ID, "idSIButton9")
            signin_button.click()
            time.sleep(2)
            
            # Gérer "Rester connecté?" si présent
            try:
                stay_signed_in = driver.find_element(By.ID, "idSIButton9")
                stay_signed_in.click()
            except NoSuchElementException:
                pass
            
        except (TimeoutException, NoSuchElementException) as e:
            # Tentative avec des sélecteurs génériques
            try:
                email_field = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']"))
                )
                email_field.clear()
                email_field.send_keys(sso_email)
                
                password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                password_field.send_keys(sso_password)
                
                # Trouver le bouton submit
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                submit_button.click()
                time.sleep(3)
            except Exception:
                print(f"❌ Impossible de trouver les champs du formulaire SSO")
                return None
        
        # Attendre que les cookies soient présents
        for i in range(30):
            cookies = driver.get_cookies()
            access_token = None
            refresh_token = None
            
            for cookie in cookies:
                if cookie['name'] == 'access_token':
                    access_token = cookie['value']
                elif cookie['name'] == 'refresh_token':
                    refresh_token = cookie['value']
            
            if access_token and refresh_token:
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            
            time.sleep(2)
        
        print("❌ Timeout: tokens non récupérés après authentification")
        return None
        
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification automatique: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()


def update_env_file(access_token: str, refresh_token: str):
    """
    Met à jour le fichier .env avec les nouveaux tokens
    
    Args:
        access_token: Le nouveau access token
        refresh_token: Le nouveau refresh token
    """
    env_path = Path(__file__).parent / 'config' / '.env'
    if not env_path.exists():
        env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"❌ Fichier .env introuvable")
        return
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        token_updated = False
        refresh_updated = False
        
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('ONEFLEX_TOKEN='):
                    f.write(f'ONEFLEX_TOKEN={access_token}\n')
                    token_updated = True
                elif line.startswith('ONEFLEX_REFRESH_TOKEN='):
                    f.write(f'ONEFLEX_REFRESH_TOKEN={refresh_token}\n')
                    refresh_updated = True
                else:
                    f.write(line)
            
            # Ajouter les lignes si elles n'existaient pas
            if not token_updated:
                f.write(f'\nONEFLEX_TOKEN={access_token}\n')
            if not refresh_updated:
                f.write(f'ONEFLEX_REFRESH_TOKEN={refresh_token}\n')
        
        print(f"✅ Fichier .env mis à jour : {env_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du .env: {e}")


def main():
    """Point d'entrée principal"""
    print("\n" + "="*80)
    print("RAFRAÎCHISSEMENT AUTOMATIQUE DES TOKENS ONEFLEX")
    print("="*80 + "\n")
    
    # Récupérer les credentials depuis .env
    sso_email = os.getenv('SSO_EMAIL')
    sso_password = os.getenv('SSO_PASSWORD')
    
    if not sso_email or not sso_password:
        print("❌ SSO_EMAIL et SSO_PASSWORD doivent être définis dans .env")
        print("\nAjoutez ces lignes à votre .env :")
        print("SSO_EMAIL=votre.email@worldline.com")
        print("SSO_PASSWORD=votre_mot_de_passe")
        sys.exit(1)
    
    print(f"🔐 Authentification SSO avec: {sso_email}")
    print("⏳ Connexion en cours...\n")
    
    # Récupérer les tokens automatiquement
    result = auto_refresh_tokens(sso_email, sso_password, headless=True)
    
    if result:
        print("✅ Tokens récupérés avec succès !\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🔑 ACCESS TOKEN: {result['access_token'][:50]}...")
        print(f"🔄 REFRESH TOKEN: {result['refresh_token']}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Mettre à jour le .env
        update_env_file(result['access_token'], result['refresh_token'])
        
        print("\n✅ Processus terminé avec succès !")
    else:
        print("\n❌ Échec de la récupération des tokens")
        print("\n💡 Vérifiez :")
        print("   • Les credentials SSO_EMAIL et SSO_PASSWORD dans .env")
        print("   • Que Chrome/Chromium est installé")
        print("   • Les logs ci-dessus pour plus de détails")
        sys.exit(1)


if __name__ == "__main__":
    main()
