# 🏖️ Gestion des Vacances et Absences

Le bot OneFlex peut automatiquement gérer vos périodes de vacances :
- **Ne pas réserver** pendant vos absences
- **Annuler automatiquement** les réservations existantes pendant vos vacances
- **Synchroniser automatiquement** vos congés depuis l'API ADP

---

## 🚀 Méthode Recommandée : Synchronisation ADP Automatique

### Script `sync_vacations_adp.py`

Le moyen le plus simple et fiable pour gérer vos congés est d'utiliser le script de synchronisation ADP qui récupère directement vos congés depuis votre portail RH.

#### Installation Initiale

```bash
# 1. Obtenir votre cookie de session ADP
# Ouvrez https://mon.adp.com dans Chrome
# F12 → Application → Cookies → https://mon.adp.com
# Copiez la valeur de 'EMEASMSESSION'

# 2. Obtenir votre Worker ID
# Trouvez votre ID dans l'URL de votre profil ADP
# Exemple: https://mon.adp.com/.../workers/jdupont-abc/...
# L'ID est: jdupont-abc

# 3. Sauvegarder la configuration (une seule fois)
python scripts/sync_vacations_adp.py \
  --cookie "votre_cookie_ici" \
  --worker-id "votre_id_ici" \
  --save-config

# ✅ Configuration sauvegardée dans .adp_config
```

#### Utilisation

```bash
# Lancer la synchronisation
python scripts/sync_vacations_adp.py
```

**Résultat :**
```
🔄 Synchronisation des congés depuis ADP
==================================================

📡 Connexion à l'API ADP...
✅ 74 demande(s) de congé(s) récupérée(s)

🔍 Filtrage des congés approuvés...
✅ 66 période(s) approuvée(s):

  • 30/01/2025 → 31/01/2025
  • 05/02/2025
  • 13/02/2025 → 21/02/2025
  ...

📝 Format pour le bot:
  VACATION_DATES=2025-01-30:2025-01-31,2025-02-05,...

💾 Mise à jour de config/.env...
✅ config/.env mis à jour avec succès!

🚀 Prochaines étapes:
  1. Redémarrez le bot: docker compose restart
  2. Ou attendez la prochaine exécution automatique
```

#### Avantages

- ✅ **Automatique** : Récupère tous vos congés approuvés
- ✅ **À jour** : Synchronise depuis la source officielle
- ✅ **Fiable** : Format JSON structuré (pas de copier-coller)
- ✅ **Complet** : Toutes les périodes en une commande

#### Cookie Expiré ?

Si vous obtenez une erreur 401 :

```bash
# Le script vous guidera :
❌ Session expirée - Cookie invalide ou expiré

Pour mettre à jour le cookie EMEASMSESSION:
  1. Ouvrez https://mon.adp.com dans Chrome
  2. Connectez-vous si nécessaire
  3. F12 > Application > Cookies > https://mon.adp.com
  4. Copiez la valeur de 'EMEASMSESSION'
  5. Relancez: python scripts/sync_vacations_adp.py --cookie 'nouveau_cookie' --save-config
```

#### Automatisation

Vous pouvez ajouter un cron pour synchroniser automatiquement :

```bash
# Synchroniser tous les lundis à 8h
0 8 * * 1 cd /chemin/oneflex && python scripts/sync_vacations_adp.py && docker compose restart
```

---

## 📝 Méthode Alternative : Configuration Manuelle

Si vous ne pouvez pas utiliser l'API ADP, vous pouvez configurer manuellement.

### Format des dates

Dans votre fichier `.env`, ajoutez vos périodes de vacances :

```bash
# Une seule période
VACATION_DATES=2026-02-10:2026-02-14

# Plusieurs périodes séparées par des virgules
VACATION_DATES=2026-02-10:2026-02-14,2026-03-01:2026-03-07,2026-04-15:2026-04-22

# Jours uniques (sans période)
VACATION_DATES=2026-02-14,2026-03-15,2026-04-01

# Mixte (périodes et jours uniques)
VACATION_DATES=2026-02-10:2026-02-14,2026-03-15,2026-04-01:2026-04-07
```

### Format

- **Période** : `YYYY-MM-DD:YYYY-MM-DD` (date début : date fin)
- **Jour unique** : `YYYY-MM-DD`
- **Séparateur** : `,` (virgule entre les périodes)

### Annulation automatique

```bash
# Annuler les réservations existantes pendant les vacances
AUTO_CANCEL_VACATIONS=true

# Ne pas annuler (juste éviter de nouvelles réservations)
AUTO_CANCEL_VACATIONS=false
```

---

## 🛠️ Import depuis Texte (Méthode Manuelle Alternative)

Si vous avez copié le texte depuis le portail RH :

```bash
# 1. Copiez le texte des congés dans un fichier
nano mes_conges.txt

# 2. Lancez l'import
python scripts/import_vacations.py < mes_conges.txt
```

