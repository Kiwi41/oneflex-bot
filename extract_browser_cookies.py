#!/usr/bin/env python3
"""
Extrait les cookies OneFlex depuis votre navigateur Chrome personnel
pour comprendre le mécanisme de persistance de session
"""

import os
import sqlite3
import json
from pathlib import Path
import shutil

def find_chrome_cookies_db():
    """Trouve la base de données des cookies de Chrome"""
    possible_paths = [
        Path.home() / '.config/google-chrome/Default/Cookies',
        Path.home() / '.config/chromium/Default/Cookies',
        Path.home() / 'snap/chromium/common/chromium/Default/Cookies',
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def extract_oneflex_cookies():
    """Extrait les cookies OneFlex du navigateur"""
    
    cookies_db = find_chrome_cookies_db()
    
    if not cookies_db:
        print('❌ Base de données Chrome Cookies non trouvée')
        print('\n📝 Chemins testés:')
        for path in [
            Path.home() / '.config/google-chrome/Default/Cookies',
            Path.home() / '.config/chromium/Default/Cookies',
            Path.home() / 'snap/chromium/common/chromium/Default/Cookies',
        ]:
            print(f'  - {path}')
        return
    
    print(f'✅ Base de données trouvée: {cookies_db}')
    
    # Copier la base de données (Chrome la verrouille)
    temp_db = '/tmp/chrome_cookies_temp.db'
    try:
        shutil.copy2(cookies_db, temp_db)
    except Exception as e:
        print(f'❌ Erreur lors de la copie: {e}')
        print('💡 Fermez Chrome et réessayez')
        return
    
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Requête pour obtenir les cookies OneFlex
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE '%oneflex%' OR host_key LIKE '%worldline%'
            ORDER BY host_key, name
        """)
        
        cookies = cursor.fetchall()
        
        if not cookies:
            print('❌ Aucun cookie OneFlex trouvé dans Chrome')
            print('\n💡 Assurez-vous d\'être connecté à OneFlex dans Chrome')
            return
        
        print(f'\n✅ {len(cookies)} cookie(s) OneFlex trouvé(s):\n')
        print('='*80)
        
        cookies_data = []
        
        for cookie in cookies:
            host, name, value, path, expires, secure, httponly, samesite = cookie
            
            print(f'\n📦 Cookie: {name}')
            print(f'   Domain: {host}')
            print(f'   Path: {path}')
            print(f'   Secure: {bool(secure)}')
            print(f'   HttpOnly: {bool(httponly)}')
            print(f'   SameSite: {samesite}')
            print(f'   Expires: {expires} (timestamp Chrome)')
            print(f'   Size: {len(value)} chars')
            
            # Afficher preview
            if len(value) < 50:
                print(f'   Value: {value}')
            elif 'token' in name.lower() or 'auth' in name.lower() or 'session' in name.lower():
                print(f'   Value (preview): {value[:100]}...')
            
            cookies_data.append({
                'name': name,
                'value': value,
                'domain': host,
                'path': path,
                'secure': bool(secure),
                'httpOnly': bool(httponly),
                'sameSite': samesite
            })
        
        # Sauvegarder dans un fichier JSON
        output_file = 'browser_cookies.json'
        with open(output_file, 'w') as f:
            json.dump(cookies_data, f, indent=2)
        
        print(f'\n\n✅ Cookies sauvegardés dans: {output_file}')
        print('\n' + '='*80)
        print('💡 ANALYSE:')
        print('='*80)
        
        # Chercher des patterns
        token_cookies = [c for c in cookies_data if any(k in c['name'].lower() for k in ['token', 'auth', 'session', 'jwt'])]
        
        if token_cookies:
            print(f'\n🔑 {len(token_cookies)} cookie(s) potentiel(s) pour l\'authentification:')
            for c in token_cookies:
                print(f"  - {c['name']} ({len(c['value'])} chars)")
        else:
            print('\n⚠️  Aucun cookie avec "token", "auth", "session" ou "jwt" dans le nom')
            print('    Les tokens sont peut-être stockés sous d\'autres noms')
        
        # Chercher les cookies avec de longues valeurs (possibles JWTs)
        long_cookies = [c for c in cookies_data if len(c['value']) > 200]
        if long_cookies:
            print(f'\n📏 {len(long_cookies)} cookie(s) avec valeurs longues (> 200 chars):')
            for c in long_cookies:
                print(f"  - {c['name']} ({len(c['value'])} chars) - Possible JWT ou token")
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

if __name__ == '__main__':
    print('🔍 Extraction des cookies OneFlex depuis Chrome\n')
    extract_oneflex_cookies()
