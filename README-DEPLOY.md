# Déploiement automatique sur Synology NAS

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

### 3. Cloner le repo sur le NAS
```bash
# Se connecter au NAS
ssh your_user@192.168.0.191

# Créer le répertoire
mkdir -p /volume1/docker/oneflex
cd /volume1/docker/oneflex

# Cloner le repo
git clone https://github.com/Kiwi41/oneflex-bot.git .

# Copier le fichier de configuration
cp config/.env.example config/.env
# Puis éditer config/.env avec vos tokens
```

## Utilisation

### Méthode 1: Déploiement via Git (recommandé)
Le bot tire les modifications depuis GitHub et redémarre.

```bash
# Éditer deploy-to-nas.sh avec vos infos
nano deploy-to-nas.sh  # Modifier NAS_USER

# Déployer
./deploy-to-nas.sh
```

### Méthode 2: Synchronisation locale (rsync)
Synchronise vos fichiers locaux vers le NAS.

```bash
# Éditer sync-to-nas.sh avec vos infos
nano sync-to-nas.sh  # Modifier NAS_USER

# Synchroniser
./sync-to-nas.sh
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

## Commandes utiles

```bash
# Voir les logs en direct
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && docker compose logs -f'

# Statut du conteneur
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && docker compose ps'

# Redémarrer manuellement
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && docker compose restart'

# Voir les réservations
ssh your_user@192.168.0.191 'cd /volume1/docker/oneflex && docker compose exec oneflex-bot python main.py --show'
```

## Architecture

```
WSL (Développement)           NAS Synology (Production)
├─ git push ──────────────────> GitHub
└─ deploy-to-nas.sh ──SSH────> git pull + docker restart
```
