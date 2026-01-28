#!/usr/bin/env python3
"""
Analyse approfondie du mécanisme de refresh OneFlex
Capture toutes les requêtes réseau et cookies
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def analyze_refresh_mechanism():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
    
    print('🔍 Analyse complète du mécanisme de refresh OneFlex\n')
    print('📋 Instructions:')
    print('   1. Connectez-vous normalement')
    print('   2. Attendez que la page OneFlex charge complètement')
    print('   3. Le script va attendre 30 secondes puis analyser\n')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get('https://oneflex.myworldline.com')
        
        print('⏳ Attendez 30 secondes après connexion pour analyse...')
        time.sleep(30)
        
        print('\n' + '='*80)
        print('📊 ANALYSE DES RÉSULTATS')
        print('='*80)
        
        # 1. Cookies
        print('\n🍪 TOUS LES COOKIES (triés par domaine):')
        print('-'*80)
        cookies = driver.get_cookies()
        cookies_by_domain = {}
        
        for c in cookies:
            domain = c['domain']
            if domain not in cookies_by_domain:
                cookies_by_domain[domain] = []
            cookies_by_domain[domain].append(c)
        
        for domain, domain_cookies in sorted(cookies_by_domain.items()):
            print(f'\n🌐 Domaine: {domain}')
            for c in domain_cookies:
                size = len(c['value'])
                flags = []
                if c.get('httpOnly'): flags.append('HttpOnly')
                if c.get('secure'): flags.append('Secure')
                if c.get('sameSite'): flags.append(f"SameSite={c['sameSite']}")
                
                print(f"  📦 {c['name']}: {size} chars {' [' + ', '.join(flags) + ']' if flags else ''}")
                if size < 50:
                    print(f"     Value: {c['value']}")
                elif 'token' in c['name'].lower() or 'auth' in c['name'].lower():
                    print(f"     Preview: {c['value'][:100]}...")
        
        # 2. Analyse des logs réseau pour trouver les requêtes de refresh
        print('\n\n🔍 ANALYSE DES REQUÊTES RÉSEAU:')
        print('-'*80)
        
        logs = driver.get_log('performance')
        
        # Chercher spécifiquement les requêtes de refresh/auth
        refresh_requests = []
        auth_requests = []
        
        for entry in logs:
            try:
                message = json.loads(entry['message'])['message']
                
                # Requêtes
                if message['method'] == 'Network.requestWillBeSent':
                    url = message['params']['request']['url']
                    method = message['params']['request']['method']
                    
                    # Filtrer les requêtes intéressantes
                    if any(keyword in url.lower() for keyword in ['refresh', 'token', '/auth/']):
                        headers = message['params']['request'].get('headers', {})
                        post_data = message['params']['request'].get('postData', '')
                        
                        req_info = {
                            'url': url,
                            'method': method,
                            'headers': {k: v for k, v in headers.items() if 'token' in k.lower() or 'auth' in k.lower() or 'cookie' in k.lower()},
                            'postData': post_data[:200] if post_data else None
                        }
                        
                        if 'refresh' in url.lower():
                            refresh_requests.append(req_info)
                        else:
                            auth_requests.append(req_info)
                
                # Réponses
                if message['method'] == 'Network.responseReceived':
                    url = message['params']['response']['url']
                    status = message['params']['response']['status']
                    
                    if any(keyword in url.lower() for keyword in ['refresh', 'token', '/auth/']):
                        headers = message['params']['response'].get('headers', {})
                        
                        # Chercher les Set-Cookie headers
                        set_cookies = {k: v for k, v in headers.items() if 'set-cookie' in k.lower()}
                        
                        if set_cookies or status != 200:
                            print(f'\n📨 Response: {method} {url}')
                            print(f'   Status: {status}')
                            if set_cookies:
                                for k, v in set_cookies.items():
                                    print(f'   {k}: {v[:100]}...')
            
            except Exception as e:
                continue
        
        # Afficher les requêtes de refresh trouvées
        if refresh_requests:
            print('\n\n✅ REQUÊTES DE REFRESH DÉTECTÉES:')
            print('-'*80)
            for req in refresh_requests:
                print(f"\n🔄 {req['method']} {req['url']}")
                if req['headers']:
                    print('   Headers:')
                    for k, v in req['headers'].items():
                        print(f'     {k}: {v[:100]}...')
                if req['postData']:
                    print(f"   Post Data: {req['postData']}")
        else:
            print('\n\n❌ Aucune requête de refresh détectée')
        
        # Afficher autres requêtes auth
        if auth_requests:
            print('\n\n🔐 AUTRES REQUÊTES AUTH:')
            print('-'*80)
            for req in auth_requests[:5]:  # Limiter à 5
                print(f"\n📍 {req['method']} {req['url']}")
                if req['postData']:
                    print(f"   Data: {req['postData']}")
        
        # 3. Analyse du localStorage
        print('\n\n💾 LOCAL STORAGE:')
        print('-'*80)
        try:
            local_storage = driver.execute_script("""
                let storage = {};
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    let value = localStorage.getItem(key);
                    storage[key] = value.length > 100 ? value.substring(0, 100) + '...' : value;
                }
                return storage;
            """)
            
            if local_storage:
                for key, value in local_storage.items():
                    print(f"  🗄️  {key}: {value}")
            else:
                print('  (vide)')
        except Exception as e:
            print(f'  Erreur: {e}')
        
        # 4. Suggestion de solution
        print('\n\n' + '='*80)
        print('💡 SUGGESTIONS')
        print('='*80)
        
        oneflex_cookies = [c for c in cookies if 'oneflex' in c['domain'] or 'worldline' in c['domain']]
        
        if oneflex_cookies:
            print('\n✅ Des cookies OneFlex existent. Possibilités:')
            print('   1. Les cookies contiennent peut-être un session ID qui persiste')
            print('   2. Le backend OneFlex gère le refresh automatiquement')
            print('   3. Tester de faire une requête GraphQL avec ces cookies')
        
        if not refresh_requests:
            print('\n📝 Aucune requête de refresh n\'a été capturée.')
            print('   Cela suggère que:')
            print('   - Le refresh se fait côté serveur (OneFlex backend)')
            print('   - Ou le navigateur maintient une session via cookies seulement')
            print('   - Essayez de capturer le trafic pendant 1-2 heures pour voir un refresh')
        
        print('\n⏸️  Appuyez sur Entrée pour fermer...')
        input()
        
    finally:
        driver.quit()

if __name__ == '__main__':
    analyze_refresh_mechanism()
