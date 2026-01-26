# Déploiement sur Synology NAS avec Docker

Ce guide explique comment déployer le bot OneFlex sur un NAS Synology en utilisant Docker.

## 📋 Prérequis

1. **Docker** installé sur votre Synology (via le Package Center)
2. **Accès SSH** au NAS (optionnel mais recommandé)
3. Un **dossier partagé** pour stocker le projet

## 🚀 Installation

### Méthode 1 : Via SSH (Recommandé)

#### 1. Se connecter au NAS

```bash
ssh votre_utilisateur@ip_du_nas
```

#### 2. Cloner le projet

```bash
cd /volume1/docker  # ou votre dossier docker préféré
git clone https://github.com/Kiwi41/oneflex-bot.git
cd oneflex-bot
```

#### 3. Créer la structure de configuration

```bash
mkdir -p config
cp .env.example config/.env
```

#### 4. Configurer le fichier .env

```bash
nano config/.env
# ou
vim config/.env
```

Ajoutez vos tokens OneFlex :
```bash
ONEFLEX_TOKEN=votre_token_ici
ONEFLEX_REFRESH_TOKEN=votre_refresh_token_ici
RESERVATION_TIME=09:00
RESERVATION_DAYS_AHEAD=7

# Optionnel : pour réservation récurrente (ex: Lundi, Mercredi, Vendredi)
RESERVATION_DAYS_OF_WEEK=1,3,5
```

#### 5. Construire et lancer le container

```bash
docker-compose build
docker-compose up -d
```

### Méthode 2 : Via Synology Docker GUI

#### 1. Télécharger le projet

Téléchargez le projet depuis GitHub et décompressez-le dans un dossier partagé Synology (ex: `/docker/oneflex-bot`)

#### 2. Préparer la configuration

1. Créez un dossier `config` dans `/docker/oneflex-bot`
2. Copiez `.env.example` vers `config/.env`
3. Éditez `config/.env` avec vos tokens OneFlex

#### 3. Ouvrir Docker dans DSM

1. Ouvrez **Docker** depuis le menu des applications
2. Allez dans l'onglet **Image**
3. Cliquez sur **Ajouter** > **Ajouter depuis un fichier**
4. Sélectionnez le `Dockerfile` du projet
5. Nommez l'image `oneflex-bot` et cliquez sur **Construire**

#### 4. Créer le container

1. Une fois l'image construite, allez dans l'onglet **Container**
2. Cliquez sur **Créer**
3. Sélectionnez l'image `oneflex-bot`
4. Configurez le container :

**Paramètres généraux :**
- Nom : `oneflex-bot`
- ✅ Activer le redémarrage automatique

**Paramètres de volume :**
- Dossier local : `/docker/oneflex-bot/config`
- Point de montage : `/app/config`
- Mode : Lecture seule

**Variables d'environnement :**
- `TZ` = `Europe/Paris`

**Commande (optionnelle) :**
- Par défaut : `python main.py` (exécution unique)
- Mode continu : `python main.py --schedule`

5. Cliquez sur **Appliquer** puis **Suivant** et **Terminé**

## ⚙️ Modes d'exécution

### Mode recommandé : Bot en continu avec --schedule

Le bot tourne en permanence et réserve automatiquement chaque jour à l'heure configurée (RESERVATION_TIME).

**Avantages :**
- ✅ Automatique : pas besoin de Task Scheduler
- ✅ Simple : un seul container qui tourne en continu
- ✅ Fiable : restart automatique en cas d'erreur

**Configuration :**
Le [docker-compose.yml](docker-compose.yml) est déjà configuré avec `command: python main.py --schedule`

Le bot :
1. Vérifie chaque jour à l'heure configurée (ex: 08:00)
2. Réserve pour J+N jours (selon RESERVATION_DAYS_AHEAD)
3. Utilise les jours configurés dans RESERVATION_DAYS_OF_WEEK
4. Redémarre automatiquement en cas d'erreur

### Mode alternatif : Exécution quotidienne avec Task Scheduler

Si vous préférez contrôler l'exécution via Synology Task Scheduler :

**Configuration du container :**
Modifiez [docker-compose.yml](docker-compose.yml) :
```yaml
# Retirer la ligne command pour utiliser le comportement par défaut
# command: python main.py --schedule
```

