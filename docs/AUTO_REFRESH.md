# Ré-authentification Automatique SSO

## Problème

Les tokens OneFlex expirent toutes les 15 minutes et l'API ne fournit pas de mécanisme de refresh. Cela nécessitait une intervention manuelle régulière pour renouveler les tokens, rendant le bot inutile en mode autonome.

## Solution

Le bot peut maintenant se ré-authentifier **automatiquement** via SSO lorsque le token expire, en utilisant vos credentials Worldline stockés dans le `.env`.

## Configuration

### 1. Ajouter vos credentials SSO dans `.env`

```bash
# Credentials SSO pour ré-authentification automatique
SSO_EMAIL=votre.email@worldline.com
SSO_PASSWORD=votre_mot_de_passe_sso
```

### 2. Obtenir les tokens initiaux

```bash
python auto_get_tokens.py
```

Cela va ouvrir un navigateur où vous devrez vous connecter une première fois.

### 3. Le bot gère le reste automatiquement

Une fois configuré, le bot :
- ✅ Détecte quand le token expire (erreur 401)
- ✅ Lance automatiquement une ré-authentification SSO en headless
- ✅ Récupère les nouveaux tokens
- ✅ Met à jour le fichier `.env`
- ✅ Continue son exécution sans interruption

## Fonctionnement technique

### Workflow de ré-authentification

```
Requête API
    ↓
Erreur 401 (token expiré)
    ↓
Ré-authentification SSO automatique (headless)
    ├─ Ouvre Chrome en mode invisible
    ├─ Se connecte avec SSO_EMAIL/SSO_PASSWORD
    ├─ Récupère les nouveaux cookies (access_token, refresh_token)
    └─ Met à jour .env
    ↓
Réessaie la requête avec le nouveau token
    ↓
Succès ✅
```

### Fichiers impliqués

- **`auto_refresh_tokens.py`** : Script de ré-authentification automatique via Selenium
- **`oneflex_client.py`** : Méthode `refresh_access_token()` qui appelle le script
- **`config.py`** : Charge `SSO_EMAIL` et `SSO_PASSWORD`
- **`main.py`** : Passe les credentials SSO au client

## Sécurité

⚠️ **Important** : Vos credentials SSO sont stockés en clair dans le `.env`. Assurez-vous que :
- Le fichier `.env` est dans `.gitignore` (déjà configuré)
- Le fichier n'est accessible que par vous (`chmod 600 .env`)
- Vous utilisez un mot de passe fort

### Recommandations

1. **Ne jamais committer le `.env`** avec vos credentials
2. **Sur votre NAS**, protégez le répertoire avec les bons droits
3. **Utilisez Docker secrets** pour une sécurité renforcée (voir ci-dessous)

### Alternative avec Docker Secrets (recommandé pour production)

```yaml
# docker-compose.yml
services:
  oneflex-bot:
    secrets:
      - sso_email
      - sso_password
    environment:
      - SSO_EMAIL_FILE=/run/secrets/sso_email
      - SSO_PASSWORD_FILE=/run/secrets/sso_password

secrets:
  sso_email:
    file: ./secrets/sso_email.txt
  sso_password:
    file: ./secrets/sso_password.txt
```

## Dépannage

### Le bot ne se reconnecte pas automatiquement

1. **Vérifiez que Chrome/Chromium est installé**
   ```bash
   which google-chrome chromium-browser chromium
   ```

2. **Vérifiez que Selenium est installé**
   ```bash
   pip install selenium
   ```

3. **Testez manuellement la ré-authentification**
   ```bash
   python auto_refresh_tokens.py
   ```

4. **Vérifiez les logs**
   ```bash
   docker logs oneflex-bot
   ```

### Erreurs courantes

#### `SSO_EMAIL et SSO_PASSWORD doivent être définis`
➜ Ajoutez vos credentials dans `.env`

#### `Échec de la ré-authentification SSO`
➜ Vérifiez que vos credentials sont corrects
➜ Testez manuellement avec `python auto_get_tokens.py`

#### `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable`
➜ Installez Chrome ou Chromium sur votre système

## Mode manuel (sans credentials SSO)

Si vous ne souhaitez pas stocker vos credentials :
1. Ne remplissez pas `SSO_EMAIL` et `SSO_PASSWORD`
2. Recevez des alertes Discord quand le token expire
3. Lancez manuellement `python auto_get_tokens.py` pour renouveler

## Performance

- **Temps de ré-authentification** : ~10-15 secondes
- **Fréquence** : Seulement quand le token expire (toutes les 15 minutes en moyenne)
- **Impact** : Transparent pour l'utilisateur, aucune intervention requise

## Exemple de logs

```
INFO:oneflex_client:🔑 Token d'authentification fourni
INFO:oneflex_client:🔄 Refresh token disponible pour renouvellement automatique
INFO:oneflex_client:🔐 Credentials SSO disponibles pour ré-authentification automatique
...
WARNING:oneflex_client:⚠️ Token expiré, tentative de rafraîchissement...
INFO:oneflex_client:🔄 Ré-authentification automatique via SSO...
INFO:oneflex_client:✅ Token rafraîchi avec succès via SSO automatique
INFO:oneflex_client:📝 Fichier .env mis à jour avec le nouveau token
```

## Désactiver la ré-authentification automatique

Pour revenir au mode manuel :
```bash
# Supprimez ou commentez ces lignes dans .env
# SSO_EMAIL=...
# SSO_PASSWORD=...
```

Le bot vous enverra des alertes Discord quand le token expire.
