# Script de déploiement OneFlex Bot sur Synology NAS (depuis Windows)
# Utilise l'image Docker publiée sur GitHub Container Registry

$ErrorActionPreference = "Stop"

# Configuration
$NAS_HOST = "192.168.0.191"
$NAS_USER = "kiwi"
$NAS_PATH = "/volume1/docker/oneflex"

Write-Host "🚀 Déploiement OneFlex Bot sur Synology NAS" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier la connexion SSH
Write-Host "📡 Vérification de la connexion au NAS..." -ForegroundColor Yellow
try {
    ssh -o ConnectTimeout=5 "$NAS_USER@$NAS_HOST" "echo 'Connexion OK'" 2>$null | Out-Null
    Write-Host "✅ Connexion SSH établie" -ForegroundColor Green
} catch {
    Write-Host "❌ Impossible de se connecter au NAS" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez que :" -ForegroundColor Yellow
    Write-Host "1. SSH est activé sur le NAS (Panneau de configuration > Terminal & SNMP)"
    Write-Host "2. Votre clé SSH est dans ~/.ssh/authorized_keys sur le NAS"
    exit 1
}

# Créer le dossier sur le NAS
Write-Host ""
Write-Host "📁 Création du dossier de déploiement..." -ForegroundColor Yellow
ssh "$NAS_USER@$NAS_HOST" "sudo mkdir -p $NAS_PATH && sudo chown $NAS_USER $NAS_PATH"
Write-Host "✅ Dossier créé: $NAS_PATH" -ForegroundColor Green

# Copier les fichiers de configuration
Write-Host ""
Write-Host "📦 Copie des fichiers de configuration..." -ForegroundColor Yellow
scp -r config "$NAS_USER@${NAS_HOST}:$NAS_PATH/"
scp docker-compose.ghcr.yml "$NAS_USER@${NAS_HOST}:$NAS_PATH/"
Write-Host "✅ Fichiers copiés" -ForegroundColor Green

# Déployer le conteneur
Write-Host ""
Write-Host "🐳 Déploiement du conteneur Docker..." -ForegroundColor Yellow
ssh "$NAS_USER@$NAS_HOST" @"
    cd $NAS_PATH || exit 1
    
    echo '📥 Pull de la dernière image depuis GitHub...'
    sudo docker compose -f docker-compose.ghcr.yml pull
    
    echo '🔄 Redémarrage du conteneur...'
    sudo docker compose -f docker-compose.ghcr.yml down 2>/dev/null || true
    sudo docker compose -f docker-compose.ghcr.yml up -d
    
    echo ''
    echo '📊 Statut du conteneur:'
    sudo docker compose -f docker-compose.ghcr.yml ps
    
    echo ''
    echo '📋 Logs (dernières lignes):'
    sudo docker logs oneflex-bot 2>&1 | tail -10
"@

Write-Host ""
Write-Host "✅ Déploiement terminé!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Commandes utiles sur le NAS:" -ForegroundColor Cyan
Write-Host "  • Voir les logs:     sudo docker logs -f oneflex-bot"
Write-Host "  • Arrêter:           sudo docker compose -f $NAS_PATH/docker-compose.ghcr.yml down"
Write-Host "  • Redémarrer:        sudo docker compose -f $NAS_PATH/docker-compose.ghcr.yml restart"
Write-Host "  • Mettre à jour:     cd $NAS_PATH && sudo docker compose -f docker-compose.ghcr.yml pull && sudo docker compose -f docker-compose.ghcr.yml up -d"
Write-Host ""
