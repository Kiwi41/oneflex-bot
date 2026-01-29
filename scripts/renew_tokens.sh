#!/bin/bash
# Script de renouvellement automatique des tokens OneFlex
# Usage: ./renew_tokens.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Renouvellement des tokens OneFlex..."
echo "📁 Répertoire: $SCRIPT_DIR"
echo ""

# Activer l'environnement virtuel si disponible
if [ -f ".venv/bin/activate" ]; then
    echo "🐍 Activation de l'environnement virtuel..."
    source .venv/bin/activate
fi

# Vérifier que auto_get_tokens.py existe
if [ ! -f "auto_get_tokens.py" ]; then
    echo "❌ Erreur: auto_get_tokens.py non trouvé"
    exit 1
fi

# Lancer auto_get_tokens.py
echo "🚀 Lancement de auto_get_tokens.py..."
echo "   (Un navigateur va s'ouvrir pour la connexion SSO)"
echo ""

python auto_get_tokens.py

# Vérifier que le .env a été créé/mis à jour
if [ ! -f ".env" ]; then
    echo "❌ Erreur: Fichier .env non créé"
    exit 1
fi

# Copier vers config/.env pour Docker
echo ""
echo "📋 Copie vers config/.env..."
mkdir -p config
cp .env config/.env

# Vérifier si Docker est disponible
if command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Redémarrage du container Docker..."
    if [ -f "docker-compose.yml" ]; then
        docker compose restart
        echo "✅ Container redémarré"
    else
        echo "⚠️  docker-compose.yml non trouvé, skip restart"
    fi
else
    echo ""
    echo "ℹ️  Docker non disponible, skip restart"
fi

echo ""
echo "✅ Tokens renouvelés avec succès !"
echo ""
echo "📝 Prochaines étapes (si Docker non auto-redémarré):"
echo "   docker compose restart"
