# 🎓 Guide du Débutant - OneFlex Bot

Ce guide explique comment fonctionne le bot OneFlex de manière simple et détaillée.

## 📚 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du code](#architecture-du-code)
3. [Fichiers principaux](#fichiers-principaux)
4. [Flux d'exécution](#flux-dexécution)
5. [Concepts importants](#concepts-importants)

---

## 🌟 Vue d'ensemble

Le bot OneFlex est un programme Python qui automatise la réservation de bureaux sur la plateforme OneFlex.

**Ce qu'il fait :**
- Se connecte à OneFlex avec vos tokens d'authentification
- **Renouvelle automatiquement les tokens** quand ils expirent (toutes les ~15 minutes)
- Réserve automatiquement votre bureau favori
- Peut réserver plusieurs semaines à l'avance (mode récurrent)
- Gère vos périodes de vacances (ne réserve pas pendant vos absences)
- Vous envoie des notifications Discord

**Quand il s'exécute :**
- Tous les jours à l'heure configurée (par défaut 03:05)
- Tourne dans un container Docker

---

## 🏗️ Architecture du code

```
oneflex-bot/
├── main.py                 # Point d'entrée principal, orchestre tout
├── config.py               # Chargement des variables de configuration (.env)
├── oneflex_client.py       # Communication avec l'API OneFlex
├── vacation_manager.py     # Gestion des périodes de vacances
├── notifications.py        # Envoi de notifications Discord/email
├── auto_get_tokens.py      # Outil manuel pour récupérer les tokens
├── renew_tokens.sh         # Script helper pour renouveler les tokens
├── requirements.txt        # Liste des dépendances Python
├── Dockerfile              # Instructions pour construire l'image Docker
├── docker-compose.yml      # Configuration pour lancer le container
├── .env                    # Configuration (TOKENS, HORAIRES, etc.)
└── docs/
    └── TOKEN_MANAGEMENT.md # Documentation sur les tokens
```

---

## 📄 Fichiers principaux

### 1. `config.py` - La configuration

**Rôle :** Charge toutes les variables depuis le fichier `.env`

**Pourquoi c'est important :** Au lieu d'écrire les tokens et horaires directement dans le code (dangereux et peu flexible), on les met dans un fichier `.env` que ce module charge.

**Variables clés :**
```python
TOKEN                    # Token d'authentification (expire après 15 min)
RESERVATION_TIME         # Heure d'exécution (ex: "03:05")
RESERVATION_DAYS_OF_WEEK # Jours à réserver (ex: "1,2,3,4,5" = lun-ven)
RECURRING_WEEKS          # Nombre de semaines à l'avance (ex: 4)
VACATION_DATES           # Périodes de vacances
```

### 2. `oneflex_client.py` - Le client API

**Rôle :** Communique avec l'API OneFlex (envoie des requêtes HTTP)

**Qu'est-ce qu'une API ?** C'est comme un serveur de restaurant : vous passez commande (requête) et il vous sert ce que vous demandez (réponse).

**Méthodes principales :**
- `login()` : Se connecte à OneFlex
- `get_favorite_desks()` : Récupère vos bureaux favoris
- `book_desk()` : Réserve un bureau
- `get_my_bookings()` : Liste vos réservations existantes

**Comment ça marche ?**
```python
# 1. Créer un client avec votre token
client = OneFlexClient(token="votre_token_ici")

# 2. Se connecter
client.login()

# 3. Réserver un bureau
client.book_desk(desk_id="...", space_id="...", date=datetime.now())
```

### 3. `main.py` - Le chef d'orchestre

**Rôle :** Coordonne tout le reste (configuration, client API, réservations)

**Structure :**
```python
class OneFlexBot:
    def __init__():
        # Initialisation : charge config, crée le client API
        
    def book_recurring_days():
        # Réserve plusieurs semaines de bureaux d'un coup
        # C'est la méthode la plus importante !
        
    def run_schedule():
        # Tourne en boucle, exécute les réservations à l'heure définie
```

**Flux d'exécution :**
1. Le bot démarre (`main.py` est lancé)
2. Il charge la configuration (`.env`)
3. Il programme une tâche quotidienne à l'heure définie
4. Chaque jour à cette heure, il appelle `book_recurring_days()`
5. Cette méthode réserve tous les bureaux nécessaires

### 4. `vacation_manager.py` - Gestion des vacances

**Rôle :** Évite de réserver pendant vos vacances

**Comment ça marche ?**
```python
# Configuration dans .env :
VACATION_DATES=2026-02-10:2026-02-14,2026-03-01

# Le code fait :
vacation_manager = VacationManager("2026-02-10:2026-02-14,2026-03-01")

# Vérifier si une date est en vacances :
if vacation_manager.is_vacation_day(date(2026, 2, 12)):
    print("C'est les vacances, on ne réserve pas!")
```

### 5. `notifications.py` - Notifications

**Rôle :** Envoie des messages Discord quand :
- Les réservations sont créées avec succès
- Le token a expiré (besoin de renouvellement)
- Une erreur se produit

---

## ⚙️ Flux d'exécution

### Scénario : Le bot réserve vos bureaux

```
1. Docker lance le container
   └─> Exécute: python main.py --schedule

2. main.py démarre
   ├─> Charge config.py (lit le fichier .env)
   ├─> Crée OneFlexClient (avec votre TOKEN)
   └─> Programme une tâche quotidienne à RESERVATION_TIME

3. Chaque jour à l'heure définie (ex: 03:05):
   ├─> Appelle book_recurring_days()
   ├─> Calcule les dates à réserver
   │   (ex: tous les lundis-vendredis des 4 prochaines semaines)
   ├─> Filtre les dates de vacances
   └─> Pour chaque date :
       ├─> Vérifie si déjà réservé
       ├─> Si non : appelle client.book_desk()
       └─> Si oui : skip

4. Résumé envoyé sur Discord
   └─> "✅ 20 réservations créées avec succès"
```

### Exemple concret

Aujourd'hui nous sommes le **28 janvier 2026** (mercredi).

**Configuration :**
- `RECURRING_WEEKS=4` (réserver 4 semaines)
- `RESERVATION_DAYS_OF_WEEK=1,2,3,4,5` (lundi-vendredi)
- `VACATION_DATES=2026-02-10:2026-02-14` (vacances du 10 au 14 février)

**Calcul des dates :**
```
Semaine 1: Lun 2, Mar 3, Mer 4, Jeu 5, Ven 6 février
Semaine 2: Lun 9, [10-14 = VACANCES EXCLUES], Ven 13
Semaine 3: Lun 16, Mar 17, Mer 18, Jeu 19, Ven 20
Semaine 4: Lun 23, Mar 24, Mer 25, Jeu 26, Ven 27

Total: 20 dates réservées (25 - 5 jours de vacances)
```

---

## 🧠 Concepts importants

### 1. Les Tokens d'authentification

**Qu'est-ce que c'est ?**
Un token est comme un badge d'accès temporaire. OneFlex vous le donne quand vous vous connectez.

**Problème :** Les tokens expirent après 15 minutes !

**Solution :** Le bot utilise des tokens pré-récupérés que vous devez renouveler manuellement chaque jour.

**Comment renouveler ?**
```bash
# Sur votre machine (pas dans Docker) :
python auto_get_tokens.py

# Puis copier les nouveaux tokens dans .env et redémarrer Docker
```

### 2. Le mode récurrent

Au lieu de réserver un bureau à la fois, le bot réserve **plusieurs semaines d'un coup**.

**Avantages :**
- Plus efficace (une seule exécution quotidienne)
- Vous êtes toujours réservé à l'avance
- Le bot gère automatiquement le décalage temporel

**Algorithme (simplifié) :**
```python
# Pour chaque semaine (0, 1, 2, 3):
for week in range(4):
    # Pour chaque jour (lundi=1, mardi=2, ..., vendredi=5):
    for day in [1, 2, 3, 4, 5]:
        # Calculer la date :
        # "Quel est le prochain [lundi/mardi/etc] dans X semaines ?"
        days_until = (day - today.isoweekday()) % 7
        if days_until == 0:
            days_until = 7  # Même jour → semaine suivante
        
        target_date = today + timedelta(days=days_until + week*7)
        
        # Réserver cette date (si pas en vacances)
        if not vacation_manager.is_vacation_day(target_date):
            client.book_desk(date=target_date)
```

### 3. Docker et l'isolation

**Pourquoi Docker ?**
- Le bot tourne 24/7 sans monopoliser votre PC
- Portable : marche partout (PC, NAS Synology, serveur)
- Isolé : ne pollue pas votre système

**Image vs Container :**
- **Image** = recette (Dockerfile) : comment construire le bot
- **Container** = plat préparé : instance en cours d'exécution

**Commandes utiles :**
```bash
# Voir les logs en temps réel
docker logs -f oneflex-bot

# Redémarrer le bot
docker compose restart

# Arrêter le bot
docker compose down
```

### 4. La bibliothèque `schedule`

Le bot utilise la lib `schedule` pour programmer des tâches récurrentes.

**Exemple :**
```python
import schedule

# Programmer une tâche tous les jours à 03:05
schedule.every().day.at("03:05").do(ma_fonction)

# Boucle infinie qui vérifie l'heure
while True:
    schedule.run_pending()  # Exécute les tâches si c'est l'heure
    time.sleep(60)          # Attendre 1 minute avant de revérifier
```

---

## 🎯 Points clés à retenir

1. **Le bot ne stocke PAS votre mot de passe** : il utilise des tokens temporaires
2. **Les tokens expirent** : il faut les renouveler manuellement chaque jour
3. **Le mode récurrent est intelligent** : il calcule automatiquement les dates futures
4. **Les vacances sont respectées** : le bot ne réserve jamais pendant vos absences
5. **Tout est configurable** : horaires, jours, semaines... tout est dans `.env`

---

## 🐛 Dépannage

**Le bot ne réserve rien ?**
→ Vérifiez que le token n'a pas expiré (regardez les logs)

**Je reçois des notifications "Token expiré" ?**
→ C'est normal ! Relancez `auto_get_tokens.py` pour obtenir de nouveaux tokens

**Le bot réserve les mauvais jours ?**
→ Vérifiez `RESERVATION_DAYS_OF_WEEK` dans `.env`

**Comment voir ce que fait le bot ?**
→ `docker logs -f oneflex-bot` affiche tous les logs en temps réel

---

## 📚 Ressources

- [Documentation tokens](docs/TOKEN_MANAGEMENT.md)
- [Code source sur GitHub](https://github.com/Kiwi41/oneflex-bot)
- Python : https://docs.python.org/fr/3/tutorial/
- Docker : https://docs.docker.com/get-started/

---

**Bonne chance avec votre bot ! 🚀**
