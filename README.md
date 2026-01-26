# Bot de Réservation OneFlex

Bot Python pour automatiser la réservation de places de travail sur OneFlex avec support SSO et rafraîchissement automatique du token.

## ✨ Fonctionnalités

- ✅ **Connexion SSO** avec authentification par token
- ✅ **Rafraîchissement automatique** du token d'accès (plus besoin de le mettre à jour manuellement)
- ✅ **Réservation automatique** de votre bureau favori
- ✅ **Planification** des réservations quotidiennes
- ✅ **Affichage** de vos réservations actuelles
- ✅ **Réservation pour une date spécifique**

## 📦 Installation

1. Cloner le repository
2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurer vos tokens OneFlex (voir section Configuration)

## ⚙️ Configuration

### 1. Copier le fichier de configuration

```bash
cp .env.example .env
```

### 2. Récupérer vos tokens OneFlex

Consultez le guide détaillé dans [GET_TOKEN.md](GET_TOKEN.md) pour récupérer vos tokens.

**En résumé** :
1. Connectez-vous sur https://oneflex.myworldline.com
2. Ouvrez les outils développeur (F12)
3. Allez dans **Application** > **Cookies** > `https://oneflex.myworldline.com`
4. Copiez les valeurs de :
   - `access_token`
   - `refresh_token`

### 3. Configurer le fichier .env

Éditez le fichier `.env` :

```bash
# Tokens d'authentification (requis)
ONEFLEX_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ONEFLEX_REFRESH_TOKEN=de24ee12d9703f31ccf1

# Paramètres de réservation (optionnel)
RESERVATION_TIME=09:00
RESERVATION_DAYS_AHEAD=7
```

### Options de configuration

- **ONEFLEX_TOKEN** : Token d'accès (expire après 15 minutes)
- **ONEFLEX_REFRESH_TOKEN** : Token de rafraîchissement (durée longue) - **Recommandé**
- **RESERVATION_TIME** : Heure de la réservation automatique quotidienne (format HH:MM)
- **RESERVATION_DAYS_AHEAD** : Nombre de jours à l'avance pour réserver (par défaut 7)

## 🚀 Utilisation

### Réserver automatiquement

Réserve votre bureau favori selon `RESERVATION_DAYS_AHEAD` (7 jours par défaut) :

```bash
python main.py
```

### Réserver pour une date spécifique

```bash
python main.py --date 2026-03-15
```

### Afficher vos réservations

```bash
python main.py --show
```

### Mode automatique quotidien

Lance le bot en mode planifié (s'exécute automatiquement chaque jour à l'heure configurée) :

```bash
python main.py --schedule
```

## 🔄 Rafraîchissement automatique du token

Avec le `ONEFLEX_REFRESH_TOKEN` configuré, le bot :
- ✅ Détecte automatiquement quand le token expire
- ✅ Rafraîchit le token d'accès automatiquement
- ✅ Sauvegarde le nouveau token dans le fichier `.env`
- ✅ Continue l'exécution sans interruption

**Vous n'avez plus besoin de mettre à jour manuellement le token !**

## 🤖 Automatisation avec Cron

Pour exécuter le bot automatiquement chaque jour :

```bash
crontab -e
```

Ajoutez cette ligne (exemple : exécution à 9h du matin) :

```cron
0 9 * * * cd /home/a154355/git/perso/oneflex && .venv/bin/python main.py
```

Ou utilisez le mode `--schedule` :

```bash
# Lancer en arrière-plan avec nohup
nohup python main.py --schedule > bot.log 2>&1 &
```

## 📋 Exemples d'utilisation

### Réserver pour demain
```bash
python main.py --date $(date -d "+1 day" +%Y-%m-%d)
```

### Réserver pour toute la semaine prochaine
```bash
for i in {1..5}; do
  python main.py --date $(date -d "+$i day" +%Y-%m-%d)
done
```

### Vérifier mes réservations
```bash
python main.py --show
```

## 🔧 Bureau favori

Le bot identifie automatiquement votre bureau favori en analysant vos réservations passées :
- Il sélectionne le bureau que vous avez réservé le plus souvent
- Si vous avez configuré des bureaux favoris dans OneFlex, il les utilise en priorité

Pour forcer un bureau spécifique, ajoutez dans `.env` :
```bash
ONEFLEX_DESK_ID=edbb6ebe-ff94-4322-bf0c-b02bebad7ec7
ONEFLEX_SPACE_ID=cd973815-041c-4a53-bf1d-f1b4582e4c3d
ONEFLEX_DESK_NAME=Mon bureau préféré
```

## 📝 Notes

- Le bot réserve automatiquement pour **toute la journée** (matin + après-midi)
- Si vous avez déjà une réservation pour la date demandée, le bot détectera le conflit
- Le `refresh_token` a une durée de vie longue mais peut aussi expirer (plusieurs jours/semaines)

## 🐛 Dépannage

### "Token invalide ou expiré"

1. Vérifiez que votre `ONEFLEX_REFRESH_TOKEN` est configuré
2. Si le problème persiste, reconnectez-vous sur OneFlex et récupérez de nouveaux tokens

### "Impossible de trouver un bureau favori"

1. Assurez-vous d'avoir déjà fait des réservations sur OneFlex
2. Ou configurez manuellement `ONEFLEX_DESK_ID` et `ONEFLEX_SPACE_ID` dans `.env`

### Le bot ne se lance pas automatiquement

1. Vérifiez votre configuration cron : `crontab -l`
2. Vérifiez les logs : consultez le fichier `bot.log` si vous utilisez nohup
3. Testez la commande manuellement d'abord

## 📄 Licence

Ce bot est un projet personnel et n'est pas affilié à OneFlex ou Worldline.

## ⚠️ Avertissement

Utilisez ce bot de manière responsable et conformément aux politiques de votre entreprise concernant l'automatisation des réservations.