**Format du texte attendu :**
```
Type de congé: RTT salarié
Période: Du 30 octobre 2025 Au 31 octobre 2025
Statut: Approuvé

Type de congé: RTT salarié
Date: 3 novembre 2025
Statut: Approuvé
```

Le script parse automatiquement les dates françaises et met à jour `config/.env`.

---

## ✨ Fonctionnalités

### 1. Exclusion des réservations

Le bot **n'inclura PAS** les jours de vacances dans plusieurs modes :

#### Mode récurrent (`--recurring`)

Lors de la réservation récurrente, les jours de vacances sont automatiquement exclus :

```bash
python main.py --recurring 4
```

Exemple de sortie :
```
🏖️ 5 jour(s) de vacances exclu(s)
   ⊗ 10/02/2026 - Vacances
   ⊗ 11/02/2026 - Vacances
   ⊗ 12/02/2026 - Vacances
   ⊗ 13/02/2026 - Vacances
   ⊗ 14/02/2026 - Vacances
```

#### Mode date spécifique (`--date`)

Essayer de réserver une date pendant les vacances est **bloqué** avec un message d'avertissement :

```bash
python main.py --date 2026-02-10
```

Sortie :
```
⚠️ La date 10/02/2026 est pendant vos vacances configurées.
💡 Utilisez --force si vous voulez réserver quand même.
```

Pour forcer quand même :
```bash
python main.py --date 2026-02-10 --force
```

### 2. Annulation automatique

Avec `AUTO_CANCEL_VACATIONS=true`, le bot annule automatiquement les réservations existantes pendant vos vacances.

#### En mode récurrent (`--recurring`)

Avant de créer les nouvelles réservations, le bot annule automatiquement celles qui tombent pendant les vacances :

```bash
python main.py --recurring 4
```

Sortie :
```
🏖️ Vérification des réservations pendant les vacances...
📋 4 réservation(s) à annuler:
   🗑️  2026-02-10 (MORNING) - Bureau COP-0-05
   🗑️  2026-02-10 (AFTERNOON) - Bureau COP-0-05
   🗑️  2026-02-11 (MORNING) - Bureau COP-0-05
   🗑️  2026-02-11 (AFTERNOON) - Bureau COP-0-05
✅ 4/4 réservation(s) annulée(s)
```

#### En mode automatique (`--schedule`)

En mode planifié avec `AUTO_CANCEL_VACATIONS=true`, le bot annule automatiquement les réservations qui tombent pendant vos vacances :

```bash
python main.py --schedule
```

Le bot :
1. Vérifie vos réservations existantes
2. Identifie celles qui tombent pendant les vacances
3. Les annule automatiquement
4. Réserve les nouvelles dates (hors vacances)

---

## 📊 Exemples pratiques

### Exemple 1 : Vacances d'hiver (1 semaine)

```bash
# .env
RESERVATION_DAYS_OF_WEEK=1,2,3,4,5
RECURRING_WEEKS=4
VACATION_DATES=2026-02-09:2026-02-13
AUTO_CANCEL_VACATIONS=true
```

**Résultat** :
- Le bot réserve tous les jours ouvrés des 4 prochaines semaines
- **SAUF** du 9 au 13 février (5 jours exclus)
- Si des réservations existaient déjà, elles sont annulées

### Exemple 2 : Jours fériés ponctuels

```bash
VACATION_DATES=2026-04-06,2026-05-01,2026-05-08,2026-07-14
AUTO_CANCEL_VACATIONS=true
```

**Résultat** :
- Pas de réservation les jours fériés français
- Annulation automatique si des réservations existaient

### Exemple 3 : Plusieurs périodes de vacances

```bash
VACATION_DATES=2026-02-09:2026-02-13,2026-04-13:2026-04-24,2026-07-20:2026-08-10
```

**Résultat** :
- 3 périodes exclues : 
  - Vacances d'hiver : 5 jours
  - Vacances de printemps : 12 jours
  - Vacances d'été : 22 jours

---

## 🎯 Commandes utiles

### Voir les vacances configurées

```bash
python main.py --schedule
```

Au démarrage, le bot affiche :
```
🏖️ Périodes de vacances à venir:
   • 09/02/2026 → 13/02/2026 (5 jours)
   • 13/04/2026 → 24/04/2026 (12 jours)
   • 20/07/2026 → 10/08/2026 (22 jours)
```

### Réserver sans tenir compte des vacances

Si vous voulez ignorer temporairement les vacances configurées, modifiez le `.env` :

```bash
VACATION_DATES=
```

Ou commentez la ligne :
```bash
# VACATION_DATES=2026-02-09:2026-02-13
```

---

## 🔄 Workflow automatique

En mode `--schedule` avec vacances configurées :

