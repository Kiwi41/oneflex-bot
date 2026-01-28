#!/usr/bin/env python3
"""
Test différentes méthodes pour appeler l'endpoint de refresh
Si vos collègues ont réussi, il y a forcément une méthode qui fonctionne
"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

ACCESS_TOKEN = os.getenv('ONEFLEX_TOKEN')
REFRESH_TOKEN = os.getenv('ONEFLEX_REFRESH_TOKEN')

BASE_URL = 'https://oneflex.myworldline.com'

def test_method_1_simple_get():
    """Méthode 1: Simple GET avec Authorization header"""
    print('\n1️⃣  Test: GET /api/auth/refresh avec Authorization header')
    print('-' * 70)
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/auth/refresh', headers=headers, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_2_post_with_refresh_token():
    """Méthode 2: POST avec refresh_token dans le body"""
    print('\n2️⃣  Test: POST /api/auth/refresh avec refresh_token en body')
    print('-' * 70)
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        'refresh_token': REFRESH_TOKEN
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/refresh', headers=headers, json=payload, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_3_post_with_cookies():
    """Méthode 3: POST avec tokens en cookies"""
    print('\n3️⃣  Test: POST /api/auth/refresh avec tokens en cookies')
    print('-' * 70)
    
    cookies = {
        'access_token': ACCESS_TOKEN,
        'refresh_token': REFRESH_TOKEN
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/refresh', cookies=cookies, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        print(f'   Set-Cookie headers: {response.headers.get("Set-Cookie", "None")}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_4_post_form_data():
    """Méthode 4: POST avec form data (comme OAuth2 standard)"""
    print('\n4️⃣  Test: POST /api/auth/refresh avec form data (OAuth2 standard)')
    print('-' * 70)
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/refresh', headers=headers, data=data, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_5_get_with_refresh_header():
    """Méthode 5: GET avec X-Refresh-Token header custom"""
    print('\n5️⃣  Test: GET /api/auth/refresh avec X-Refresh-Token header')
    print('-' * 70)
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'X-Refresh-Token': REFRESH_TOKEN
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/auth/refresh', headers=headers, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_6_token_endpoint():
    """Méthode 6: POST /api/auth/token (endpoint alternatif)"""
    print('\n6️⃣  Test: POST /api/auth/token avec refresh_token')
    print('-' * 70)
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/token', headers=headers, json=payload, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_7_renew_endpoint():
    """Méthode 7: POST /api/auth/renew"""
    print('\n7️⃣  Test: POST /api/auth/renew')
    print('-' * 70)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    payload = {
        'refresh_token': REFRESH_TOKEN
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/renew', headers=headers, json=payload, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            print('   ✅ SUCCESS!')
            return response.json()
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def test_method_8_graphql_refresh():
    """Méthode 8: Requête GraphQL pour refresh"""
    print('\n8️⃣  Test: GraphQL mutation pour refresh token')
    print('-' * 70)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    query = """
    mutation RefreshToken($refreshToken: String!) {
        refreshToken(refreshToken: $refreshToken) {
            accessToken
            refreshToken
        }
    }
    """
    
    payload = {
        'query': query,
        'variables': {
            'refreshToken': REFRESH_TOKEN
        }
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/gql', headers=headers, json=payload, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                print('   ✅ SUCCESS!')
                return data['data']
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    return None

def main():
    print('='*70)
    print('🔍 TEST DE TOUTES LES MÉTHODES DE REFRESH POSSIBLES')
    print('='*70)
    
    if not ACCESS_TOKEN or not REFRESH_TOKEN:
        print('\n❌ ACCESS_TOKEN ou REFRESH_TOKEN manquant dans .env')
        return
    
    print(f'\n📝 Tokens utilisés:')
    print(f'   ACCESS_TOKEN: {ACCESS_TOKEN[:50]}...')
    print(f'   REFRESH_TOKEN: {REFRESH_TOKEN[:50] if len(REFRESH_TOKEN) > 50 else REFRESH_TOKEN}')
    
    methods = [
        test_method_1_simple_get,
        test_method_2_post_with_refresh_token,
        test_method_3_post_with_cookies,
        test_method_4_post_form_data,
        test_method_5_get_with_refresh_header,
        test_method_6_token_endpoint,
        test_method_7_renew_endpoint,
        test_method_8_graphql_refresh
    ]
    
    results = []
    for method in methods:
        result = method()
        if result:
            results.append({
                'method': method.__name__,
                'result': result
            })
    
    print('\n\n' + '='*70)
    print('📊 RÉSUMÉ')
    print('='*70)
    
    if results:
        print(f'\n✅ {len(results)} méthode(s) réussie(s):')
        for r in results:
            print(f'\n🎉 {r["method"]}')
            print(f'   Result: {json.dumps(r["result"], indent=2)[:300]}')
    else:
        print('\n❌ Aucune méthode n\'a fonctionné')
        print('\n💡 Suggestions:')
        print('   1. Vérifiez que vos tokens sont valides (pas expirés)')
        print('   2. Vos collègues utilisent peut-être une méthode différente')
        print('   3. Le refresh se fait peut-être automatiquement côté serveur')
        print('   4. Il y a peut-être un endpoint /api/auth/* différent')

if __name__ == '__main__':
    main()
