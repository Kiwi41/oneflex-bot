# 🐳 Image Docker OneFlex Bot

Image Docker officielle disponible sur GitHub Container Registry.

## 🚀 Utilisation rapide

### Pull de l'image

```bash
docker pull ghcr.io/kiwi41/oneflex-bot:latest
```

### Tags disponibles

- `latest` - Dernière version stable (branche main)
- `v1.0.0` - Version spécifique (si taggée)
- `main` - Build automatique de la branche main

## 📦 docker-compose

```yaml
version: '3.8'

services:
  oneflex-bot:
    image: ghcr.io/kiwi41/oneflex-bot:latest
    container_name: oneflex-bot
    restart: unless-stopped
    
    volumes:
      - ./config/.env:/app/config/.env:ro
      - ./logs:/app/logs
    
    environment:
      - TZ=Europe/Paris
    
    command: python main.py --schedule
```

## 🔧 Configuration

1. Créer un fichier `config/.env` :

```bash
mkdir -p config
cat > config/.env << 'EOF'
ONEFLEX_TOKEN=votre_token
ONEFLEX_REFRESH_TOKEN=votre_refresh_token
RESERVATION_TIME=03:05
RESERVATION_DAYS_OF_WEEK=1,2,3,4,5
RECURRING_WEEKS=4
EOF
```

2. Lancer le container :

```bash
docker-compose up -d
```

## 📱 Synology NAS

L'image est compatible avec les NAS Synology (architectures AMD64 et ARM64).

Voir le guide complet : [SYNOLOGY.md](SYNOLOGY.md)

## 🏗️ Build de l'image

L'image est automatiquement buildée et publiée sur GHCR à chaque push sur `main` via GitHub Actions.

### Build local (optionnel)

```bash
docker build -t oneflex-bot .
```

## 🔄 Mise à jour

```bash
# Pull de la dernière version
docker-compose pull

# Redémarrer avec la nouvelle image
docker-compose up -d
```

## 📋 Variables d'environnement

Voir [.env.example](.env.example) pour la liste complète des variables disponibles.

## 🐛 Troubleshooting

### Voir les logs

```bash
docker-compose logs -f
```

### Redémarrer le container

```bash
docker-compose restart
```

### Recréer le container

```bash
docker-compose down
docker-compose up -d
```