**Configuration Task Scheduler :**
1. Ouvrez **Panneau de configuration** > **Planificateur de tâches**
2. Créez une nouvelle tâche : **Créer** > **Tâche planifiée** > **Script défini par l'utilisateur**
3. Configurez :
   - **Nom** : Réservation OneFlex
   - **Utilisateur** : root
   - **Planification** : Quotidienne à 09:00 (ou l'heure souhaitée)
   - **Script** :
   ```bash
   docker start oneflex-bot
   ```

## 📊 Surveillance et logs
```bash
docker run -d \
  --name oneflex-bot \
  --restart unless-stopped \
  -v /volume1/docker/oneflex-bot/config/.env:/app/config/.env:ro \
  -e TZ=Europe/Paris \
  oneflex-bot \
  python main.py --schedule
```

## 📊 Surveillance et logs

### Voir les logs en temps réel

Via SSH :
```bash
docker logs -f oneflex-bot
```

Via Docker GUI :
1. Ouvrez **Docker**
2. Onglet **Container**
3. Sélectionnez `oneflex-bot`
4. Cliquez sur **Détails** > **Journal**

### Vérifier que le bot tourne

```bash
docker ps | grep oneflex-bot
```

Vous devriez voir :
```
CONTAINER ID   IMAGE          STATUS                  PORTS     NAMES
abc123def456   oneflex-bot    Up 2 hours                        oneflex-bot
```

### Redémarrer le container

```bash
docker restart oneflex-bot
```

### Arrêter le container

```bash
docker stop oneflex-bot
```

### Mettre à jour le bot

```bash
cd /volume1/docker/oneflex-bot
git pull
docker-compose build
docker-compose down
docker-compose up -d
```

## 🔄 Rafraîchissement du token

Le bot rafraîchit automatiquement le token d'accès quand il expire, **mais** le fichier `.env` dans le container est en **lecture seule** pour des raisons de sécurité.

**Solutions :**

### Option A : Token longue durée (Recommandé)
Le `refresh_token` a une durée de vie longue (plusieurs semaines). Renouvelez-le manuellement quand il expire.

### Option B : Volume en lecture/écriture
Montez le volume en mode lecture/écriture pour permettre la mise à jour automatique :

```yaml
volumes:
  - ./config/.env:/app/config/.env  # sans :ro
```

### Option C : Renouvellement manuel périodique
Créez une tâche planifiée pour mettre à jour les tokens régulièrement (ex: tous les 7 jours).

## 🐛 Dépannage

### Le container ne démarre pas

```bash
docker logs oneflex-bot
```

Vérifiez :
- Le fichier `.env` existe dans `config/`
- Les tokens sont valides
- Les permissions du dossier sont correctes

### "Token invalide ou expiré"

1. Récupérez un nouveau token depuis OneFlex
2. Éditez `config/.env` avec le nouveau token
3. Redémarrez le container :
   ```bash
   docker restart oneflex-bot
   ```

### Le bot ne réserve pas

Vérifiez :
- Les logs du container : `docker logs oneflex-bot`
- La configuration de `RESERVATION_DAYS_AHEAD` dans `.env`
- Que vous n'avez pas déjà une réservation pour cette date

## 📝 Exemples de commandes

### Réserver manuellement pour demain
```bash
docker exec oneflex-bot python main.py --date $(date -d "+1 day" +%Y-%m-%d)
```

### Voir mes réservations
```bash
docker exec oneflex-bot python main.py --show
```

### Réserver pour une date spécifique
```bash
docker exec oneflex-bot python main.py --date 2026-03-15
```

### Réservation récurrente (selon RESERVATION_DAYS_OF_WEEK)

Configurez d'abord les jours dans `config/.env` :
```bash
# Exemple : tous les Lundis, Mercredis, Vendredis
RESERVATION_DAYS_OF_WEEK=1,3,5
```

Puis exécutez :
```bash
# Réserver pour 4 semaines (par défaut)
docker exec oneflex-bot python main.py --recurring

# Réserver pour 8 semaines
docker exec oneflex-bot python main.py --recurring 8
```

### Automatiser les réservations récurrentes

Dans le Task Scheduler Synology, créez une tâche hebdomadaire :
```bash
# Tous les dimanches à 20h00, réserver pour les 4 prochaines semaines
docker exec oneflex-bot python main.py --recurring 4
```

## 🔒 Sécurité

- Le fichier `.env` contenant vos tokens doit être protégé
- Utilisez les permissions appropriées : `chmod 600 config/.env`
- Ne commitez **jamais** le fichier `.env` dans git
- Le `.gitignore` est déjà configuré pour l'ignorer

## 🆘 Support

Pour toute question ou problème :
1. Consultez les logs : `docker logs oneflex-bot`
2. Vérifiez le [README.md](README.md) principal
3. Consultez [GET_TOKEN.md](GET_TOKEN.md) pour les problèmes de tokens
