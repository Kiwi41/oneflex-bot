#!/usr/bin/env python3
"""
Script automatisé pour récupérer les tokens OneFlex via Selenium
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_oneflex_tokens(headless=False):
    """
    Ouvre le navigateur, se connecte à OneFlex et récupère les tokens
    
    Args:
        headless: Si True, le navigateur s'ouvre en mode invisible
    
    Returns:
        dict: {'access_token': str, 'refresh_token': str}
    """
    print("🚀 Démarrage du navigateur automatisé...\n")
    
    # Configuration du navigateur
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Initialiser le driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print("📱 Ouverture de OneFlex...")
        driver.get('https://oneflex.myworldline.com')
        
        print("⏳ En attente de la connexion SSO...")
        print("   👉 Veuillez vous connecter manuellement dans le navigateur\n")
        
        # Attendre que l'utilisateur se connecte (jusqu'à 5 minutes)
        wait = WebDriverWait(driver, 300)
        
        # Attendre que les cookies soient présents
        print("⏳ En attente des tokens...")
        for i in range(60):
            cookies = driver.get_cookies()
            access_token = None
            refresh_token = None
            
            for cookie in cookies:
                if cookie['name'] == 'access_token':
                    access_token = cookie['value']
                elif cookie['name'] == 'refresh_token':
                    refresh_token = cookie['value']
            
            if access_token and refresh_token:
                print("\n✅ Tokens récupérés avec succès !\n")
                
                # Sauvegarder la session pour réutilisation future
                try:
                    from session_manager import SessionManager
                    session_manager = SessionManager()
                    all_cookies = driver.get_cookies()
                    if session_manager.save_cookies(all_cookies):
                        print("💾 Session sauvegardée pour rafraîchissement automatique\n")
                except Exception as e:
                    print(f"⚠️ Avertissement : impossible de sauvegarder la session: {e}\n")
                
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("🔑 ACCESS TOKEN:")
                print(access_token)
                print("\n🔄 REFRESH TOKEN:")
                print(refresh_token)
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                
                # Proposer de mettre à jour le .env
                update = input("📝 Voulez-vous mettre à jour le fichier .env automatiquement ? (o/N) : ")
                if update.lower() in ['o', 'oui', 'y', 'yes']:
                    update_env_file(access_token, refresh_token)
                else:
                    print("\n✅ Copiez ces lignes dans votre .env :")
                    print(f"ONEFLEX_TOKEN={access_token}")
                    print(f"ONEFLEX_REFRESH_TOKEN={refresh_token}")
                
                driver.quit()
                return {'access_token': access_token, 'refresh_token': refresh_token}
            
            time.sleep(5)
        
        print("❌ Timeout : les tokens n'ont pas été trouvés après 5 minutes")
        print("   Assurez-vous d'être bien connecté sur OneFlex")
        driver.quit()
        return None
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        if 'driver' in locals():
            driver.quit()
        return None


def update_env_file(access_token, refresh_token):
    """Met à jour le fichier .env avec les nouveaux tokens"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Fichier .env non trouvé : {env_path}")
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Mettre à jour les tokens
        updated = False
        refresh_updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('ONEFLEX_TOKEN='):
                lines[i] = f'ONEFLEX_TOKEN={access_token}\n'
                updated = True
            elif line.startswith('ONEFLEX_REFRESH_TOKEN='):
                lines[i] = f'ONEFLEX_REFRESH_TOKEN={refresh_token}\n'
                refresh_updated = True
        
        # Ajouter si non trouvé
        if not updated:
            lines.append(f'ONEFLEX_TOKEN={access_token}\n')
        if not refresh_updated:
            lines.append(f'ONEFLEX_REFRESH_TOKEN={refresh_token}\n')
        
        # Sauvegarder
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Fichier .env mis à jour : {env_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du .env : {e}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           RÉCUPÉRATION AUTOMATIQUE DES TOKENS ONEFLEX                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Ce script va :
1. Ouvrir un navigateur Chrome automatisé
2. Charger OneFlex
3. Attendre que vous vous connectiez via SSO
4. Récupérer automatiquement les tokens depuis les cookies
5. Optionnellement mettre à jour votre .env

⚠️  PRÉREQUIS :
   • Chrome ou Chromium installé
   • selenium installé : pip install selenium

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    input("Appuyez sur Entrée pour démarrer...")
    
    tokens = get_oneflex_tokens(headless=False)
    
    if tokens:
        print("\n✅ Processus terminé avec succès !")
    else:
        print("\n❌ Échec de la récupération des tokens")
        print("   Vous pouvez toujours les récupérer manuellement via les DevTools")


if __name__ == '__main__':
    main()
