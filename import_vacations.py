#!/usr/bin/env python3
"""
Script d'import automatique des congés depuis le portail RH

Usage:
  1. Copiez le texte depuis votre portail RH
  2. Lancez: python import_vacations.py
  3. Collez le texte (Ctrl+D pour terminer)
  
  OU depuis un fichier:
  python import_vacations.py < mes_conges.txt
"""

import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Mapping des mois français
MONTHS_FR = {
    'janv': 1, 'janvier': 1,
    'févr': 2, 'février': 2,
    'mars': 3,
    'avr': 4, 'avril': 4,
    'mai': 5,
    'juin': 6,
    'juil': 7, 'juillet': 7,
    'août': 8, 'aout': 8,
    'sept': 9, 'septembre': 9,
    'oct': 10, 'octobre': 10,
    'nov': 11, 'novembre': 11,
    'déc': 12, 'décembre': 12, 'dec': 12
}


def parse_french_date(date_str: str) -> datetime:
    """Parse une date en français (ex: '21 mai 2026', '15 avr. 2026')"""
    # Nettoyer la chaîne
    date_str = date_str.strip().lower()
    
    # Pattern: "15 mai 2026" ou "15 mai. 2026"
    pattern = r'(\d{1,2})\s+([a-zéû\.]+)\s+(\d{4})'
    match = re.search(pattern, date_str)
    
    if not match:
        raise ValueError(f"Format de date invalide: {date_str}")
    
    day = int(match.group(1))
    month_str = match.group(2).rstrip('.')
    year = int(match.group(3))
    
    # Trouver le mois
    month = None
    for french_name, month_num in MONTHS_FR.items():
        if month_str.startswith(french_name):
            month = month_num
            break
    
    if month is None:
        raise ValueError(f"Mois inconnu: {month_str}")
    
    return datetime(year, month, day)


def parse_vacations(text: str) -> List[Tuple[str, str]]:
    """
    Parse le texte du portail RH et extrait les périodes de congés approuvés
    
    Returns:
        Liste de tuples (date_debut, date_fin) au format YYYY-MM-DD
        Pour une date unique, date_debut == date_fin
    """
    vacations = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Chercher un bloc de congé (commence par "Congé" ou "RTT")
        if line.startswith(('Congé', 'RTT')):
            # Vérifier le statut (ligne suivante normalement)
            if i + 1 < len(lines):
                status = lines[i + 1].strip()
                
                # Seulement les congés approuvés
                if status == 'Approuvé':
                    # Chercher les dates dans les lignes suivantes
                    j = i + 2
                    start_date = None
                    end_date = None
                    
                    while j < len(lines) and j < i + 10:  # Limiter la recherche
                        current_line = lines[j].strip()
                        
                        # Fin du bloc si on trouve un nouveau type de congé
                        if current_line.startswith(('Congé', 'RTT')):
                            break
                        
                        # Période: "Du X Au Y"
                        if current_line.startswith('Du '):
                            try:
                                start_date = parse_french_date(current_line[3:])
                            except:
                                pass
                        
                        if current_line.startswith('Au '):
                            try:
                                end_date = parse_french_date(current_line[3:])
                            except:
                                pass
                        
                        # Date unique (pas de "Du" ni "Au", mais contient un mois)
                        if not current_line.startswith(('Du ', 'Au ', 'Journée', 'Après-midi', 'Matin')):
                            # Essayer de parser comme une date
                            try:
                                date = parse_french_date(current_line)
                                if start_date is None:
                                    start_date = date
                                    end_date = date
                            except:
                                pass
                        
                        j += 1
                    
                    # Ajouter la vacation si on a trouvé des dates
                    if start_date:
                        if end_date is None:
                            end_date = start_date
                        
                        vacations.append((
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d')
                        ))
        
        i += 1
    
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


def update_env_file(vacation_string: str, env_path: Path = Path('config/.env')):
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
    print("📅 Import des congés depuis le portail RH")
    print("=" * 50)
    print()
    
    # Vérifier si on lit depuis stdin ou un fichier
    if sys.stdin.isatty():
        print("Collez le texte depuis votre portail RH (Ctrl+D pour terminer):")
        print()
    
    # Lire tout le texte
    text = sys.stdin.read()
    
    if not text.strip():
        print("❌ Aucun texte fourni")
        return 1
    
    print()
    print("🔍 Analyse du texte...")
    
    # Parser les congés
    try:
        vacations = parse_vacations(text)
    except Exception as e:
        print(f"❌ Erreur lors du parsing: {e}")
        return 1
    
    if not vacations:
        print("⚠️  Aucun congé approuvé trouvé")
        return 1
    
    print(f"✅ {len(vacations)} période(s) de congés trouvée(s):")
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
    
    # Demander confirmation
    if sys.stdin.isatty():
        response = input("Mettre à jour config/.env ? (o/n): ")
        if response.lower() != 'o':
            print("❌ Annulé")
            return 0
    
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


if __name__ == '__main__':
    sys.exit(main())