1. **Chaque jour à 3h05** (ou l'heure configurée) :
   ```
   1. Vérifie s'il y a des réservations pendant les vacances
   2. Les annule si AUTO_CANCEL_VACATIONS=true
   3. Réserve les N prochaines semaines (RECURRING_WEEKS)
   4. Exclut automatiquement les jours de vacances
   ```

2. **Résultat** :
   - Vous n'avez **jamais** de réservations pendant vos absences
   - Le bot s'adapte automatiquement à votre calendrier

---

## ⚙️ Configuration Docker

Pour Docker/NAS Synology, ajoutez simplement les variables dans votre `.env` :

```bash
# config/.env
VACATION_DATES=2026-02-09:2026-02-13,2026-04-13:2026-04-24
AUTO_CANCEL_VACATIONS=true
```

Le conteneur les lira automatiquement au démarrage.

---

## 💡 Bonnes pratiques

### ✅ Recommandé

- **Planifier à l'avance** : Ajoutez vos vacances dès que vous les connaissez
- **AUTO_CANCEL_VACATIONS=true** : Pratique si vous avez déjà réservé avant de connaître vos dates
- **Vérifier régulièrement** : `python main.py --show` pour voir vos réservations

### ⚠️ Attention

- **Format strict** : Respectez `YYYY-MM-DD` (année-mois-jour avec des zéros)
- **Pas d'espaces** : `2026-02-09:2026-02-13` ✅ | `2026-02-09 : 2026-02-13` ❌
- **Virgules uniquement** : Pas de point-virgule ou autre séparateur

---

## 🐛 Dépannage

### Les vacances ne sont pas prises en compte

1. Vérifiez le format des dates :
   ```bash
   VACATION_DATES=2026-02-09:2026-02-13  # ✅ Correct
   VACATION_DATES=09/02/2026:13/02/2026  # ❌ Format incorrect
   ```

2. Vérifiez qu'il n'y a pas d'espaces :
   ```bash
   VACATION_DATES=2026-02-09:2026-02-13,2026-03-01:2026-03-07  # ✅
   VACATION_DATES=2026-02-09:2026-02-13, 2026-03-01:2026-03-07  # ❌ Espace après virgule
   ```

3. Vérifiez les logs :
   ```
   📅 Périodes de vacances configurées: 2 période(s)
      • 09/02/2026 → 13/02/2026
      • 01/03/2026 → 07/03/2026
   ```

### Les réservations ne sont pas annulées

Vérifiez que :
```bash
AUTO_CANCEL_VACATIONS=true  # Pas "True" ou "TRUE"
```

### Erreur de parsing

Si vous voyez :
```
⚠️ Erreur lors du parsing des dates de vacances
Format attendu: YYYY-MM-DD:YYYY-MM-DD,YYYY-MM-DD:YYYY-MM-DD
```

Corrigez le format dans votre `.env`.

---

## ❓ FAQ

**Q: Puis-je avoir des périodes qui se chevauchent ?**  
R: Oui, le bot gère automatiquement les chevauchements. Exemple : `2026-02-10:2026-02-15,2026-02-13:2026-02-20` fonctionne.

**Q: Que se passe-t-il si j'ajoute des vacances après avoir déjà réservé ?**  
R: Si `AUTO_CANCEL_VACATIONS=true`, les réservations seront annulées au prochain lancement du bot.

**Q: Puis-je avoir plus de 10 périodes de vacances ?**  
R: Oui, aucune limite. Séparez-les simplement par des virgules.

**Q: Le bot annule-t-il TOUTES mes réservations ou seulement celles en vacances ?**  
R: Seulement celles qui tombent pendant les périodes définies dans `VACATION_DATES`.

**Q: Puis-je désactiver temporairement la gestion des vacances ?**  
R: Oui, commentez ou videz `VACATION_DATES` dans le `.env`.

---

## 📝 Exemple complet de configuration

```bash
# .env
ONEFLEX_TOKEN=votre_access_token_ici
ONEFLEX_REFRESH_TOKEN=votre_refresh_token_ici

# Réservation automatique à 3h du matin
RESERVATION_TIME=03:00

# Tous les jours ouvrés
RESERVATION_DAYS_OF_WEEK=1,2,3,4,5

# 4 semaines à l'avance
RECURRING_WEEKS=4

# Vacances 2026
VACATION_DATES=2026-02-09:2026-02-13,2026-04-13:2026-04-24,2026-07-20:2026-08-10,2026-12-21:2027-01-02

# Annulation automatique activée
AUTO_CANCEL_VACATIONS=true

# Webhook Discord pour les alertes
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Avec cette config, le bot :
- ✅ Réserve automatiquement tous les jours ouvrés pour 4 semaines
- ✅ Exclut automatiquement vos 4 périodes de vacances
- ✅ Annule les réservations existantes pendant vos absences
- ✅ Vous alerte en cas de problème via Discord
