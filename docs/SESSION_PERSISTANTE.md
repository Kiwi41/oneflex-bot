# Rafraîchissement Automatique des Tokens

## Le Problème

Les tokens OneFlex expirent **toutes les 15 minutes** et l'API ne fournit pas de mécanisme de refresh. Cela nécessitait une intervention manuelle constante, rendant impossible l'automatisation complète.

## La Solution : Session Persistante

Au lieu de stocker votre mot de passe (impossible avec 2FA), le bot utilise une **session persistante** :

1. Vous vous connectez **une fois manuellement** (avec 2FA)
2. Le bot sauvegarde **tous les cookies de session**
3. Quand le token expire, le bot **réutilise les cookies** pour obtenir de nouveaux tokens
4. Les cookies de session durent **plusieurs jours/semaines**

✅ **Aucun mot de passe stocké**  
✅ **Compatible avec 2FA**  
✅ **Automatisation complète** jusqu'à expiration de la session

## Configuration Initiale

### 1. Récupérer les tokens initiaux

```bash
python auto_get_tokens.py
```

Ce script va :
- Ouvrir Chrome
- Vous demander de vous connecter (avec votre 2FA)
- Récupérer les tokens
- **Sauvegarder la session dans `config/session.json`**
- Mettre à jour `.env`

### 2. C'est tout !

Le bot gère ensuite automatiquement :
- Détection des expirations de token
- Rafraîchissement via les cookies sauvegardés
- Mise à jour du `.env`

## Fonctionnement Technique

### Workflow Automatique

```
Requête API OneFlex
    ↓
Token expiré ? (401)
    ↓ OUI
Charger cookies de session sauvegardés
    ↓
Ouvrir Chrome en headless
    ↓
Restaurer tous les cookies
    ↓
Naviguer vers OneFlex (déjà connecté !)
    ↓
Récupérer nouveaux tokens
    ↓
Mettre à jour .env
    ↓
Continuer l'exécution
```

### Fichiers Importants

- **`config/session.json`** : Cookies de session sauvegardés (SENSIBLE !)
- **`session_manager.py`** : Gestion de la persistance
- **`auto_get_tokens.py`** : Login manuel initial + sauvegarde session
- **`oneflex_client.py`** : Rafraîchissement automatique intégré

## Durée de Vie

| Élément | Durée | Action requise |
|---------|-------|----------------|
| `access_token` | 15 minutes | Automatique (session persistante) |
| Cookies de session | Plusieurs jours/semaines | Relancer `auto_get_tokens.py` |
| Session expirée | Variable | Alerte Discord + reconnexion manuelle |

## Logs

### Démarrage Normal

```
INFO:oneflex_client:🔑 Token d'authentification fourni
INFO:oneflex_client:🔄 Refresh token disponible pour renouvellement automatique
INFO:oneflex_client:💾 Session persistante disponible pour rafraîchissement automatique
```

### Rafraîchissement Automatique

```
WARNING:oneflex_client:⚠️ Token expiré, tentative de rafraîchissement...
INFO:oneflex_client:🔄 Tentative de rafraîchissement via session persistante...
INFO:session_manager:📂 Session chargée : 24 cookies
INFO:session_manager:🌐 Ouverture de OneFlex avec session sauvegardée...
INFO:session_manager:🔄 Restauration des cookies de session...
INFO:session_manager:🔍 Récupération des tokens...
INFO:session_manager:✅ Tokens récupérés avec succès via session persistante
INFO:oneflex_client:✅ Token rafraîchi avec succès via session persistante
INFO:oneflex_client:📝 Fichier .env mis à jour avec le nouveau token
```

### Session Expirée

```
WARNING:oneflex_client:⚠️ Token expiré, tentative de rafraîchissement...
INFO:oneflex_client:🔄 Tentative de rafraîchissement via session persistante...
ERROR:session_manager:❌ Session expirée ou invalide. Reconnectez-vous avec auto_get_tokens.py
ERROR:oneflex_client:❌ Impossible de rafraîchir le token
ERROR:oneflex_client:📝 Action requise : Lancez 'python auto_get_tokens.py' pour vous reconnecter
CRITICAL:notifications:⚠️ ALERTE : Token expiré. Reconnectez-vous avec: python auto_get_tokens.py
```

## Sécurité

### Fichier `config/session.json`

⚠️ **ATTENTION** : Ce fichier contient vos cookies de session et permet d'accéder à OneFlex sans mot de passe !

**Protection requise** :

