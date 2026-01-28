# 🪟 Déploiement OneFlex Bot sur NAS depuis Windows

Ce guide explique comment déployer le bot OneFlex sur un Synology NAS depuis Windows.

## Prérequis

### 1. Activer SSH sur le NAS
1. Ouvrez le **Panneau de configuration** du Synology
2. Allez dans **Terminal & SNMP**
3. Cochez **Activer le service SSH**
4. Port: **22** (par défaut)

### 2. Configurer l'authentification SSH (depuis Windows)

#### Option A : Avec OpenSSH (Windows 10+)
```powershell
# Générer une clé SSH (si vous n'en avez pas)
ssh-keygen -t ed25519 -C "oneflex-deploy"

# Copier la clé sur le NAS
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh kiwi@192.168.0.191 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

#### Option B : Avec PuTTY
1. Ouvrez **PuTTYgen**
2. Générez une paire de clés SSH
3. Copiez la clé publique
4. Connectez-vous au NAS avec PuTTY
5. Sur le NAS:
```bash
mkdir -p ~/.ssh
echo 'VOTRE_CLE_PUBLIQUE' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 3. Tester la connexion SSH
```powershell
ssh kiwi@192.168.0.191 "echo 'Connexion OK'"
```

## 🚀 Déploiement

### Depuis Windows avec PowerShell

1. **Ouvrir PowerShell** dans le dossier du projet:
```powershell
cd C:\path\to\oneflex-bot
```

2. **Exécuter le script de déploiement**:
```powershell
.\deploy-to-nas.ps1
```

Le script va:
- ✅ Vérifier la connexion SSH
- ✅ Créer le dossier `/volume1/docker/oneflex` sur le NAS
- ✅ Copier les fichiers de configuration
- ✅ Pull l'image Docker depuis GitHub Container Registry
- ✅ Lancer le conteneur

### Depuis WSL (Linux sous Windows)

Si vous préférez utiliser WSL:
```bash
./deploy-to-nas.sh
```

## 📊 Vérifier le déploiement

### Via SSH depuis Windows
```powershell
ssh kiwi@192.168.0.191 "sudo docker logs -f oneflex-bot"
```

### Via l'interface web du NAS
1. Ouvrez **Docker** dans le Synology DSM
2. Allez dans **Conteneur**
3. Vérifiez que `oneflex-bot` est en cours d'exécution
4. Double-cliquez pour voir les logs

## 🔄 Mise à jour

Pour mettre à jour le bot vers la dernière version:

```powershell
ssh kiwi@192.168.0.191 @"
    cd /volume1/docker/oneflex
    sudo docker compose -f docker-compose.ghcr.yml pull
    sudo docker compose -f docker-compose.ghcr.yml up -d
"@
```

Ou relancez simplement:
```powershell
.\deploy-to-nas.ps1
```

## 🛠️ Commandes utiles

### Voir les logs en temps réel
```powershell
ssh kiwi@192.168.0.191 "sudo docker logs -f oneflex-bot"
```

### Redémarrer le bot
```powershell
ssh kiwi@192.168.0.191 "sudo docker compose -f /volume1/docker/oneflex/docker-compose.ghcr.yml restart"
```

### Arrêter le bot
```powershell
ssh kiwi@192.168.0.191 "sudo docker compose -f /volume1/docker/oneflex/docker-compose.ghcr.yml down"
```

### Voir les réservations actuelles
```powershell
ssh kiwi@192.168.0.191 "sudo docker exec oneflex-bot python main.py --show"
```

## ⚙️ Configuration

Les fichiers de configuration sont dans `config/.env` sur le NAS.

Pour modifier:
1. Éditez `config/.env` localement
2. Relancez `.\deploy-to-nas.ps1` pour copier la nouvelle configuration
3. Le conteneur redémarre automatiquement avec la nouvelle config

## 🐛 Dépannage

### Erreur "Permission denied (publickey)"
- Vérifiez que votre clé SSH est bien dans `~/.ssh/authorized_keys` sur le NAS
- Vérifiez les permissions: `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`

### Erreur "Cannot connect to the Docker daemon"
- Docker n'est pas installé ou pas démarré sur le NAS
- Installez Docker depuis le **Centre de paquets** du Synology

### Le bot ne réserve rien
- Vérifiez les logs: `ssh kiwi@192.168.0.191 "sudo docker logs oneflex-bot"`
- Vérifiez la configuration dans `config/.env`
- Vérifiez que les tokens sont valides

### Notification Discord ne fonctionne pas
- Vérifiez `NOTIFICATION_WEBHOOK_URL` dans `config/.env`
- Testez le webhook manuellement
