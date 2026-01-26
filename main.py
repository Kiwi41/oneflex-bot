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
        
        # Si pas d'ID spécifié, utiliser le bureau favori
        if not desk_id or not space_id:
            logger.info("🔍 Recherche de votre bureau favori...")
            favorite = self.client.get_favorite_desk()
            
            if not favorite:
                logger.error("❌ Impossible de trouver un bureau favori")
                return False
            
            desk_id = favorite['desk_id']
            space_id = favorite['space_id']
            desk_name = favorite['name']
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
                if days_until == 0 and week == 0:
                    days_until = 7  # Si c'est aujourd'hui, prendre la semaine prochaine
                
                target_date = today + timedelta(days=days_until + (week * 7))
                dates_to_book.append(target_date)
        
        # Trier les dates
        dates_to_book.sort()
        
        # Réserver chaque date
        stats = {'success': 0, 'failed': 0, 'already_booked': 0}
        
        for date in dates_to_book:
            date_obj = datetime.combine(date, datetime.min.time())
            day_name = day_names.get(date.isoweekday(), str(date.isoweekday()))
            
            logger.info(f"📅 {day_name} {date.strftime('%d/%m/%Y')}")
            
            success = self.client.book_desk(
                desk_id=desk_id,
                space_id=space_id,
                date=date_obj,
                desk_name=desk_name
            )
            
            if success:
                stats['success'] += 1
            else:
                # Vérifier si c'est déjà réservé ou une autre erreur
                stats['already_booked'] += 1
            
            # Petite pause entre les réservations
            import time
            time.sleep(0.5)
        
        # Afficher le résumé
        logger.info(f"\n✅ Résumé:")
        logger.info(f"  • Réservations créées: {stats['success']}")
        logger.info(f"  • Déjà réservé/Échecs: {stats['already_booked']}")
        logger.info(f"  • Total tenté: {len(dates_to_book)}")
        
        return stats
    
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
    
    def schedule_daily_booking(self):
        """Configure une réservation automatique quotidienne"""
        logger.info(f"⏰ Réservation automatique configurée pour {Config.RESERVATION_TIME}")
        
        schedule.every().day.at(Config.RESERVATION_TIME).do(
            self.book_next_available
        )
        
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
        bot.book_recurring_days()
        bot.show_my_bookings()
    
    # Réservation récurrente avec nombre de semaines personnalisé
    elif len(sys.argv) == 3 and sys.argv[1] == '--recurring':
        try:
            weeks = int(sys.argv[2])
            bot.book_recurring_days(weeks_ahead=weeks)
            bot.show_my_bookings()
        except ValueError:
            logger.error("❌ Le nombre de semaines doit être un entier")
    
    # Réserver pour une date spécifique (YYYY-MM-DD)
    elif len(sys.argv) == 3 and sys.argv[1] == '--date':
        try:
            date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
            bot.book_next_available(date=date)
            bot.show_my_bookings()
        except ValueError:
            logger.error("❌ Format de date invalide. Utilisez YYYY-MM-DD")
    
    # Aide
    else:
        print("""
Usage: python main.py [OPTIONS]

Options:
  (aucun)              Réserve un bureau selon RESERVATION_DAYS_AHEAD
  --schedule           Lance le bot en mode automatique quotidien
  --show               Affiche vos réservations actuelles
  --date YYYY-MM-DD    Réserve pour une date spécifique
  --recurring [WEEKS]  Réserve selon les jours configurés dans RESERVATION_DAYS_OF_WEEK
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
