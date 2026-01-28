# Comment récupérer vos tokens OneFlex (SSO)

Puisque OneFlex utilise SSO, vous devez récupérer vos tokens d'authentification.

## 🔑 Tokens nécessaires

1. **access_token** : Token d'accès (expire après 15 minutes)
2. **refresh_token** : Token pour renouveler automatiquement l'access_token (longue durée)

## 🤖 Méthode Automatique (Recommandée)

Utilisez le script automatisé qui gère tout pour vous :

```bash
python auto_get_tokens.py
```

Le script va :
1. ✅ Ouvrir Chrome automatiquement
2. ✅ Attendre que vous vous connectiez via SSO
3. ✅ Récupérer automatiquement les tokens depuis les cookies
4. ✅ Mettre à jour votre fichier `.env` directement

**Prérequis** :
```bash
pip install selenium
```

---

## 📋 Méthode Manuelle : Via les Cookies

1. **Connectez-vous** sur https://oneflex.myworldline.com
2. **Ouvrez les outils développeur** : `F12` ou `Ctrl+Shift+I`
3. **Allez dans l'onglet "Application"** (Chrome/Edge) ou "Storage" (Firefox)
4. **Dans la section "Cookies"**, sélectionnez `https://oneflex.myworldline.com`
5. **Cherchez ces deux cookies** :
   - `access_token` - Copiez sa valeur
   - `refresh_token` - Copiez sa valeur
6. **Ajoutez-les dans votre fichier `.env`** :

```bash
ONEFLEX_TOKEN=votre_access_token_ici
ONEFLEX_REFRESH_TOKEN=votre_refresh_token_ici
```

## ✨ Rafraîchissement automatique

Avec le `refresh_token` configuré, le bot rafraîchira **automatiquement** l'`access_token` quand il expire. Vous n'aurez plus besoin de le mettre à jour manuellement !

Le nouveau token sera automatiquement sauvegardé dans le fichier `.env`.

## Vérification

Pour vérifier que tout fonctionne :

```bash
python main.py --show
```

Vous devriez voir :
- ✅ Token d'authentification fourni
- 🔄 Refresh token disponible pour renouvellement automatique
