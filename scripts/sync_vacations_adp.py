#!/usr/bin/env python3
"""
Script de synchronisation automatique des congés depuis l'API ADP

Usage:
  1. Copiez votre session cookie depuis Chrome DevTools (F12 > Network > cookie EMEASMSESSION)
  2. export ADP_SESSION_COOKIE="votre_cookie"
  3. python sync_vacations_adp.py
  
  OU avec le cookie en argument:
  python sync_vacations_adp.py --cookie "votre_cookie"
"""

import sys
import os
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional


def get_cookie_from_file(cookie_file: Path = Path('.adp_cookie')) -> Optional[str]:
    """
    Lit le cookie depuis un fichier
    
    Args:
        cookie_file: Chemin vers le fichier contenant le cookie
        
    Returns:
        Le cookie ou None si le fichier n'existe pas
    """
    if not cookie_file.exists():
        return None
    
    with open(cookie_file, 'r') as f:
        cookie = f.read().strip()
        return cookie if cookie else None


def save_cookie_to_file(cookie: str, cookie_file: Path = Path('.adp_cookie')):
    """
    Sauvegarde le cookie dans un fichier
    
    Args:
        cookie: Le cookie à sauvegarder
        cookie_file: Chemin vers le fichier
    """
    with open(cookie_file, 'w') as f:
        f.write(cookie)
    
    # Sécuriser le fichier (lecture/écriture propriétaire uniquement)
    os.chmod(cookie_file, 0o600)
    print(f"✅ Cookie sauvegardé dans {cookie_file}")


def get_adp_vacations(session_cookie: str, worker_id: str = "kfavry-jm3") -> List[dict]:
    """
    Récupère les congés depuis l'API ADP
    
    Args:
        session_cookie: Cookie de session EMEASMSESSION
        worker_id: ID du travailleur ADP
        
    Returns:
        Liste des congés au format ADP
    """
    # Dates de recherche : 2 ans en arrière et 2 ans en avant
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d')
    
    url = f"https://mon.adp.com/time/v3/workers/{worker_id}/time-off-requests"
    params = {
        '$filter': f"datePeriod/startDate ge '{start_date}' and datePeriod/endDate le '{end_date}'"
    }
    
    cookies = {
        'EMEASMSESSION': session_cookie,
        'ADPEHCSSO': 'Yes',
        'ADPLangLocaleCookie': 'en_US',
        'ADPFED': '1'
    }
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR',
        'consumerappoid': 'RDBX:2024.06',
        'rolecode': 'employee',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    
    if response.status_code == 401:
        print("❌ Session expirée - Cookie invalide ou expiré")
        print()
        print("Pour mettre à jour le cookie EMEASMSESSION:")
        print("  1. Ouvrez https://mon.adp.com dans Chrome")
        print("  2. Connectez-vous si nécessaire")
        print("  3. Appuyez sur F12 pour ouvrir DevTools")
        print("  4. Allez dans l'onglet 'Application' (ou 'Stockage')")
        print("  5. Dans le menu de gauche: Cookies > https://mon.adp.com")
        print("  6. Trouvez 'EMEASMSESSION' dans la liste")
        print("  7. Double-cliquez sur la valeur et copiez-la (Ctrl+C)")
        print("  8. Relancez: python sync_vacations_adp.py --cookie 'nouveau_cookie' --save-cookie")
        print()
        raise Exception("Cookie expiré")
    
    if response.status_code != 200:
        raise Exception(f"❌ Erreur API ADP: {response.status_code} - {response.text}")
    
    data = response.json()
    
    if 'timeOffRequests' not in data:
        raise Exception(f"❌ Format de réponse inattendu: {data}")
    
    return data['timeOffRequests']


def parse_adp_vacations(time_off_requests: List[dict]) -> List[Tuple[str, str]]:
    """
    Parse les congés ADP et extrait les périodes approuvées
    
    Returns:
        Liste de tuples (date_debut, date_fin) au format YYYY-MM-DD
    """
    vacations = []
    
    for request in time_off_requests:
        # Vérifier le statut
        status_code = request.get('requestStatusCode', {}).get('codeValue', '')
        
        # Filtrer uniquement les congés approuvés
        if status_code.lower() != 'approved':
            continue
        
        # Récupérer les dates depuis timeOffEntries
        time_off_entries = request.get('timeOffEntries', [])
        
        for entry in time_off_entries:
            date_time_period = entry.get('dateTimePeriod', {})
            start_datetime = date_time_period.get('startDateTime')
            end_datetime = date_time_period.get('endDateTime')
            
            if not start_datetime or not end_datetime:
                continue
            
            # Convertir ISO datetime en date YYYY-MM-DD
            start_date = datetime.fromisoformat(start_datetime).strftime('%Y-%m-%d')
            end_date = datetime.fromisoformat(end_datetime).strftime('%Y-%m-%d')
            
            vacations.append((start_date, end_date))
    
    return vacations


