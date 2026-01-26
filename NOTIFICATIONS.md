# 🔔 Système de Notifications OneFlex Bot

Le bot peut vous alerter en cas de problème, notamment quand le token expire et ne peut plus être rafraîchi.

## 📋 Types de notifications

### 1. Token expiré (Critique ⚠️)
Vous serez alerté si :
- Le token d'accès ne peut plus être rafraîchi
- Le refresh_token est invalide
- Le serveur refuse le rafraîchissement

### 2. Réservations créées (Info ✅)
Notification de succès après chaque session de réservation

### 3. Échec de réservation (Erreur ❌)
Alerte si une erreur critique survient pendant la réservation

---

## 🔗 Configuration Webhook (Recommandé)

Les webhooks permettent d'envoyer des alertes vers Discord, Slack, Microsoft Teams, etc.

### Discord

1. Ouvrez votre serveur Discord
2. Allez dans **Paramètres du salon** > **Intégrations** > **Webhooks**
3. Cliquez sur **Nouveau Webhook**
4. Copiez l'URL du webhook
5. Ajoutez dans votre `.env` :

```bash
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefgh...
```

### Slack

1. Créez une [Incoming Webhook App](https://api.slack.com/messaging/webhooks)
2. Choisissez le canal de destination
3. Copiez l'URL du webhook
4. Ajoutez dans votre `.env` :

```bash
NOTIFICATION_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
```

### Exemple de notification Discord

```json
{
  "embeds": [{
    "title": "OneFlex Bot Notification",
    "description": "⚠️ Le token d'authentification a expiré...",
    "color": 16753920,
    "timestamp": "2026-01-26T15:30:00Z"
  }]
}
```

---

## 📧 Configuration Email (Optionnel)

Pour recevoir des alertes par email.

### Gmail

1. Activez l'authentification à 2 facteurs sur votre compte Gmail
2. Générez un [mot de passe d'application](https://myaccount.google.com/apppasswords)
3. Configurez votre `.env` :

```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_TO=votre.email@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Mot de passe d'application
```

### Outlook/Office 365

```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_TO=destinataire@example.com
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=votre.email@outlook.com
SMTP_PASSWORD=votre_mot_de_passe
```

### Serveur SMTP personnalisé

```bash
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_TO=admin@example.com
SMTP_HOST=mail.example.com
SMTP_PORT=587
SMTP_USER=bot@example.com
SMTP_PASSWORD=password123
```

---

## 🧪 Tester les notifications

### Test manuel en Python

```python
from notifications import notification_service

# Test alerte token expiré
notification_service.send_token_expired_alert("Test d'alerte")

# Test succès réservation
notification_service.send_booking_success(5, weeks=4)

# Test échec réservation
notification_service.send_booking_failure("Erreur de test")
```

### Test depuis le terminal

Créez un fichier `test_notifications.py` :

```python
from notifications import notification_service
notification_service.send_token_expired_alert("Test de notification - Token expiré")
```

Puis exécutez :

```bash
python test_notifications.py
```

---

## 📊 Exemples de messages

### Token expiré

```
⚠️ ALERTE ONEFLEX BOT ⚠️

Le token d'authentification a expiré et ne peut plus être rafraîchi.

Détails:
- Date: 2026-01-26 15:30:45
- Erreur: Impossible de rafraîchir le token (HTTP 401)

Actions requises:
1. Récupérez un nouveau token via: python auto_get_tokens.py
2. Mettez à jour votre fichier .env
3. Redémarrez le bot

Documentation: GET_TOKEN.md
```

### Réservations réussies

```
✅ OneFlex Bot - Réservations effectuées

- 20 réservation(s) créée(s) avec succès
- Période: 4 semaine(s)
- Date: 2026-01-26 03:05:12
```

---

## 🐳 Configuration Docker

Si vous utilisez Docker, assurez-vous que les variables d'environnement sont bien passées :

```yaml
# docker-compose.yml
services:
  oneflex-bot:
    environment:
      - NOTIFICATION_WEBHOOK_URL=${NOTIFICATION_WEBHOOK_URL}
      - NOTIFICATION_EMAIL_ENABLED=${NOTIFICATION_EMAIL_ENABLED}
      - NOTIFICATION_EMAIL_TO=${NOTIFICATION_EMAIL_TO}
      # ... autres variables SMTP
```

Ou montez directement le fichier `.env` :

```yaml
volumes:
  - ./config/.env:/app/config/.env
```

---

## 🔕 Désactiver les notifications

Par défaut, **seules les alertes critiques** (token expiré) sont envoyées.

Pour désactiver complètement :
- Ne configurez pas `NOTIFICATION_WEBHOOK_URL`
- Mettez `NOTIFICATION_EMAIL_ENABLED=false`

Les logs seront toujours écrits dans la console/fichier de log.

---

## 💡 Recommandations

### Pour un usage personnel
- **Webhook Discord** : Créez un serveur Discord privé avec un canal #oneflex-alerts

### Pour une équipe
- **Slack** : Canal dédié pour toute l'équipe
- **Email** : Liste de diffusion pour les administrateurs

### Pour un NAS/Serveur
- **Webhook** : Plus fiable que l'email (pas de config SMTP complexe)
- **Logs** : Toujours activés en complément

---

## ❓ FAQ

**Q: Les notifications sont-elles obligatoires ?**  
R: Non, le bot fonctionne sans notifications. Elles sont juste pratiques pour être alerté rapidement.

**Q: Puis-je utiliser plusieurs webhooks ?**  
R: Non, un seul webhook pour le moment. Mais vous pouvez utiliser un service comme Zapier pour rediriger vers plusieurs destinations.

**Q: Les emails contiennent-ils mes tokens ?**  
R: Non, les messages ne contiennent jamais de données sensibles, seulement des codes d'erreur.

**Q: Quelle est la fréquence des notifications ?**  
R: 
- Token expiré : Une fois quand détecté
- Réservations : Après chaque session (quotidien en mode --schedule)
- Échecs : À chaque erreur critique
