#!/usr/bin/env python3
"""
Script de reverse engineering pour découvrir l'endpoint SSO Worldline
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def discover_sso_endpoint():
    """Découvre l'endpoint SSO en analysant les requêtes réseau"""
    
    print("🔍 Démarrage du reverse engineering SSO Worldline...\n")
    
    # Configuration Chrome avec capture des logs réseau
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Activer la capture des logs réseau (nouvelle syntaxe Selenium 4+)
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("�� Navigation vers OneFlex...")
        driver.get("https://oneflex.myworldline.com")
        time.sleep(3)
        
        # Récupérer les logs de performance
        logs = driver.get_log('performance')
        
        print(f"\n📊 Analyse de {len(logs)} événements réseau...\n")
        
        # URLs SSO découvertes
        sso_urls = set()
        oauth_endpoints = []
        
        import json
        for entry in logs:
            try:
                log = json.loads(entry['message'])
                message = log.get('message', {})
                
                if message.get('method') in ['Network.requestWillBeSent', 'Network.responseReceived']:
                    params = message.get('params', {})
                    
                    # Requête
                    if 'request' in params:
                        url = params['request'].get('url', '')
                        method = params['request'].get('method', '')
                        
                        # Chercher les URLs SSO/OAuth
                        if any(keyword in url.lower() for keyword in ['oauth', 'sso', 'auth', 'login', 'token', 'worldline']):
                            sso_urls.add(url)
                            
                            # Si c'est un POST, capturer les détails
                            if method == 'POST':
                                headers = params['request'].get('headers', {})
                                post_data = params['request'].get('postData', '')
                                oauth_endpoints.append({
                                    'url': url,
                                    'method': method,
                                    'headers': headers,
                                    'body': post_data
                                })
                    
                    # Réponse
                    if 'response' in params:
                        url = params['response'].get('url', '')
                        if any(keyword in url.lower() for keyword in ['oauth', 'sso', 'auth', 'token']):
                            sso_urls.add(url)
                            
            except Exception as e:
                continue
        
        # Afficher les découvertes
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🌐 URLs SSO/OAuth découvertes:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for url in sorted(sso_urls):
            print(f"  • {url}")
        
        if oauth_endpoints:
            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🔑 Endpoints OAuth POST détectés:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for endpoint in oauth_endpoints:
                print(f"\n📍 URL: {endpoint['url']}")
                print(f"   Method: {endpoint['method']}")
                if endpoint.get('body'):
                    print(f"   Body: {endpoint['body'][:200]}...")
        
        # Analyser les cookies
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🍪 Cookies SSO:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        cookies = driver.get_cookies()
        for cookie in cookies:
            if any(keyword in cookie['name'].lower() for keyword in ['token', 'auth', 'session', 'sso']):
                print(f"  • {cookie['name']}: {cookie['value'][:50]}... (domain: {cookie['domain']})")
        
        # Analyser le DOM pour trouver des infos
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 Analyse du DOM pour config OAuth:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Chercher dans le JavaScript global
        js_config = driver.execute_script("""
            // Chercher des configs OAuth/SSO dans window
            let configs = [];
            
            // Patterns communs
            const patterns = ['oauth', 'sso', 'auth', 'client_id', 'token_endpoint'];
            
            // Scanner window
            for (let key in window) {
                try {
                    let value = window[key];
                    if (typeof value === 'object' && value !== null) {
                        let str = JSON.stringify(value).toLowerCase();
                        for (let pattern of patterns) {
                            if (str.includes(pattern)) {
                                configs.push({key: key, value: value});
                                break;
                            }
                        }
                    }
                } catch(e) {}
            }
            
            return configs;
        """)
        
        if js_config:
            for config in js_config[:5]:  # Limiter à 5 résultats
                print(f"  • window.{config['key']}: {str(config['value'])[:200]}...")
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ Analyse terminée!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        input("\n⏸️  Appuyez sur Entrée pour fermer le navigateur...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    discover_sso_endpoint()
