# 🏗️ Architecture du Bot OneFlex

Ce document explique l'architecture technique du bot pour les débutants.

## 📐 Vue d'Ensemble

Le bot OneFlex est une application Python qui automatise les réservations de bureaux. Voici comment il fonctionne :

```
┌───────────────────────────────────────────────────────────────┐
│  UTILISATEUR                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Terminal │  │  Docker  │  │ Discord  │                   │
│  └─────┬────┘  └────┬─────┘  └────▲─────┘                   │
└────────┼────────────┼─────────────┼──────────────────────────┘
         │            │             │
         ▼            ▼             │
┌───────────────────────────────────┼──────────────────────────┐
│  BOT ONEFLEX                      │                          │
│                                   │                          │
│  ┌─────────────┐   ┌──────────────┴────────┐                │
│  │  main.py    │──►│  notifications.py     │                │
│  │  (Orchestre │   │  (Envoie messages    │                │
│  │   tout)     │   │   Discord)           │                │
│  └──────┬──────┘   └───────────────────────┘                │
│         │                                                     │
│         ├──► config.py (Lit .env)                           │
│         │                                                     │
│         ├──► oneflex_client.py (Appelle API OneFlex)       │
│         │                                                     │
│         └──► vacation_manager.py (Gère congés)             │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │  API OneFlex   │
                   │  (Internet)    │
                   └────────────────┘
```

## 📦 Les Composants Principaux

### 1. `src/main.py` - Le Chef d'Orchestre

C'est le **point d'entrée** du bot. Il coordonne tous les autres modules.

**Responsabilités :**
- Parse les arguments de la ligne de commande (`--schedule`, `--date`, etc.)
- Initialise les modules (client, notifications, vacances)
- Lance le scheduler pour les exécutions automatiques
- Gère la boucle principale du bot

**Code simplifié :**
```python
def main():
    # 1. Lire les arguments
    args = parser.parse_args()
    
    # 2. Créer le bot
    bot = OneFlexBot()
    
    # 3. Choisir le mode
    if args.schedule:
        # Mode automatique : tourne en permanence
        bot.schedule_daily_booking()
    elif args.date:
        # Mode manuel : réserve une date précise
        bot.book_for_date(args.date)
    elif args.recurring:
        # Mode récurrent : réserve N semaines d'avance
        bot.book_recurring()
```

### 2. `src/config.py` - Le Gestionnaire de Configuration

Ce fichier charge **toutes les variables d'environnement** depuis le fichier `.env`.

**Pourquoi un fichier séparé ?**
- Centralise toute la configuration
- Évite de mettre des secrets dans le code
- Permet de changer la config sans modifier le code

**Exemple :**
```python
class Config:
    # Charge depuis .env
    TOKEN = os.getenv('ONEFLEX_TOKEN')  # Le token d'accès
    RESERVATION_TIME = os.getenv('RESERVATION_TIME', '09:00')  # Heure par défaut
    REMINDER_TIME = os.getenv('REMINDER_TIME', '')  # Peut être vide
    
    # Conversion en types appropriés
    RECURRING_WEEKS = int(os.getenv('RECURRING_WEEKS', 0))  # Converti en nombre
```

**Variables importantes :**
- `ONEFLEX_TOKEN` : Authentification API (obligatoire)
- `RESERVATION_TIME` : Heure d'exécution (format `HH:MM`)
- `VACATION_DATES` : Périodes de congés (format `YYYY-MM-DD:YYYY-MM-DD,YYYY-MM-DD`)

### 3. `src/oneflex_client.py` - Le Communicateur API

Ce module **communique avec l'API OneFlex** via des requêtes HTTP.

**Rôle :**
- Authentification avec le token
- Récupération des bureaux disponibles
- Création de réservations
- Annulation de réservations existantes

**Méthodes principales :**

```python
class OneFlexClient:
    def __init__(self, token):
        """
        Initialise le client avec le token d'authentification
        """
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def get_available_desks(self, date):
        """
        Récupère les bureaux disponibles pour une date
        
        Args:
            date: La date au format YYYY-MM-DD
            
        Returns:
            Liste des bureaux disponibles
        """
        # Fait une requête GraphQL à l'API OneFlex
        response = requests.post(
            'https://api.oneflex.com/graphql',
            headers=self.headers,
            json={'query': '...'}
        )
        return response.json()
    
    def book_desk(self, desk_id, date):
        """
        Réserve un bureau spécifique
        
        Args:
            desk_id: L'ID du bureau à réserver
            date: La date de réservation
            
        Returns:
            True si succès, False sinon
        """
        # Envoie une mutation GraphQL
        response = requests.post(...)
        return response.status_code == 200
```