def format_vacation_dates(vacations: List[Tuple[str, str]]) -> str:
    """
    Formate les vacations au format attendu par le bot
    
    Format: DATE:DATE,DATE:DATE ou DATE pour une date unique
    """
    formatted = []
    
    for start, end in sorted(vacations):
        if start == end:
            formatted.append(start)
        else:
            formatted.append(f"{start}:{end}")
    
    return ','.join(formatted)


def update_env_file(vacation_string: str, env_path: Path = Path('config/.env')) -> bool:
    """Met à jour le fichier .env avec les nouvelles vacations"""
    if not env_path.exists():
        print(f"❌ Fichier {env_path} introuvable")
        return False
    
    # Lire le contenu actuel
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Mettre à jour la ligne VACATION_DATES
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('VACATION_DATES='):
            lines[i] = f'VACATION_DATES={vacation_string}\n'
            updated = True
            break
    
    if not updated:
        print(f"❌ VACATION_DATES non trouvé dans {env_path}")
        return False
    
    # Écrire le nouveau contenu
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Synchronise les congés depuis l\'API ADP')
    parser.add_argument('--cookie', help='Cookie de session EMEASMSESSION')
    parser.add_argument('--cookie-file', default='.adp_cookie', help='Fichier contenant le cookie (défaut: .adp_cookie)')
    parser.add_argument('--save-cookie', action='store_true', help='Sauvegarder le cookie dans le fichier')
    parser.add_argument('--worker-id', default='kfavry-jm3', help='ID du travailleur ADP')
    args = parser.parse_args()
    
    cookie_file = Path(args.cookie_file)
    
    print("🔄 Synchronisation des congés depuis ADP")
    print("=" * 50)
    print()
    
    # Récupérer le cookie (priorité: argument > fichier > env var)
    session_cookie = args.cookie or get_cookie_from_file(cookie_file) or os.getenv('ADP_SESSION_COOKIE')
    
    # Sauvegarder le cookie si demandé
    if args.save_cookie and args.cookie:
        save_cookie_to_file(args.cookie, cookie_file)
        print()
    
    if not session_cookie:
        print("❌ Cookie de session manquant")
        print()
        print("Méthode recommandée (sauvegarde dans fichier):")
        print("  python sync_vacations_adp.py --cookie 'votre_cookie' --save-cookie")
        print()
        print("Autres méthodes:")
        print("  1. Créez le fichier .adp_cookie avec votre cookie")
        print("  2. export ADP_SESSION_COOKIE='votre_cookie'")
        print("  3. python sync_vacations_adp.py --cookie 'votre_cookie'")
        print()
        print("Pour obtenir le cookie:")
        print("  1. Ouvrez https://mon.adp.com dans Chrome")
        print("  2. F12 > Onglet 'Application' > Cookies > https://mon.adp.com")
        print("  3. Copiez la valeur de 'EMEASMSESSION'")
        return 1
    
    try:
        # Récupérer les congés depuis l'API
        print("📡 Connexion à l'API ADP...")
        time_off_requests = get_adp_vacations(session_cookie, args.worker_id)
        print(f"✅ {len(time_off_requests)} demande(s) de congé(s) récupérée(s)")
        print()
        
        # Parser et filtrer les congés approuvés
        print("🔍 Filtrage des congés approuvés...")
        vacations = parse_adp_vacations(time_off_requests)
        
        if not vacations:
            print("⚠️  Aucun congé approuvé trouvé")
            return 1
        
        print(f"✅ {len(vacations)} période(s) approuvée(s):")
        print()
        
        # Afficher les congés trouvés
        for start, end in sorted(vacations):
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            
            if start == end:
                print(f"  • {start_date.strftime('%d/%m/%Y')}")
            else:
                print(f"  • {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}")
        
        print()
        
        # Formater pour le bot
        vacation_string = format_vacation_dates(vacations)
        print("📝 Format pour le bot:")
        print(f"  VACATION_DATES={vacation_string}")
        print()
        
        # Mettre à jour le fichier
        print("💾 Mise à jour de config/.env...")
        if update_env_file(vacation_string):
            print("✅ config/.env mis à jour avec succès!")
            print()
            print("🚀 Prochaines étapes:")
            print("  1. Redémarrez le bot: docker compose restart")
            print("  2. Ou attendez la prochaine exécution automatique")
            return 0
        else:
            return 1
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
