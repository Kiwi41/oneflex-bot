"""
Bot de réservation OneFlex
"""
from datetime import datetime, timedelta
import logging
import schedule
import time
from typing import Optional

from config import Config
from oneflex_client import OneFlexClient
from notifications import notification_service
from vacation_manager import VacationManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OneFlexBot:
    """Bot pour automatiser les réservations OneFlex"""
    
    def __init__(self):
        Config.validate()
        # Utiliser le token si disponible (pour SSO), sinon email/password
        if Config.TOKEN:
            self.client = OneFlexClient(
                token=Config.TOKEN,
                refresh_token=Config.REFRESH_TOKEN
            )
        else:
            self.client = OneFlexClient(Config.EMAIL, Config.PASSWORD)
        self.is_logged_in = False
        
        # Initialiser le gestionnaire de vacances
        self.vacation_manager = VacationManager(Config.VACATION_DATES)
    
    def connect(self) -> bool:
        """Établit la connexion avec OneFlex"""
        if not self.is_logged_in:
            self.is_logged_in = self.client.login()
        return self.is_logged_in
    
    def book_next_available(
        self, 
        date: Optional[datetime] = None,
        days_ahead: int = None,
        desk_id: Optional[str] = None,
        space_id: Optional[str] = None
    ) -> bool:
        """
        Réserve votre bureau favori (ou un bureau spécifique)
        
        Args:
            date: Date de réservation (par défaut selon Config)
            days_ahead: Nombre de jours à l'avance (surcharge Config)
            desk_id: ID du bureau spécifique (optionnel)
            space_id: ID de l'espace spécifique (optionnel)
            
        Returns:
            bool: True si la réservation est réussie
        """
        if not self.connect():
            return False
        
        # Déterminer la date de réservation
        if date is None:
            days = days_ahead if days_ahead else Config.RESERVATION_DAYS_AHEAD
            date = datetime.now() + timedelta(days=days)
        
        # Si pas d'ID spécifié, utiliser le bureau favori avec fallback
        if not desk_id or not space_id:
            logger.info("🔍 Recherche de vos bureaux favoris...")
            favorite_desks = self.client.get_favorite_desks()
            
            if not favorite_desks:
                logger.error("❌ Impossible de trouver un bureau favori")
                return False
            
            # Essayer chaque bureau dans l'ordre de préférence
            for i, desk in enumerate(favorite_desks):
                desk_id = desk['desk_id']
                space_id = desk['space_id']
                desk_name = desk['name']
                
                if i == 0:
                    logger.info(f"🎯 Essai du bureau principal: {desk_name}")
                else:
                    logger.info(f"🔄 Essai du bureau alternatif #{i}: {desk_name}")
                
                logger.info(f"📅 Date: {date.strftime('%d/%m/%Y')}")
                
                # Tenter la réservation
                success = self.client.book_desk(
                    desk_id=desk_id,
                    space_id=space_id,
                    date=date,
                    desk_name=desk_name
                )
                
                if success:
                    return True
                
                # Si ce n'est pas le dernier bureau, continuer
                if i < len(favorite_desks) - 1:
                    logger.warning(f"⚠️ Bureau occupé, essai du suivant...")
            
            # Aucun bureau n'est disponible
            logger.error(f"❌ Aucun de vos {len(favorite_desks)} bureau(x) favori(s) n'est disponible")
            return False
        else:
            desk_name = Config.DESK_NAME if hasattr(Config, 'DESK_NAME') else "Bureau"
        
        logger.info(f"🎯 Réservation du bureau: {desk_name}")
        logger.info(f"📅 Date: {date.strftime('%d/%m/%Y')}")
        
        # Réserver le bureau
        success = self.client.book_desk(
            desk_id=desk_id,
            space_id=space_id,
            date=date,
            desk_name=desk_name
        )
        
        return success
    
    def book_recurring_days(self, weeks_ahead: int = 4) -> dict:
        """
        Réserve selon les jours de semaine configurés (ex: tous les lundis, mercredis, vendredis)
        
        Args:
            weeks_ahead: Nombre de semaines à l'avance à réserver
            
        Returns:
            dict: Statistiques des réservations (succès, échecs, déjà réservé)
        """
        if not Config.RESERVATION_DAYS_OF_WEEK:
            logger.error("❌ RESERVATION_DAYS_OF_WEEK n'est pas configuré dans .env")
            return {'success': 0, 'failed': 0, 'already_booked': 0}
        
        if not self.connect():
            return {'success': 0, 'failed': 0, 'already_booked': 0}
        
        # Parser les jours de la semaine (1=Lundi, 7=Dimanche)
        try:
            days_of_week = [int(d.strip()) for d in Config.RESERVATION_DAYS_OF_WEEK.split(',')]
        except ValueError:
            logger.error("❌ Format invalide pour RESERVATION_DAYS_OF_WEEK. Utilisez des chiffres séparés par des virgules (ex: 1,3,5)")
            return {'success': 0, 'failed': 0, 'already_booked': 0}
        
        # Noms des jours pour l'affichage
        day_names = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
        selected_days = [day_names.get(d, str(d)) for d in days_of_week]
        
        logger.info(f"📅 Réservation récurrente pour: {', '.join(selected_days)}")
        logger.info(f"⏱️ Période: {weeks_ahead} semaines à l'avance")
        
        # Récupérer le bureau favori une seule fois
        logger.info("🔍 Recherche de votre bureau favori...")
        favorite = self.client.get_favorite_desk()
        
        if not favorite:
            logger.error("❌ Impossible de trouver un bureau favori")
            return {'success': 0, 'failed': 0, 'already_booked': 0}
        
        desk_id = favorite['desk_id']
        space_id = favorite['space_id']
        desk_name = favorite['name']
        
        logger.info(f"🎯 Bureau: {desk_name}\n")
        
        # Générer toutes les dates à réserver
        dates_to_book = []
        today = datetime.now().date()
        
        for week in range(weeks_ahead):
            for day_of_week in days_of_week:
                # Calculer la date
                days_until = (day_of_week - today.isoweekday()) % 7
                if days_until == 0:
                    days_until = 7  # Si c'est le même jour, toujours prendre la semaine suivante
                
                target_date = today + timedelta(days=days_until + (week * 7))
                dates_to_book.append(target_date)
        
        # Trier les dates
        dates_to_book.sort()
        
        # Filtrer les dates de vacances
        dates_to_book = self.vacation_manager.filter_vacation_dates(dates_to_book)
        
        if not dates_to_book:
            logger.warning("⚠️ Aucune date à réserver (toutes sont en vacances)")
            return {'success': 0, 'failed': 0, 'already_booked': 0}
        
        # Réserver chaque date
        stats = {'success': 0, 'failed': 0, 'already_booked': 0}
        new_bookings = []  # Tracker uniquement les NOUVELLES réservations
        
        for date in dates_to_book:
            date_obj = datetime.combine(date, datetime.min.time())
            day_name = day_names.get(date.isoweekday(), str(date.isoweekday()))
            
            logger.info(f"📅 {day_name} {date.strftime('%d/%m/%Y')}")
            
            success, already_existed = self.client.book_desk(
                desk_id=desk_id,
                space_id=space_id,
                date=date_obj,
                desk_name=desk_name
            )
            
            if success:
                if already_existed:
                    stats['already_booked'] += 1
                else:
                    stats['success'] += 1
                    new_bookings.append(date.strftime('%d/%m/%Y'))  # Nouvelle réservation
            else:
                stats['failed'] += 1
            
            # Petite pause entre les réservations
            import time
            time.sleep(0.5)
        
        # Afficher le résumé
        logger.info(f"\n✅ Résumé:")
        logger.info(f"  • Nouvelles réservations: {stats['success']}")
        logger.info(f"  • Déjà réservé: {stats['already_booked']}")
        logger.info(f"  • Échecs: {stats['failed']}")
        logger.info(f"  • Total tenté: {len(dates_to_book)}")
        
        # Envoyer notification UNIQUEMENT si nouvelles réservations
        if stats['success'] > 0:
            notification_service.send_booking_success(stats['success'], weeks_ahead, new_bookings)
        elif stats['already_booked'] > 0 and stats['failed'] == 0:
            logger.info("ℹ️  Aucune nouvelle réservation (toutes déjà existantes)")
        
        return stats
    
    def send_daily_reminder(self):
        """Envoie un rappel avec les réservations du jour"""
        if not self.connect():
            logger.error("❌ Impossible de se connecter pour le rappel")
            return
        
        bookings = self.client.get_today_bookings()
        
        if not bookings:
            logger.info("ℹ️  Aucune réservation aujourd'hui")
            return
        
        # Envoyer la notification avec les détails
        notification_service.send_daily_reminder(bookings)
        logger.info(f"📬 Rappel envoyé : {len(bookings)} réservation(s) aujourd'hui")
    
    def show_my_bookings(self):
        """Affiche les réservations actuelles"""
        if not self.connect():
            return
        
        bookings = self.client.get_my_bookings()
        
        if not bookings:
            return
        
        logger.info(f"\n📅 Vos réservations ({len(bookings)}):")
        for booking in bookings:
            date = booking.get('date', 'N/A')
            moment = booking.get('moment', '')
            desk = booking.get('desk', {})
            space = booking.get('space', {})
            
            desk_name = desk.get('name', 'N/A') if desk else 'N/A'
            space_name = space.get('name', '') if space else ''
            
            moment_str = f" ({moment})" if moment else ""
            space_str = f" - {space_name}" if space_name else ""
            
            logger.info(f"  • {date}{moment_str}: {desk_name}{space_str}")
    
    def cancel_vacation_bookings(self):
        """Annule les réservations qui tombent pendant les vacances"""
        if not self.connect():
            return
        
        logger.info("\n🏖️ Vérification des réservations pendant les vacances...")
        
        # Récupérer toutes les réservations
        bookings = self.client.get_my_bookings(days=90)  # 3 mois à l'avance
        
        if not bookings:
            return
        
        # Identifier les réservations à annuler
        to_cancel = self.vacation_manager.get_vacation_bookings_to_cancel(bookings)
        
        if not to_cancel:
            logger.info("✅ Aucune réservation à annuler pendant les vacances")
            return
        
        logger.info(f"📋 {len(to_cancel)} réservation(s) à annuler:")
        
        cancelled_count = 0
        cancelled_list = []
        for booking in to_cancel:
            date = booking.get('date')
            moment = booking.get('moment', '')
            booking_id = booking.get('id')
            desk = booking.get('desk', {})
            desk_name = desk.get('name', 'Bureau') if desk else 'Bureau'
            
            logger.info(f"   🗑️  {date} ({moment}) - {desk_name}")
            
            if booking_id and self.client.cancel_booking(booking_id):
                cancelled_count += 1
                cancelled_list.append(booking)
        
        logger.info(f"\n✅ {cancelled_count}/{len(to_cancel)} réservation(s) annulée(s)\n")
        
        # Envoyer une notification si des réservations ont été annulées
        if cancelled_list:
            notification_service.send_vacation_cancellation(cancelled_list)
    
    def schedule_daily_booking(self):
        """Configure une réservation automatique quotidienne"""
        # Afficher les périodes de vacances configurées
        if Config.VACATION_DATES:
            logger.info(self.vacation_manager.format_vacations_summary())
        
        if Config.RECURRING_WEEKS > 0:
            logger.info(f"⏰ Réservation récurrente configurée pour {Config.RESERVATION_TIME}")
            logger.info(f"📅 Mode: {Config.RECURRING_WEEKS} semaines à l'avance sur les jours configurés")
            
            def job():
                # Annuler les réservations pendant les vacances si activé
                if Config.AUTO_CANCEL_VACATIONS and Config.VACATION_DATES:
                    self.cancel_vacation_bookings()
                
                # Réserver pour les semaines à venir (en excluant les vacances)
                self.book_recurring_days(Config.RECURRING_WEEKS)
            
            schedule.every().day.at(Config.RESERVATION_TIME).do(job)
            
            # Planifier le rappel matinal si configuré
            if Config.REMINDER_TIME:
                schedule.every().day.at(Config.REMINDER_TIME).do(self.send_daily_reminder)
                logger.info(f"⏰ Rappel matinal configuré pour {Config.REMINDER_TIME}")
                self.book_recurring_days(weeks_ahead=Config.RECURRING_WEEKS)
                self.show_my_bookings()
            
            schedule.every().day.at(Config.RESERVATION_TIME).do(job)
        else:
            logger.info(f"⏰ Réservation automatique configurée pour {Config.RESERVATION_TIME}")
            schedule.every().day.at(Config.RESERVATION_TIME).do(self.book_next_available)
        
        logger.info("🤖 Bot en attente... (Ctrl+C pour arrêter)")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
        except KeyboardInterrupt:
            logger.info("\n👋 Arrêt du bot")