**Pourquoi GraphQL ?**
OneFlex utilise GraphQL au lieu de REST. GraphQL permet de :
- Demander exactement les données nécessaires
- Réduire le nombre de requêtes
- Avoir un schéma typé

### 4. `src/notifications.py` - Le Messager Discord

Ce module envoie des **notifications via Discord webhooks**.

**Webhook Discord :**
Un webhook est une URL spéciale qui permet d'envoyer des messages à Discord sans bot complet.

```python
class NotificationService:
    def __init__(self, webhook_url):
        """
        Initialise avec l'URL du webhook Discord
        """
        self.webhook_url = webhook_url
    
    def send_success(self, booking_info):
        """
        Envoie une notification de réservation réussie
        
        Args:
            booking_info: Dict avec date, desk, space, moment
        """
        # Construit un embed Discord (message formaté avec couleurs)
        embed = {
            "title": "✅ OneFlex Bot - Réservation confirmée",
            "color": 0x00FF00,  # Vert
            "fields": [
                {"name": "📅 Date", "value": booking_info['date']},
                {"name": "🏢 Bureau", "value": booking_info['desk']},
                # ...
            ]
        }
        
        # Envoie le webhook
        requests.post(self.webhook_url, json={"embeds": [embed]})
```

**Types de notifications :**
1. **Réservation réussie** (✅ vert)
2. **Rappel matinal** (☀️ jaune)
3. **Congés annulés** (🏝️ bleu)

### 5. `src/vacation_manager.py` - Le Gestionnaire de Congés

Ce module gère les **périodes de vacances**.

**Fonctionnalités :**
- Parse le format `VACATION_DATES` depuis `.env`
- Vérifie si une date est en vacances
- Annule automatiquement les réservations pendant les congés

```python
class VacationManager:
    def __init__(self, vacation_dates_str):
        """
        Parse la chaîne de congés
        
        Format: "2026-02-10:2026-02-14,2026-03-01"
        Devient: [
            (date(2026, 2, 10), date(2026, 2, 14)),
            (date(2026, 3, 1), date(2026, 3, 1))
        ]
        """
        self.vacations = self._parse_dates(vacation_dates_str)
    
    def is_vacation(self, date):
        """
        Vérifie si une date est en vacances
        
        Args:
            date: La date à vérifier
            
        Returns:
            True si en vacances, False sinon
        """
        for start, end in self.vacations:
            if start <= date <= end:
                return True
        return False
```

## 🔄 Flux d'Exécution Détaillé

### Scénario : Mode `--schedule` (bot en continu)

```
1. DÉMARRAGE
   ├─ main.py lit les arguments : --schedule détecté
   ├─ Charge config.py : lit RESERVATION_TIME = "03:05"
   ├─ Initialise oneflex_client.py avec le token
   ├─ Initialise notifications.py avec le webhook Discord
   └─ Initialise vacation_manager.py avec VACATION_DATES

2. PLANIFICATION
   ├─ Utilise le module 'schedule' Python
   ├─ Programme une tâche à 03:05 chaque jour
   └─ Si REMINDER_TIME défini, programme aussi à 08:00

3. BOUCLE INFINIE
   ├─ Vérifie toutes les secondes si une tâche doit s'exécuter
   ├─ À 03:05 → Lance book_next_available()
   └─ À 08:00 → Lance send_daily_reminder()

4. RÉSERVATION (à 03:05)
   ├─ Calcule date_cible = aujourd'hui + RESERVATION_DAYS_AHEAD
   ├─ vacation_manager.is_vacation(date_cible) ?
   │  ├─ Si OUI : ❌ Skip, c'est un jour de congé
   │  └─ Si NON : ✅ Continue
   ├─ oneflex_client.get_available_desks(date_cible)
   ├─ Prend le premier bureau disponible
   ├─ oneflex_client.book_desk(desk_id, date_cible)
   └─ notifications.send_success(booking_info)

5. RAPPEL MATINAL (à 08:00)
   ├─ oneflex_client.get_today_bookings()
   ├─ Si réservations trouvées :
   │  └─ notifications.send_daily_reminder(bookings)
   └─ Sinon : rien (pas de notification si pas de bureau)
```

## 🧩 Modules Externes Utilisés

### `schedule` - Planificateur de Tâches

```python
import schedule

# Programme une fonction à une heure précise
schedule.every().day.at("03:05").do(ma_fonction)

# Boucle pour exécuter les tâches
while True:
    schedule.run_pending()
    time.sleep(1)
```

**Pourquoi ?** Permet d'exécuter du code à des heures précises sans cron.

### `requests` - Requêtes HTTP

