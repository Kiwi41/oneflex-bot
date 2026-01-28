# Gestion des tokens OneFlex

## ⚠️ Important : Renouvellement manuel requis

L'API OneFlex **ne supporte pas le refresh automatique des tokens**. Les tokens doivent être renouvelés manuellement lorsqu'ils expirent.

## 📅 Durée de vie des tokens

- **Access Token** : ~15 minutes après émission
- **Session cookies** : 4-6 heures après connexion SSO
- Les tokens restent valides tant que votre session SSO Worldline est active

## 🔄 Comment renouveler les tokens

### Méthode 1 : Depuis votre machine locale

```bash
# 1. Activer l'environnement virtuel
cd /path/to/oneflex-bot
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows

# 2. Lancer l'outil de récupération
python auto_get_tokens.py

# 3. Se connecter via SSO dans le navigateur qui s'ouvre
# Les tokens sont automatiquement récupérés et sauvegardés

# 4. Mettre à jour le fichier config/.env pour Docker
cp .env config/.env

# 5. Redémarrer le bot Docker
docker compose restart
```

### Méthode 2 : Script automatisé (recommandé)

Créez un script `renew_tokens.sh` :

```bash
#!/bin/bash
cd /path/to/oneflex-bot
source .venv/bin/activate
python auto_get_tokens.py --headless 2>/dev/null || python auto_get_tokens.py
cp .env config/.env
docker compose restart
```

Ajoutez une tâche cron pour renouveler quotidiennement :

```cron
# Renouveler les tokens tous les jours à 2h du matin
0 2 * * * /path/to/oneflex-bot/renew_tokens.sh
```

### Méthode 3 : Sur Synology NAS

1. **Via SSH** :
   ```bash
   ssh admin@nas-ip
   cd /volume1/docker/oneflex-bot
   python3 auto_get_tokens.py
   cp .env config/.env
   docker compose restart
   ```

2. **Via Task Scheduler** (interface web) :
   - Panneau de configuration → Planificateur de tâches
   - Créer → Tâche planifiée → Script défini par l'utilisateur
   - Fréquence : Quotidien à 2h00
   - Script :
     ```bash
     cd /volume1/docker/oneflex-bot
     python3 auto_get_tokens.py
     cp .env config/.env
     docker compose restart
     ```

## 🔔 Notifications d'expiration

Lorsqu'un token expire, le bot :
1. ❌ S'arrête automatiquement
2. 📧 Envoie une alerte Discord (si configuré)
3. 📝 Log un message d'erreur clair

**Exemple de message Discord :**
```
🔑 Token OneFlex expiré

Reconnectez-vous avec:
python auto_get_tokens.py

Puis redémarrez le bot Docker.
```

## 🛠️ Dépannage

### Le bot s'arrête avec "Token expiré"

**Solution :** Relancez `auto_get_tokens.py` pour renouveler les tokens.

### auto_get_tokens.py ne s'ouvre pas

**Causes possibles :**
- Chrome/Chromium non installé
- Pas d'affichage graphique (serveur distant)

**Solution :** Utilisez le mode headless si disponible ou lancez depuis une machine avec interface graphique.

### Les tokens expirent trop rapidement

**Normal !** Les access tokens ne durent que 15 minutes. C'est la session SSO qui les maintient valides.

Si votre session SSO expire (déconnexion IdP, timeout), les tokens ne peuvent plus être renouvelés et vous devez vous reconnecter.

## 📊 Fréquence de renouvellement recommandée

| Environnement | Fréquence | Méthode |
|---------------|-----------|---------|
| Développement | À la demande | Manuel |
| Production (NAS) | Quotidien | Cron/Task Scheduler |
| CI/CD | N/A | Tokens en secrets |

## 🔐 Sécurité

- ⚠️ Ne committez **JAMAIS** les tokens dans Git
- ✅ Les tokens sont dans `.env` (ignoré par `.gitignore`)
- ✅ `config/session.json` est également ignoré
- 🔒 Les tokens donnent accès complet à votre compte OneFlex
- 🗑️ Révoquez les tokens si compromis en changeant votre mot de passe SSO

## 💡 Améliorations futures

Des solutions de refresh automatique pourraient être explorées :
- Intégration OAuth2 complète avec refresh_token
- Proxy de session persistant
- Extension du protocole SSO

Actuellement, le renouvellement manuel reste la méthode la plus fiable et sécurisée.
