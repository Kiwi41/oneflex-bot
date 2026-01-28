#!/bin/bash
# Script de déploiement automatique sur Synology NAS
# Utilise l'image Docker publiée sur GitHub Container Registry

set -e

# Configuration
NAS_HOST="192.168.0.191"
NAS_USER="your_synology_user"  # À modifier
NAS_PATH="/volume1/docker/oneflex"  # Chemin sur le NAS

echo "🚀 Déploiement OneFlex Bot sur Synology NAS"
echo "============================================="

# Vérifier la connexion SSH
echo "📡 Vérification de la connexion au NAS..."
if ! ssh -o ConnectTimeout=5 "${NAS_USER}@${NAS_HOST}" "echo 'Connexion OK'" 2>/dev/null; then
    echo "❌ Impossible de se connecter au NAS"
    echo ""
    echo "Configuration SSH requise:"
    echo "1. ssh-copy-id ${NAS_USER}@${NAS_HOST}"
    echo "2. Activer SSH sur le NAS (Panneau de configuration > Terminal & SNMP)"
    exit 1
fi

echo "✅ Connexion SSH établie"

# Déployer via l'image Docker GHCR
echo ""
echo "📦 Pull de la dernière image Docker..."
ssh "${NAS_USER}@${NAS_HOST}" << 'ENDSSH'
    cd /volume1/docker/oneflex || exit 1
    
    echo "📥 Pull de la dernière image depuis GitHub..."
    docker compose -f docker-compose.ghcr.yml pull
    
    echo "🔄 Redémarrage du conteneur..."
    docker compose -f docker-compose.ghcr.yml down
    docker compose -f docker-compose.ghcr.yml up -d
    
    echo "📊 Statut du conteneur:"
    docker compose -f docker-compose.ghcr.yml ps
    
    echo "📝 Derniers logs:"
    docker compose -f docker-compose.ghcr.yml logs --tail=10
ENDSSH

echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "Pour voir les logs en temps réel:"
echo "  ssh ${NAS_USER}@${NAS_HOST} 'cd ${NAS_PATH} && docker compose logs -f'"
