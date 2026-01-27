#!/usr/bin/env python3
"""
Script de test pour les notifications Discord
"""
from notifications import NotificationService

# Créer le service de notification
notif = NotificationService()

# Test 1: Notification de succès de réservation
print("📤 Test 1: Notification de succès...")
notif.send_booking_success(count=5, weeks=4)

# Test 2: Alerte d'expiration de token
print("📤 Test 2: Alerte d'expiration de token...")
notif.send_token_expired_alert("Test d'alerte - token expiré")

print("\n✅ Tests envoyés! Vérifie ton canal Discord.")
