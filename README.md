# Bot de Réservation OneFlex

Bot Python pour automatiser la réservation de places de travail sur OneFlex avec support SSO.

## ✨ Fonctionnalités

- ✅ **Connexion SSO** avec authentification par token
- ✅ **Réservation automatique** de votre bureau favori avec **fallback** si occupé
- ✅ **Réservation récurrente** par jours de semaine (ex: tous les Lundi/Mercredi/Vendredi)
- ✅ **Gestion des vacances** : exclusion et annulation automatique des réservations (voir [VACATIONS.md](docs/VACATIONS.md))
- ✅ **Planification** des réservations quotidiennes
- ✅ **Affichage** de vos réservations actuelles
- ✅ **Réservation pour une date spécifique**
- ✅ **Support Docker** pour déploiement sur Synology NAS
- ✅ **Notifications Discord** pour les événements importants

## ✅ Gestion des tokens

**Bonne nouvelle :** Le bot renouvelle automatiquement les tokens quand ils expirent !

Les tokens OneFlex ont une durée de vie courte (~15 minutes), mais grâce au `refresh_token`, 
le bot les renouvelle automatiquement en arrière-plan. Vous n'avez rien à faire.

Voir la documentation complète : [TOKEN_MANAGEMENT.md](docs/TOKEN_MANAGEMENT.md)

### Configuration initiale uniquement

Vous devez récupérer vos tokens **une seule fois** lors de l'installation :

```bash
# Méthode simple
python auto_get_tokens.py
cp .env config/.env
docker compose up -d
```

Après cela, le bot gère tout automatiquement ! ✨

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

#### Méthode automatique (Recommandée)

Utilisez le script automatisé :

```bash
python auto_get_tokens.py
```

Le script va :
- Ouvrir Chrome automatiquement
- Attendre que vous vous connectiez via SSO
- Récupérer automatiquement les tokens
- Mettre à jour votre `.env` directement

#### Méthode manuelle

Consultez le guide détaillé dans [GET_TOKEN.md](GET_TOKEN.md) ou :

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
- **RESERVATION_TIME** : Heure de la réservation automatique quotidienne (format HH:MM, ex: `03:05`)
- **RESERVATION_DAYS_AHEAD** : Nombre de jours à l'avance pour réserver (par défaut 7)
- **RESERVATION_DAYS_OF_WEEK** : Jours de la semaine pour réservation récurrente (ex: `1,3,5` pour Lundi, Mercredi, Vendredi)
  - `1` = Lundi, `2` = Mardi, `3` = Mercredi, `4` = Jeudi, `5` = Vendredi, `6` = Samedi, `7` = Dimanche
- **RECURRING_WEEKS** : Nombre de semaines à réserver à l'avance en mode `--schedule` (0 = désactivé, défaut 0)

## 🚀 Utilisation

### Réserver automatiquement

Réserve votre bureau favori selon `RESERVATION_DAYS_AHEAD` (7 jours par défaut) :

```bash
python main.py
```

### Réserver pour une date spécifique

```bash
# Réserver pour une date (bloquée si vacances configurées)
python main.py --date 2026-03-15

# Forcer la réservation même pendant les vacances
python main.py --date 2026-03-15 --force
```

**Note** : Si la date est dans une période de vacances configurée (`VACATION_DATES`), la réservation sera bloquée avec un message d'avertissement. Utilisez `--force` pour passer outre.

### Afficher vos réservations

```bash
python main.py --show
```

### Réservation récurrente (jours spécifiques)

Réserve automatiquement selon les jours de la semaine configurés dans `RESERVATION_DAYS_OF_WEEK`.

**Configuration dans `.env`** :
```bash
# Réserver tous les Lundis, Mercredis et Vendredis
RESERVATION_DAYS_OF_WEEK=1,3,5
```

**Exécution** :
```bash
# Réserver pour 4 semaines (défaut)
python main.py --recurring

# Réserver pour 8 semaines
python main.py --recurring 8
```

