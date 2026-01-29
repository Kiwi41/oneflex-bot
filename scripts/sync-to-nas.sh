#!/bin/bash
# Script de synchronisation de la configuration vers le NAS
# L'image Docker est téléchargée depuis GHCR, seul le .env est synchronisé

set -e

# Configuration
NAS_HOST="192.168.0.191"
NAS_USER="your_synology_user"  # À modifier
NAS_PATH="/volume1/docker/oneflex"

echo "🔄 Synchronisation de la configuration vers le NAS"
echo "=================================================="

# Vérifier la connexion
if ! ssh -o ConnectTimeout=5 "${NAS_USER}@${NAS_HOST}" "echo 'OK'" &>/dev/null; then
    echo "❌ Connexion SSH impossible"
    exit 1
fi

# Synchroniser uniquement les fichiers de configuration
echo "📤 Transfert du fichier de configuration..."
rsync -avz \
    --include='docker-compose.ghcr.yml' \
    --include='config/' \
    --include='config/.env' \
    --exclude='*' \
    ./ "${NAS_USER}@${NAS_HOST}:${NAS_PATH}/"

echo "✅ Configuration synchronisée"

# Redémarrer le conteneur
echo "🔄 Redémarrage du conteneur..."
ssh "${NAS_USER}@${NAS_HOST}" "cd ${NAS_PATH} && sudo docker compose -f docker-compose.ghcr.yml pull && sudo docker compose -f docker-compose.ghcr.yml up -d"

echo ""
echo "✅ Déploiement terminé!"