```python
import requests

# GET
response = requests.get('https://api.example.com/data')
print(response.json())

# POST avec JSON
response = requests.post(
    'https://api.example.com/create',
    json={'key': 'value'},
    headers={'Authorization': 'Bearer token'}
)
```

**Pourquoi ?** Communique avec l'API OneFlex et Discord.

### `python-dotenv` - Variables d'Environnement

```python
from dotenv import load_dotenv
import os

load_dotenv('.env')  # Charge le fichier .env
token = os.getenv('ONEFLEX_TOKEN')  # Récupère une variable
```

**Pourquoi ?** Évite de mettre les secrets dans le code.

## 🐳 Docker et Containerisation

### Pourquoi Docker ?

Docker permet d'**emballer l'application** avec toutes ses dépendances dans un "container" portable.

**Avantages :**
- ✅ Fonctionne partout (Windows, Linux, Mac, NAS)
- ✅ Pas de conflit de versions Python
- ✅ Installation simplifiée
- ✅ Isolation des processus

### Structure Docker

```dockerfile
# Dockerfile - Recette pour construire l'image

FROM python:3.11-slim    # Base : Python 3.11 léger
WORKDIR /app             # Dossier de travail dans le container
COPY requirements.txt .  # Copie les dépendances
RUN pip install -r requirements.txt  # Installe les dépendances
COPY src/ ./src/         # Copie le code source
CMD ["python", "src/main.py"]  # Commande par défaut
```

```yaml
# docker-compose.yml - Configuration du déploiement

services:
  oneflex-bot:
    build: .               # Construit l'image depuis Dockerfile
    volumes:
      - ./config:/app/config  # Monte le dossier config
    command: python src/main.py --schedule  # Lance en mode automatique
```

**Workflow Docker :**

```bash
# 1. Construire l'image
docker build -t oneflex-bot .

# 2. Lancer le container
docker run -d \
  -v ./config:/app/config \
  oneflex-bot \
  python src/main.py --schedule

# 3. Voir les logs
docker logs -f oneflex-bot
```

## 🔐 Sécurité

### Token Management

Les tokens sont **secrets** et ne doivent **jamais** être committés dans Git.

**Bonne pratique :**
```bash
# .gitignore
.env            # Ne JAMAIS versionner les secrets
.adp_config     # Ne JAMAIS versionner la config ADP
config/.env     # Ne JAMAIS versionner la config
```

**Stockage sécurisé :**
- Les tokens sont dans `config/.env` (ignoré par Git)
- Le fichier `.env.example` montre la structure sans secrets
- La config ADP (cookie + worker ID) est dans `.adp_config` avec permissions `600`

### Expiration des Tokens

Les tokens OneFlex expirent après **15 minutes** d'inactivité.

**Solution actuelle :** Renouvellement manuel
```bash
python scripts/auto_get_tokens.py
```

**Future amélioration possible :** Renouvellement automatique avec `refresh_token`.

## 📊 Gestion des Erreurs

Le bot gère plusieurs types d'erreurs :

```python
def book_desk(self, desk_id, date):
    try:
        response = requests.post(...)
        if response.status_code == 401:
            # Token expiré
            logger.error("❌ Token expiré")
            return False
        elif response.status_code == 404:
            # Bureau non trouvé
            logger.error("❌ Bureau introuvable")
            return False
        # ...
    except requests.exceptions.RequestException as e:
        # Erreur réseau
        logger.error(f"❌ Erreur réseau : {e}")
        return False
```

**Stratégies :**
- Logging détaillé avec `logger`
- Retour de valeurs explicites (`True`/`False`, tuples)
- Messages d'erreur clairs pour l'utilisateur

## 🎯 Prochaines Améliorations Possibles

1. **Tests automatisés** (`tests/`)
   - Tests unitaires pour chaque module
   - Tests d'intégration

2. **Renouvellement auto des tokens**
   - Utiliser le `refresh_token`
   - Éviter l'intervention manuelle

3. **Interface Web**
   - Dashboard pour voir les réservations
   - Configuration via UI

4. **Préférences de bureaux**
   - Favoris (bureaux préférés)
   - Blacklist (bureaux à éviter)

5. **Historique**
   - Base de données des réservations
   - Statistiques d'utilisation

## 📚 Ressources pour Aller Plus Loin

- [Python Official Docs](https://docs.python.org/3/) - Documentation Python
- [Requests Library](https://requests.readthedocs.io/) - Requêtes HTTP
- [GraphQL Introduction](https://graphql.org/learn/) - Comprendre GraphQL
- [Docker Getting Started](https://docs.docker.com/get-started/) - Apprendre Docker
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook) - API Discord

---

**Besoin d'aide ?** Consultez les autres docs dans `docs/` ou créez une issue GitHub !
