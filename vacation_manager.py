"""
Gestionnaire de périodes de vacances/absences
"""
from datetime import datetime, date
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class VacationManager:
    """Gère les périodes de vacances et l'annulation des réservations"""
    
    def __init__(self, vacation_dates_str: str = ""):
        """
        Initialise le gestionnaire de vacances
        
        Args:
            vacation_dates_str: String au format "2026-02-10:2026-02-14,2026-03-01:2026-03-07"
        """
        self.vacation_periods: List[Tuple[date, date]] = []
        self._parse_vacation_dates(vacation_dates_str)
    
    def _parse_vacation_dates(self, dates_str: str):
        """Parse la chaîne de dates de vacances"""
        if not dates_str:
            return
        
        try:
            # Format: date1:date2,date3:date4
            for period in dates_str.split(','):
                period = period.strip()
                if not period:
                    continue
                
                if ':' in period:
                    # Période (date début:date fin)
                    start_str, end_str = period.split(':')
                    start = datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
                    end = datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
                    self.vacation_periods.append((start, end))
                else:
                    # Date unique
                    single_date = datetime.strptime(period.strip(), '%Y-%m-%d').date()
                    self.vacation_periods.append((single_date, single_date))
            
            if self.vacation_periods:
                logger.info(f"📅 Périodes de vacances configurées: {len(self.vacation_periods)} période(s)")
                for start, end in self.vacation_periods:
                    if start == end:
                        logger.info(f"   • {start.strftime('%d/%m/%Y')}")
                    else:
                        logger.info(f"   • {start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')}")
        
        except ValueError as e:
            logger.warning(f"⚠️ Erreur lors du parsing des dates de vacances: {e}")
            logger.warning("Format attendu: YYYY-MM-DD:YYYY-MM-DD,YYYY-MM-DD:YYYY-MM-DD")
    
    def is_vacation_day(self, check_date: date) -> bool:
        """
        Vérifie si une date est pendant les vacances
        
        Args:
            check_date: Date à vérifier
            
        Returns:
            True si la date est pendant les vacances
        """
        for start, end in self.vacation_periods:
            if start <= check_date <= end:
                return True
        return False
    
    def filter_vacation_dates(self, dates: List[date]) -> List[date]:
        """
        Filtre une liste de dates pour exclure les vacances
        
        Args:
            dates: Liste de dates à filtrer
            
        Returns:
            Liste de dates sans les jours de vacances
        """
        if not self.vacation_periods:
            return dates
        
        filtered = []
        excluded_count = 0
        
        for d in dates:
            if self.is_vacation_day(d):
                excluded_count += 1
                logger.debug(f"   ⊗ {d.strftime('%d/%m/%Y')} - Vacances")
            else:
                filtered.append(d)
        
        if excluded_count > 0:
            logger.info(f"🏖️ {excluded_count} jour(s) de vacances exclu(s)")
        
        return filtered
    
    def get_vacation_bookings_to_cancel(self, all_bookings: List[dict]) -> List[dict]:
        """
        Identifie les réservations à annuler car elles tombent pendant les vacances
        
        Args:
            all_bookings: Liste de toutes les réservations
            
        Returns:
            Liste des réservations à annuler
        """
        if not self.vacation_periods:
            return []
        
        to_cancel = []
        
        for booking in all_bookings:
            booking_date_str = booking.get('date')
            if not booking_date_str:
                continue
            
            try:
                booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
                if self.is_vacation_day(booking_date):
                    to_cancel.append(booking)
            except ValueError:
                continue
        
        return to_cancel
    
    def get_upcoming_vacations(self) -> List[Tuple[date, date]]:
        """
        Retourne les périodes de vacances futures
        
        Returns:
            Liste des périodes de vacances à venir
        """
        today = date.today()
        return [(start, end) for start, end in self.vacation_periods if end >= today]
    
    def format_vacations_summary(self) -> str:
        """Retourne un résumé formaté des vacances"""
        if not self.vacation_periods:
            return "Aucune période de vacances configurée"
        
        upcoming = self.get_upcoming_vacations()
        if not upcoming:
            return "Aucune période de vacances à venir"
        
        lines = ["🏖️ Périodes de vacances à venir:"]
        for start, end in upcoming:
            if start == end:
                lines.append(f"   • {start.strftime('%d/%m/%Y')}")
            else:
                days = (end - start).days + 1
                lines.append(f"   • {start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')} ({days} jours)")
        
        return "\n".join(lines)