```bash
# Permissions restrictives
chmod 600 config/session.json

# Déjà dans .gitignore
git status  # Ne doit PAS apparaître
```

### Sur Docker/NAS

```yaml
# docker-compose.yml
services:
  oneflex-bot:
    volumes:
      - ./config:/app/config:rw  # Lecture/écriture pour session.json
    user: "1000:1000"  # Utilisateur non-root
```

### Bonnes Pratiques

1. ✅ Le fichier est déjà dans `.gitignore`
2. ✅ Protégez `/config` avec les bons droits UNIX
3. ✅ N'exposez jamais `session.json` sur Internet
4. ✅ Régénérez la session si vous soupçonnez une compromission

## Dépannage

### La session ne se sauvegarde pas

```bash
# Vérifier que le répertoire config/ existe
ls -la config/

# Créer si nécessaire
mkdir -p config

# Relancer auto_get_tokens.py
python auto_get_tokens.py
```

### Le rafraîchissement automatique ne fonctionne pas

```bash
# 1. Vérifier que session.json existe
ls -la config/session.json

# 2. Vérifier le contenu
cat config/session.json | jq .cookies | head

# 3. Tester manuellement le rafraîchissement
python -c "from session_manager import refresh_tokens_from_session; print(refresh_tokens_from_session(headless=False))"

# 4. Si ça échoue, régénérer la session
python auto_get_tokens.py
```

### Session expirée fréquemment

Les cookies de session OneFlex peuvent expirer selon différentes conditions :
- Changement de mot de passe
- Déconnexion manuelle sur le site
- Politique de sécurité de l'entreprise

**Solution** : Configurez une tâche cron hebdomadaire pour régénérer la session :

```bash
# Crontab : tous les dimanches à 3h00
0 3 * * 0 cd /path/to/oneflex-bot && /path/to/venv/bin/python auto_get_tokens.py --auto
```

(Note: L'option `--auto` n'existe pas encore, mais on pourrait l'ajouter si besoin)

### Chrome/Selenium non disponible

```bash
# Installer Chrome/Chromium
sudo apt-get install chromium-browser  # Debian/Ubuntu
brew install chromium  # macOS

# Installer Selenium
pip install selenium
```

## Alternatives

### Mode Manuel (sans session persistante)

Si vous préférez ne pas sauvegarder la session :

1. **Supprimez `config/session.json`**
2. Le bot vous enverra des **alertes Discord** à chaque expiration
3. Lancez manuellement `python auto_get_tokens.py` quand nécessaire

### Utilisation d'un Proxy Persistant

Pour une solution encore plus robuste, vous pourriez :
- Garder un navigateur Chrome ouvert en permanence
- Utiliser ChromeDriver en remote
- Le bot se connecte au navigateur existant

(Non implémenté, mais possible si besoin)

## Questions Fréquentes

**Q: Pourquoi ne pas utiliser le refresh_token ?**  
R: L'API OneFlex ne fournit pas d'endpoint `/api/auth/refresh`. Le refresh_token récupéré sert uniquement au front-end.

**Q: La session est-elle sécurisée ?**  
R: Aussi sécurisée que vos cookies de navigateur. Ne partagez jamais `session.json`.

**Q: Combien de temps dure la session ?**  
R: Variable selon la configuration OneFlex/Worldline. Généralement plusieurs jours à plusieurs semaines.

**Q: Que se passe-t-il si je change mon mot de passe ?**  
R: La session sera invalidée. Relancez `auto_get_tokens.py` pour en créer une nouvelle.

**Q: Puis-je utiliser le bot sur plusieurs machines ?**  
R: Oui, copiez `config/session.json` sur chaque machine. Attention à la sécurité !

## Commandes Utiles

```bash
# Voir le contenu de la session (sans les tokens)
jq '.cookies | length' config/session.json

# Voir la date de création
jq '.timestamp' config/session.json

# Tester le rafraîchissement
python -c "from session_manager import refresh_tokens_from_session; refresh_tokens_from_session(headless=False)"

# Supprimer la session (forcer reconnexion)
rm config/session.json
python auto_get_tokens.py
```

## Améliorations Futures

- [ ] Auto-détection de l'expiration de session avant échec
- [ ] Mode `--auto` pour `auto_get_tokens.py` (sans interaction)
- [ ] Chiffrement de `session.json` avec une clé locale
- [ ] Support de multiples sessions (plusieurs comptes)
- [ ] Métriques sur la durée de vie moyenne des sessions
