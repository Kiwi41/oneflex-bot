#!/usr/bin/env python3
"""
Script de test pour le mécanisme de refresh token
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from oneflex_client import OneFlexClient
from notifications import NotificationService
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def main():
    """Test du refresh token"""
    print("\n" + "="*80)
    print("TEST DU MÉCANISME DE REFRESH TOKEN")
    print("="*80 + "\n")
    
    # Charger la configuration
    config = Config()
    
    # Initialiser le client avec les tokens
    client = OneFlexClient(token=config.TOKEN, refresh_token=config.REFRESH_TOKEN)
    
    # Vérifier l'authentification initiale
    print("1️⃣ Test de l'authentification initiale...")
    user_id = client.get_my_user_id()
    if user_id:
        print(f"   ✅ Authentifié : {user_id}")
        # Récupérer les infos via GraphQL
        query = """
        query me($userId: UserIdType!) {
            user(idV2: $userId) {
                id
                firstName
                lastName
                email
            }
        }
        """
        data = client._graphql_request(query, {'userId': user_id})
        if data and 'user' in data:
            user = data['user']
            print(f"   👤 {user.get('firstName')} {user.get('lastName')}")
            print(f"   📧 {user.get('email')}")
    else:
        print("   ❌ Échec de l'authentification initiale")
        return
    
    print("\n2️⃣ Test du refresh token...")
    print("   ⏳ Tentative de rafraîchissement du token...")
    
    success = client.refresh_access_token()
    
    if success:
        print("   ✅ Token rafraîchi avec succès !")
        print("\n3️⃣ Vérification avec le nouveau token...")
        user_id = client.get_my_user_id()
        if user_id:
            print(f"   ✅ Toujours authentifié : {user_id}")
        else:
            print("   ❌ Échec après le refresh")
    else:
        print("   ❌ Échec du rafraîchissement")
        print("\n📊 Analyse :")
        print("   • L'API OneFlex ne supporte probablement pas le endpoint /api/auth/refresh")
        print("   • Le refresh_token sert uniquement pour l'authentification SSO")
        print("   • Solution : renouveler manuellement avec auto_get_tokens.py")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
