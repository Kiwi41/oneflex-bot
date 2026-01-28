# Gestion des tokens OneFlex

## ✨ Refresh automatique intégré !

**Excellente nouvelle :** Le bot renouvelle désormais automatiquement les tokens lorsqu'ils expirent.

Grâce à l'endpoint `/api/auth/token` découvert, le bot peut renouveler les `access_token` 
automatiquement en utilisant le `refresh_token`. Vous n'avez plus besoin de renouveler 
manuellement les tokens toutes les 15 minutes !

## 🔑 Comment ça marche ?

### Durée de vie des tokens

- **Access Token** : ~15 minutes (renouvelé automatiquement)
- **Refresh Token** : Plusieurs heures/jours (tant que la session SSO est active)
- **Session SSO** : Plusieurs heures (gérée par Worldline Azure AD)

### Processus automatique

1. 📡 Le bot fait une requête GraphQL
2. 🚫 L'API répond `401 Unauthorized` (token expiré)
3. 🔄 Le bot utilise automatiquement le `refresh_token` pour obtenir un nouveau `access_token`
4. 💾 Le nouveau token est sauvegardé dans `.env`
5. ♻️ La requête originale est réessayée avec succès
6. ✅ Tout cela se passe de manière transparente !

### Endpoint de refresh

```http
POST https://oneflex.myworldline.com/api/auth/token
Content-Type: application/json

{
  "grant_type": "refresh_token",
  "refresh_token": "6ecc79b280179dc304b9"
}
```

Réponse :
```json
{
  "token_type": "bearer",
  "access_token": "eyJhbGci..."
}
```

## 🚀 Configuration initiale

Vous devez récupérer vos tokens **une seule fois** lors de l'installation :

### Méthode automatique (Recommandée)

```bash
# 1. Lancer l'outil de récupération
python auto_get_tokens.py

# 2. Se connecter via SSO dans le navigateur
# Les tokens sont automatiquement récupérés

# 3. Copier vers Docker si nécessaire
cp .env config/.env

# 4. Démarrer le bot
docker compose up -d
```

### Méthode manuelle

1. Connectez-vous sur https://oneflex.myworldline.com
2. Ouvrez les outils développeur (F12)
3. Allez dans **Application** > **Cookies** > `https://oneflex.myworldline.com`
4. Copiez les valeurs de :
   - `access_token` → `ONEFLEX_TOKEN`
   - `refresh_token` → `ONEFLEX_REFRESH_TOKEN`

### Fichier .env

```bash
# Tokens d'authentification (requis)
ONEFLEX_TOKEN=votre_access_token_ici
ONEFLEX_REFRESH_TOKEN=votre_refresh_token_ici
```

## 🔔 Notifications automatiques

Le bot vous prévient uniquement si le refresh échoue :

### Cas 1 : Token expiré (Normal)
```
⚠️  Token expiré, tentative de refresh automatique...
🔄 Tentative de refresh du token...
✅ Token renouvelé avec succès
💾 Token mis à jour dans .env
✅ Token refreshé, nouvelle tentative de requête...
```

### Cas 2 : Refresh échoué (Intervention requise)
```
❌ Refresh automatique échoué ou token toujours invalide
```

**Message Discord :**
```
🔑 Token OneFlex expiré et refresh automatique échoué

Reconnectez-vous avec:
python auto_get_tokens.py

Puis redémarrez le bot Docker.
```

## 🔧 Dépannage

### Le refresh automatique échoue

**Causes possibles :**
- Le `refresh_token` a expiré (session SSO terminée)
- Vous vous êtes déconnecté de Worldline SSO
- Le `refresh_token` est manquant dans `.env`

**Solution :**
```bash
python auto_get_tokens.py
cp .env config/.env
docker compose restart
```

### Tester le refresh manuellement

```bash
python test_auto_refresh.py
```

Ce script va :
- Vérifier que le token actuel fonctionne
- Forcer un refresh du token
- Vérifier que le nouveau token fonctionne
- Tester l'auto-refresh sur 401
- Vérifier la persistence dans `.env`

### Logs de refresh

Le bot log chaque refresh automatique :

```bash
# Voir les logs en temps réel
docker logs -f oneflex-bot

# Filtrer uniquement les refreshs
docker logs oneflex-bot 2>&1 | grep -i refresh
```

## 🔐 Sécurité

- ⚠️ Ne committez **JAMAIS** les tokens dans Git
- ✅ Les tokens sont dans `.env` (ignoré par `.gitignore`)
- 🔒 Les tokens donnent accès complet à votre compte OneFlex
- 🗑️ Révoquez les tokens si compromis en changeant votre mot de passe SSO

## 📊 Fréquence de renouvellement

| Token | Durée | Renouvellement |
|-------|--------|----------------|
| Access Token | ~15 min | Automatique toutes les 15 min |
| Refresh Token | Plusieurs heures | Automatique jusqu'à expiration session SSO |
| Session SSO | Plusieurs heures | Manuel (reconnexion SSO requise) |

## 🎉 Avantages du refresh automatique

✅ **Plus de réveils à 3h du matin** pour renouveler les tokens  
✅ **Le bot fonctionne en continu** sans intervention  
✅ **Transparence totale** : le refresh se fait en arrière-plan  
✅ **Persistance** : le nouveau token est automatiquement sauvegardé dans `.env`  
✅ **Notifications intelligentes** : alerté uniquement en cas de problème  

## 🔍 Découverte technique

L'endpoint de refresh a été découvert par reverse engineering :

```bash
# Test de tous les endpoints possibles
python test_refresh_methods.py

# Résultat : /api/auth/token fonctionne avec grant_type=refresh_token
```

Cet endpoint suit le standard OAuth2 pour le renouvellement des tokens.
