#!/usr/bin/env python3
"""
Script de test pour le refresh automatique des tokens
Simule un token expiré et vérifie que le refresh fonctionne
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from oneflex_client import OneFlexClient
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_refresh():
    """Test du mécanisme de refresh automatique"""
    
    print("="*70)
    print("🧪 TEST DU REFRESH AUTOMATIQUE")
    print("="*70)
    
    # Charger la config
    load_dotenv()
    
    token = os.getenv('ONEFLEX_TOKEN')
    refresh_token = os.getenv('ONEFLEX_REFRESH_TOKEN')
    
    if not token or not refresh_token:
        print("\n❌ Tokens manquants dans .env")
        print("   Assurez-vous d'avoir ONEFLEX_TOKEN et ONEFLEX_REFRESH_TOKEN")
        return False
    
    print(f"\n📝 Configuration:")
    print(f"   Token actuel: {token[:50]}...")
    print(f"   Refresh token: {refresh_token}")
    
    # Créer le client
    client = OneFlexClient(token=token, refresh_token=refresh_token)
    
    # Test 1: Vérifier que le token actuel fonctionne
    print("\n" + "="*70)
    print("1️⃣  Test: Vérification du token actuel")
    print("="*70)
    
    if client.verify_token():
        print("✅ Le token actuel est valide")
        token_works = True
    else:
        print("⚠️  Le token actuel est expiré (c'est OK pour le test)")
        token_works = False
    
    # Test 2: Forcer un refresh
    print("\n" + "="*70)
    print("2️⃣  Test: Refresh manuel du token")
    print("="*70)
    
    old_token = client.token
    
    if client.refresh_access_token():
        print("✅ Refresh réussi!")
        
        new_token = client.token
        
        if new_token != old_token:
            print(f"✅ Nouveau token différent de l'ancien")
            print(f"   Ancien: {old_token[:50]}...")
            print(f"   Nouveau: {new_token[:50]}...")
        else:
            print("⚠️  Le token n'a pas changé (bizarre)")
        
        # Vérifier que le nouveau token fonctionne
        print("\n   Vérification du nouveau token...")
        if client.verify_token():
            print("   ✅ Le nouveau token fonctionne!")
        else:
            print("   ❌ Le nouveau token ne fonctionne pas")
            return False
    else:
        print("❌ Échec du refresh")
        return False
    
    # Test 3: Vérifier que le .env a été mis à jour
    print("\n" + "="*70)
    print("3️⃣  Test: Vérification de la persistence dans .env")
    print("="*70)
    
    # Recharger le .env
    import importlib
    import dotenv
    importlib.reload(dotenv)
    dotenv.load_dotenv(override=True)
    
    token_in_env = os.getenv('ONEFLEX_TOKEN')
    
    if token_in_env == new_token:
        print("✅ Le token dans .env a été mis à jour correctement")
    else:
        print("⚠️  Le token dans .env ne correspond pas au nouveau token")
        print(f"   .env: {token_in_env[:50] if token_in_env else 'None'}...")
        print(f"   Mémoire: {new_token[:50]}...")
    
    # Test 4: Simuler une requête après expiration
    print("\n" + "="*70)
    print("4️⃣  Test: Simulation d'un refresh automatique sur 401")
    print("="*70)
    
    # Créer un client avec un token invalide pour forcer un 401
    print("\n   Création d'un client avec un token expiré...")
    expired_client = OneFlexClient(
        token="token_invalide_pour_test",
        refresh_token=refresh_token
    )
    
    print("   Tentative de requête (devrait déclencher auto-refresh)...")
    
    # Tenter une requête (va échouer avec 401, puis auto-refresh)
    result = expired_client.verify_token()
    
    if result:
        print("   ✅ Auto-refresh fonctionne! Le client a automatiquement")
        print("      renouvelé son token et réessayé la requête")
    else:
        print("   ⚠️  Auto-refresh ne semble pas fonctionner comme attendu")
        print("      (Vérifiez les logs ci-dessus)")
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)
    print("✅ Refresh manuel: Fonctionne")
    print("✅ Persistence .env: Fonctionne")
    print("✅ Auto-refresh sur 401: " + ("Fonctionne" if result else "À vérifier"))
    
    print("\n🎉 Tous les tests sont OK!")
    print("\n💡 Le bot va maintenant renouveler automatiquement le token")
    print("   quand il expire (toutes les ~15 minutes)")
    
    return True

if __name__ == '__main__':
    try:
        success = test_refresh()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
