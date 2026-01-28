# Déploiement automatique sur Synology NAS

## Architecture

Le bot utilise l'**image Docker publiée sur GitHub Container Registry** (ghcr.io). Pas besoin d'installer Git sur le NAS !

```
WSL (Développement)           GitHub                    NAS Synology (Production)
├─ git push ──────────────────> GHCR (build)
└─ deploy-to-nas.sh ──SSH────> docker pull ──────────> bot running
```

## Configuration initiale

### 1. Activer SSH sur le NAS
1. Panneau de configuration > Terminal & SNMP
2. Activer le service SSH (port 22)
3. Appliquer

### 2. Configurer la clé SSH depuis WSL
```bash
# Générer une clé SSH (si vous n'en avez pas)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copier la clé sur le NAS
ssh-copy-id your_user@192.168.0.191
```

### 3. Préparer le NAS
```bash
# Se connecter au NAS
ssh your_user@192.168.0.191

# Créer la structure de répertoires
mkdir -p /volume1/docker/oneflex/config
cd /volume1/docker/oneflex

# Créer le fichier docker-compose.ghcr.yml
cat > docker-compose.ghcr.yml << 'EOF'
version: '3.8'

services:
  oneflex-bot:
    image: ghcr.io/kiwi41/oneflex-bot:latest
    container_name: oneflex-bot
    restart: unless-stopped
    
    volumes:
      - ./config:/app/config:rw
      - ./logs:/app/logs
    
    environment:
      - TZ=Europe/Paris
EOF

# Créer le fichier de configuration
cat > config/.env << 'EOF'
# Tokens OneFlex (obtenir avec: python auto_get_tokens.py)
ONEFLEX_TOKEN=votre_access_token
ONEFLEX_REFRESH_TOKEN=votre_refresh_token

# Notification Discord (optionnel)
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Configuration
RESERVATION_TIME=03:05
RESERVATION_DAYS=1,2,3,4,5  # Lundi à Vendredi
RECURRING_WEEKS_AHEAD=4
EOF

# Puis éditer config/.env avec vos vrais tokens
nano config/.env
```

## Utilisation

### Méthode 1: Déploiement automatique (recommandé)
Pull la dernière image Docker depuis GHCR et redémarre.

```bash
# Éditer deploy-to-nas.sh avec votre username NAS
nano deploy-to-nas.sh

# Déployer
./deploy-to-nas.sh
```

### Méthode 2: Synchronisation de la config
Synchronise uniquement votre fichier `.env` local vers le NAS.

```bash
# Éditer sync-to-nas.sh avec votre username
nano sync-to-nas.sh

# Synchroniser
./sync-to-nas.sh
```

## Workflow de déploiement

```bash
# 1. Développer localement et tester
docker compose up -d

# 2. Commiter et pousser sur GitHub
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push

# 3. GitHub Actions build l'image automatiquement
#    (voir: https://github.com/Kiwi41/oneflex-bot/actions)

# 4. Déployer sur le NAS
./deploy-to-nas.sh
```

## Commandes utiles

```bash
# Voir les logs en direct
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && sudo docker compose -f docker-compose.ghcr.yml logs -f'

# Statut du conteneur
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && sudo docker compose -f docker-compose.ghcr.yml ps'

# Redémarrer manuellement
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && sudo docker compose -f docker-compose.ghcr.yml restart'

# Voir les réservations
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && sudo docker compose -f docker-compose.ghcr.yml exec oneflex-bot python main.py --show'

# Mettre à jour l'image
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && sudo docker compose -f docker-compose.ghcr.yml pull && sudo docker compose -f docker-compose.ghcr.yml up -d'
```

## Automatisation avec Git Hooks

Déployer automatiquement après chaque `git push`:

```bash
# Créer un hook post-push
cat > .git/hooks/post-push << 'HOOK'
#!/bin/bash
echo "🚀 Auto-déploiement sur le NAS..."
./deploy-to-nas.sh
HOOK

chmod +x .git/hooks/post-push
```

## Avantages de cette méthode

✅ **Pas de Git sur le NAS** - Simplement Docker  
✅ **Images pré-buildées** - Déploiement instantané  
✅ **Toujours à jour** - Image latest depuis GHCR  
✅ **Léger** - Seulement 175MB  
✅ **Rollback facile** - Tags de version disponibles
