# 🤖 OneFlex Bot - Guide Complet

Bot d'automatisation des réservations de bureaux sur OneFlex.

## 📁 Structure du Projet

```
oneflex/
├── src/                      # 📦 Code source principal
│   ├── main.py              # Point d'entrée du bot
│   ├── config.py            # Configuration (charge le fichier .env)
│   ├── oneflex_client.py    # Client API OneFlex (fait les requêtes HTTP)
│   ├── notifications.py     # Système de notifications Discord
│   └── vacation_manager.py  # Gestion des congés/absences
│
├── scripts/                  # 🔧 Scripts utilitaires
│   ├── sync_vacations_adp.py    # Synchronise les congés depuis ADP
│   ├── import_vacations.py      # Importe les congés depuis texte
│   ├── auto_get_tokens.py       # Récupère automatiquement les tokens
│   └── deploy-to-nas.sh         # Déploie le bot sur Synology NAS
│
├── docs/                     # 📚 Documentation
│   ├── GUIDE_DEBUTANT.md    # Guide pour les débutants
│   ├── NOTIFICATIONS.md      # Configuration des notifications
│   ├── README-DEPLOY.md      # Guide de déploiement
│   ├── SYNOLOGY.md          # Déploiement sur Synology NAS
│   ├── GET_TOKEN.md         # Comment obtenir les tokens
│   ├── VACATIONS.md         # Gestion des congés
│   └── DOCKER.md            # Utilisation avec Docker
│
├── config/                   # ⚙️ Configuration
│   ├── .env.example         # Exemple de configuration
│   └── .env                 # Votre configuration (non versionné)
│
├── tests/                    # ✅ Tests (à venir)
│
├── docker-compose.yml        # Configuration Docker locale
├── docker-compose.ghcr.yml   # Configuration Docker avec image GitHub
├── Dockerfile               # Construction de l'image Docker
├── requirements.txt         # Dépendances Python
├── CHANGELOG.md            # Historique des versions
└── README.md               # Ce fichier
```

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.11+ OU Docker
- Un compte OneFlex
- (Optionnel) Un webhook Discord pour les notifications

### Installation Locale (sans Docker)

```bash
# 1. Cloner le repository
git clone https://github.com/votre-user/oneflex-bot.git
cd oneflex-bot

# 2. Créer un environnement virtuel Python
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OU
.venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer
cp config/.env.example config/.env
nano config/.env  # Éditez avec vos paramètres

# 5. Obtenir votre token OneFlex
# Suivez le guide: docs/GET_TOKEN.md

# 6. Lancer le bot
python src/main.py --schedule
```

### Installation avec Docker

```bash
# 1. Cloner et configurer
git clone https://github.com/votre-user/oneflex-bot.git
cd oneflex-bot
cp config/.env.example config/.env
nano config/.env  # Éditez avec vos paramètres

# 2. Démarrer avec Docker Compose
docker compose up -d

# 3. Voir les logs
docker logs -f oneflex-bot
```

## 📖 Guide de Configuration

