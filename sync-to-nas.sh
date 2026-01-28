#!/bin/bash
# Script de synchronisation des fichiers vers le NAS via rsync

set -e

# Configuration
NAS_HOST="192.168.0.191"
NAS_USER="your_synology_user"  # À modifier
NAS_PATH="/volume1/docker/oneflex"

echo "🔄 Synchronisation des fichiers vers le NAS"
echo "==========================================="

# Vérifier la connexion
if ! ssh -o ConnectTimeout=5 "${NAS_USER}@${NAS_HOST}" "echo 'OK'" &>/dev/null; then
    echo "❌ Connexion SSH impossible"
    exit 1
fi

# Synchroniser les fichiers
echo "📤 Transfert des fichiers..."
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='config/.env' \
    --exclude='archive/' \
    --exclude='logs/' \
    ./ "${NAS_USER}@${NAS_HOST}:${NAS_PATH}/"

echo "✅ Fichiers synchronisés"

# Redémarrer le conteneur
echo "🔄 Redémarrage du conteneur..."
ssh "${NAS_USER}@${NAS_HOST}" "cd ${NAS_PATH} && docker compose up -d --build"

echo ""
echo "✅ Déploiement terminé!"