Exemples de configurations :
- `1,3,5` : Lundi, Mercredi, Vendredi
- `2,4` : Mardi, Jeudi
- `1,2,3,4,5` : Tous les jours de la semaine

### Mode automatique quotidien

Lance le bot en mode planifié (s'exécute automatiquement chaque jour à l'heure configurée) :

```bash
python main.py --schedule
```

**Mode standard** : Réserve pour J+RESERVATION_DAYS_AHEAD chaque jour

**Mode récurrent** : Si `RECURRING_WEEKS` > 0, réserve automatiquement pour N semaines à l'avance selon les jours configurés dans `RESERVATION_DAYS_OF_WEEK`

**Exemple de configuration pour réservation récurrente** :
```bash
RESERVATION_TIME=03:05
RESERVATION_DAYS_OF_WEEK=1,2,3,4,5  # Lundi à Vendredi
RECURRING_WEEKS=4  # 4 semaines à l'avance
```

Avec cette config, le bot va réserver automatiquement les 4 prochaines semaines (20 jours) chaque jour à 3h05.

## 🔄 Rafraîchissement automatique du token

Avec le `ONEFLEX_REFRESH_TOKEN` configuré, le bot :
- ✅ Détecte automatiquement quand le token expire
- ✅ Rafraîchit le token d'accès automatiquement
- ✅ Sauvegarde le nouveau token dans le fichier `.env`
- ✅ Continue l'exécution sans interruption

**Vous n'avez plus besoin de mettre à jour manuellement le token !**

## 🏖️ Gestion des vacances

Le bot peut automatiquement gérer vos périodes de vacances :
- 🚫 **Exclure** les jours de vacances des réservations récurrentes
- 🗑️ **Annuler automatiquement** les réservations existantes pendant vos absences
- ⚠️ **Bloquer** les réservations manuelles sur des dates en vacances

**Configuration dans `.env`** :
```bash
# Périodes de vacances (format: YYYY-MM-DD:YYYY-MM-DD)
VACATION_DATES=2026-02-10:2026-02-14,2026-04-13:2026-04-24

# Annulation automatique des réservations existantes
AUTO_CANCEL_VACATIONS=true
```

📖 **Guide complet** : [VACATIONS.md](VACATIONS.md)

## � Fallback automatique des bureaux

Si votre bureau favori principal est déjà réservé, le bot essaie **automatiquement** vos autres bureaux favoris dans l'ordre de préférence.

### Comment ça fonctionne

Le bot récupère vos bureaux dans cet ordre :
1. **Bureaux marqués comme favoris** dans OneFlex
2. **Bureaux les plus réservés** (par ordre décroissant)

### Exemple d'exécution

```
📌 Bureau favori principal: Bureau COP-0-05 (+2 alternative(s))
🎯 Essai du bureau principal: Bureau COP-0-05
⚠️ Bureau occupé, essai du suivant...
🔄 Essai du bureau alternatif #1: Bureau CP-0-33
✅ Réservation confirmée!
```

### Configuration

Aucune configuration nécessaire ! Le bot :
- ✅ Utilise automatiquement vos favoris OneFlex
- ✅ Analyse votre historique de réservations
- ✅ Essaie tous vos bureaux jusqu'à trouver un disponible

**💡 Astuce** : Marquez plusieurs bureaux comme favoris dans OneFlex pour augmenter vos chances de réservation.

## �🐳 Déploiement Docker sur Synology NAS

Le bot peut être déployé sur un NAS Synology avec Docker. Consultez le guide complet : **[SYNOLOGY.md](SYNOLOGY.md)**

### Installation rapide

```bash
# Cloner le projet sur votre NAS
git clone https://github.com/Kiwi41/oneflex-bot.git
cd oneflex-bot

# Créer la configuration
mkdir -p config
cp .env.example config/.env
# Éditer config/.env avec vos tokens

# Lancer avec Docker Compose
docker-compose up -d
```

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