### Fichier `.env` - Les Essentiels

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OBLIGATOIRE : Token OneFlex
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONEFLEX_TOKEN=votre_token_ici

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Horaires (format HH:MM)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESERVATION_TIME=03:05        # Heure de réservation automatique
REMINDER_TIME=08:00           # Heure du rappel matinal (vide = désactivé)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Réservation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECURRING_WEEKS=4             # Nombre de semaines à réserver d'avance
RESERVATION_DAYS_OF_WEEK=1,2,3,4,5  # Lundi à vendredi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Notifications Discord (optionnel)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/...

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Congés (géré automatiquement par sync_vacations_adp.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VACATION_DATES=2026-02-10:2026-02-14,2026-03-01
AUTO_CANCEL_VACATIONS=true   # Annule automatiquement les réservations pendant les congés
```

### Modes d'Exécution

```bash
# Mode 1: Exécution planifiée (bot continu)
# Le bot tourne en permanence et exécute la réservation à RESERVATION_TIME
python src/main.py --schedule

# Mode 2: Réservation unique pour une date
# Réserve seulement pour le 15 février 2026 puis s'arrête
python src/main.py --date 2026-02-15

# Mode 3: Réservation récurrente immédiate
# Réserve RECURRING_WEEKS semaines d'avance puis s'arrête
python src/main.py --recurring

# Mode 4: Forcer une réservation même si déjà existante
python src/main.py --date 2026-02-15 --force
```

## 🛠️ Scripts Utilitaires

### 1. Synchronisation des Congés depuis ADP

```bash
# Première utilisation : sauvegarder le cookie ADP
python scripts/sync_vacations_adp.py --cookie "votre_cookie" --save-cookie

# Utilisations suivantes : le cookie est automatiquement lu depuis .adp_cookie
python scripts/sync_vacations_adp.py

# Le script met à jour automatiquement VACATION_DATES dans config/.env
```

**Comment obtenir le cookie ADP :**
1. Ouvrez https://mon.adp.com dans Chrome
2. F12 → Onglet "Application" → Cookies → https://mon.adp.com
3. Trouvez `EMEASMSESSION` et copiez la valeur

### 2. Import Manuel des Congés (depuis texte)

```bash
# Si vous avez copié le texte depuis le portail RH dans un fichier
python scripts/import_vacations.py < mes_conges.txt
```

### 3. Obtention Automatique des Tokens

```bash
# Ouvre un navigateur automatique pour récupérer les tokens
python scripts/auto_get_tokens.py
```

## 📊 Notifications Discord

Le bot envoie 3 types de notifications :

### 1. ✅ Réservation Réussie
```
✅ OneFlex Bot - Réservation confirmée

📅 Lundi 15 février 2026
🏢 Bureau : Desk-A-123
📍 Espace : Open Space Nord - Zone A
⏰ Moment : Journée complète (09:00 - 18:00)
```

### 2. ☀️ Rappel Matinal
```
☀️ Bonjour ! Votre bureau aujourd'hui

📅 Lundi 15 février 2026
🏢 Bureau : Desk-A-123
📍 Espace : Open Space Nord - Zone A
⏰ Moment : Journée complète
```

### 3. 🏝️ Congés Annulés
```
🏝️ OneFlex Bot - Réservations annulées

Les réservations suivantes ont été annulées :

📅 10/02/2026 - Matin, Après-midi
📅 11/02/2026 - Matin, Après-midi
📅 12/02/2026 - Matin, Après-midi

Bonnes vacances ! 🌴
```

## 🔍 Comprendre le Code

### Architecture Simplifiée

```
┌─────────────────────────────────────────────────────┐
│                   src/main.py                       │
│            (Point d'entrée principal)               │
│  - Parse les arguments (--schedule, --date, etc.)  │
│  - Lance le bot selon le mode choisi               │
└───────────────┬────────────────────────────────────┘
                │
                ├──► src/config.py
                │    (Charge les variables depuis .env)
                │
                ├──► src/oneflex_client.py
                │    (Communique avec l'API OneFlex)
                │    - get_available_desks()
                │    - book_desk()
                │    - cancel_booking()
                │
                ├──► src/notifications.py
                │    (Envoie les messages Discord)
                │    - send_success()
                │    - send_daily_reminder()
                │
                └──► src/vacation_manager.py
                     (Gère les périodes de congés)
                     - is_vacation()
                     - cancel_vacation_bookings()
```

### Flux d'Exécution Typique

```
1. Le bot démarre à RESERVATION_TIME (ex: 03:05)
   ↓
2. Calcule la date cible (aujourd'hui + RESERVATION_DAYS_AHEAD)
   ↓
3. Vérifie si c'est un jour de congé (VACATION_DATES)
   ↓
4. Cherche les bureaux disponibles (oneflex_client.get_available_desks)
   ↓
5. Réserve le premier bureau trouvé (oneflex_client.book_desk)
   ↓
6. Envoie une notification Discord ✅
   ↓
7. À REMINDER_TIME (ex: 08:00), envoie un rappel ☀️
```

## 🐛 Résolution de Problèmes

### Token Expiré

```bash
# Erreur : "Authentication failed" ou "401 Unauthorized"
# Solution : Obtenir un nouveau token

python scripts/auto_get_tokens.py
# OU manuellement suivez docs/GET_TOKEN.md
```

### Aucun Bureau Disponible

```bash
# Le bot ne trouve pas de bureau disponible
# Causes possibles :
# - Tous les bureaux sont réservés (arrivez plus tôt)
# - Mauvaise configuration des filtres (SITE_ID, FLOOR_ID)
# - Token expiré

# Solution : Vérifier les logs
docker logs oneflex-bot
```

### Cookie ADP Expiré

```bash
# Le script sync_vacations_adp.py retourne une erreur 401
# Solution : Obtenir un nouveau cookie

python scripts/sync_vacations_adp.py --cookie "nouveau_cookie" --save-cookie
```

## 📚 Documentation Complète

- [Guide Débutant](docs/GUIDE_DEBUTANT.md) - Pour bien démarrer
- [Obtenir le Token](docs/GET_TOKEN.md) - Comment récupérer le token OneFlex
- [Notifications](docs/NOTIFICATIONS.md) - Configuration Discord
- [Gestion des Congés](docs/VACATIONS.md) - Synchronisation ADP
- [Déploiement](docs/README-DEPLOY.md) - Options de déploiement
- [Synology NAS](docs/SYNOLOGY.md) - Installation sur NAS
- [Docker](docs/DOCKER.md) - Utilisation avancée de Docker

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des améliorations
- 📖 Améliorer la documentation

## 📜 Licence

MIT License - Voir [LICENSE](LICENSE)

## 🙏 Crédits

Développé avec ❤️ pour automatiser les réservations OneFlex.

---

**Version actuelle :** 1.9.0  
**Dernière mise à jour :** Janvier 2026