def main():
    """Point d'entrée principal"""
    import sys
    
    bot = OneFlexBot()
    
    # Si aucun argument, réserver pour demain
    if len(sys.argv) == 1:
        logger.info("🚀 Lancement du bot OneFlex")
        bot.book_next_available()
        bot.show_my_bookings()
    
    # Mode planifié
    elif len(sys.argv) == 2 and sys.argv[1] == '--schedule':
        bot.schedule_daily_booking()
    
    # Afficher les réservations
    elif len(sys.argv) == 2 and sys.argv[1] == '--show':
        bot.show_my_bookings()
    
    # Réservation récurrente selon les jours de semaine configurés
    elif len(sys.argv) == 2 and sys.argv[1] == '--recurring':
        # Annuler les réservations pendant les vacances si activé
        if Config.AUTO_CANCEL_VACATIONS and Config.VACATION_DATES:
            bot.cancel_vacation_bookings()
        
        bot.book_recurring_days()
        bot.show_my_bookings()
    
    # Réservation récurrente avec nombre de semaines personnalisé
    elif len(sys.argv) == 3 and sys.argv[1] == '--recurring':
        try:
            weeks = int(sys.argv[2])
            
            # Annuler les réservations pendant les vacances si activé
            if Config.AUTO_CANCEL_VACATIONS and Config.VACATION_DATES:
                bot.cancel_vacation_bookings()
            
            bot.book_recurring_days(weeks_ahead=weeks)
            bot.show_my_bookings()
        except ValueError:
            logger.error("❌ Le nombre de semaines doit être un entier")
    
    # Réserver pour une date spécifique (YYYY-MM-DD)
    elif len(sys.argv) == 3 and sys.argv[1] == '--date':
        try:
            date = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
            # Vérifier si la date est pendant les vacances
            if Config.VACATION_DATES and bot.vacation_manager.is_vacation_day(date):
                logger.warning(f"⚠️ La date {date.strftime('%d/%m/%Y')} est pendant vos vacances configurées.")
                logger.warning("💡 Utilisez --force si vous voulez réserver quand même.")
                bot.show_my_bookings()
                return
            
            bot.book_next_available(date=date)
            bot.show_my_bookings()
        except ValueError:
            logger.error("❌ Format de date invalide. Utilisez YYYY-MM-DD")
    
    # Réservation pour une date spécifique (forcer même pendant vacances)
    elif len(sys.argv) == 4 and sys.argv[1] == '--date' and sys.argv[3] == '--force':
        try:
            date = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
            bot.book_next_available(date=date)
            bot.show_my_bookings()
        except ValueError:
            logger.error("❌ Format de date invalide. Utilisez YYYY-MM-DD")
    
    # Aide
    else:
        print("""
Usage: python main.py [OPTIONS]

Options:
  (aucun)                    Réserve un bureau selon RESERVATION_DAYS_AHEAD
  --schedule                 Lance le bot en mode automatique quotidien
  --show                     Affiche vos réservations actuelles
  --date YYYY-MM-DD          Réserve pour une date spécifique (bloqué si vacances)
  --date YYYY-MM-DD --force  Force la réservation même pendant les vacances
  --recurring [WEEKS]        Réserve selon les jours configurés dans RESERVATION_DAYS_OF_WEEK
                             WEEKS: nombre de semaines (défaut: 4)

Exemples:
  python main.py
  python main.py --schedule
  python main.py --show
  python main.py --date 2026-02-01
  python main.py --recurring          # 4 semaines par défaut
  python main.py --recurring 8        # 8 semaines

Configuration récurrente (.env):
  RESERVATION_DAYS_OF_WEEK=1,3,5      # Lundi, Mercredi, Vendredi
  RESERVATION_DAYS_OF_WEEK=2,4        # Mardi, Jeudi
        """)


if __name__ == '__main__':
    main()
