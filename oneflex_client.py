"""
Client pour l'API OneFlex
"""
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import optionnel pour les notifications (éviter erreur circulaire)
try:
    from notifications import NotificationService
    notification_service = NotificationService()
except ImportError:
    notification_service = None


class OneFlexClient:
    """Client pour interagir avec l'API OneFlex (GraphQL)"""
    
    BASE_URL = "https://oneflex.myworldline.com/api"
    GQL_ENDPOINT = f"{BASE_URL}/gql"
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None, refresh_token: Optional[str] = None):
        self.email = email
        self.password = password
        self.token = token
        self.refresh_token = refresh_token
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        # Si un token est fourni directement, l'utiliser
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            logger.info("🔑 Token d'authentification fourni")
            if self.refresh_token:
                logger.info("🔄 Refresh token disponible pour auto-refresh")
    
    def refresh_access_token(self) -> bool:
        """
        Renouvelle l'access token en utilisant le refresh token
        Utilise l'endpoint /api/auth/token avec grant_type=refresh_token
        
        Returns:
            bool: True si le refresh est réussi
        """
        if not self.refresh_token:
            logger.error("❌ Aucun refresh token disponible")
            return False
        
        try:
            logger.info("🔄 Tentative de refresh du token...")
            
            # Utiliser l'endpoint /api/auth/token avec la méthode OAuth2 standard
            response = requests.post(
                f"{self.BASE_URL}/auth/token",
                json={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                
                if new_token:
                    # Mettre à jour le token en mémoire
                    self.token = new_token
                    self.session.headers.update({
                        'Authorization': f'Bearer {new_token}'
                    })
                    
                    # Sauvegarder le nouveau token dans .env
                    self._update_env_token(new_token)
                    
                    logger.info("✅ Token renouvelé avec succès")
                    return True
            
            logger.error(f"❌ Échec du refresh: HTTP {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du refresh: {e}")
            return False
    
    def _update_env_token(self, new_token: str):
        """
        Met à jour le token dans le fichier .env
        
        Args:
            new_token: Le nouveau access token
        """
        try:
            import os
            from pathlib import Path
            
            # Chemins possibles pour .env
            env_paths = [
                Path('.env'),
                Path(__file__).parent / '.env',
                Path('/app/.env'),  # Dans Docker (root)
                Path('/app/config/.env')  # Dans Docker (volume monté)
            ]
            
            env_file = None
            for path in env_paths:
                if path.exists():
                    env_file = path
                    break
            
            if not env_file:
                logger.warning("⚠️  Fichier .env non trouvé, token non sauvegardé")
                return
            
            # Lire le contenu actuel
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Mettre à jour la ligne ONEFLEX_TOKEN
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ONEFLEX_TOKEN='):
                    lines[i] = f'ONEFLEX_TOKEN={new_token}\n'
                    updated = True
                    break
            
            # Si la ligne n'existe pas, l'ajouter
            if not updated:
                lines.append(f'ONEFLEX_TOKEN={new_token}\n')
            
            # Écrire le nouveau contenu
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            logger.info(f"💾 Token mis à jour dans {env_file}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du .env: {e}")
    
    def _graphql_request(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        Exécute une requête GraphQL
        
        Args:
            query: Requête GraphQL
            variables: Variables de la requête
            
        Returns:
            Données de la réponse ou None en cas d'erreur
        """
        try:
            payload = {'query': query}
            if variables:
                payload['variables'] = variables
            
            response = self.session.post(self.GQL_ENDPOINT, json=payload)
            
            # Si erreur 401, tenter un refresh automatique
            if response.status_code == 401:
                logger.warning("⚠️  Token expiré, tentative de refresh automatique...")
                
                # Tenter le refresh une seule fois
                if self.refresh_access_token():
                    logger.info("✅ Token refreshé, nouvelle tentative de requête...")
                    # Réessayer la requête avec le nouveau token
                    response = self.session.post(self.GQL_ENDPOINT, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'errors' not in result:
                            return result.get('data')
                
                # Si le refresh échoue ou la requête échoue encore
                logger.error("❌ Refresh automatique échoué ou token toujours invalide")
                if notification_service:
                    notification_service.send_token_expired_alert(
                        "🔑 Token OneFlex expiré et refresh automatique échoué\n\n"
                        "Reconnectez-vous avec:\n"
                        "```\npython auto_get_tokens.py\n```\n"
                        "Puis redémarrez le bot Docker."
                    )
                return None
            
            # Afficher plus de détails en cas d'erreur
            if response.status_code != 200:
                logger.error(f"❌ Erreur HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None
            
            result = response.json()
            
            if 'errors' in result:
                logger.error(f"❌ Erreur GraphQL: {result['errors']}")
                return None
            
            return result.get('data')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur de requête: {e}")
            return None
    
    def login(self) -> bool:
        """
        Se connecte à l'API OneFlex via GraphQL
        Note: Avec SSO, utilisez plutôt l'initialisation avec token
        
        Returns:
            bool: True si la connexion est réussie
        """
        # Si un token existe déjà, vérifier qu'il fonctionne
        if self.token:
            return self.verify_token()
        
        # Login classique (ne fonctionne pas avec SSO)
        if not self.email or not self.password:
            logger.error("❌ Email/password requis ou utilisez un token")
            return False
        
        # TODO: Adapter cette requête selon la vraie requête GraphQL de OneFlex
        query = """
        mutation Login($email: String!, $password: String!) {
            login(email: $email, password: $password) {
                token
                user {
                    id
                    email
                }
            }
        }
        """
        
        variables = {
            'email': self.email,
            'password': self.password
        }
        
        data = self._graphql_request(query, variables)
        
        if data and 'login' in data:
            self.token = data['login'].get('token')
            
            if self.token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                logger.info("✅ Connexion réussie à OneFlex")
                return True
        
        logger.error("❌ Échec de connexion")
        return False
    
    def verify_token(self) -> bool:
        """
        Vérifie que le token est valide en récupérant le profil
        
        Returns:
            bool: True si le token est valide
        """
        # Utiliser une requête plus simple sans variables inutiles
        query = """
        query {
            me(languages: ["fr-FR", "fr"], defaultTimezone: "Europe/Paris") {
                id
                email
                firstName
                lastName
                fullName
            }
        }
        """
        
        data = self._graphql_request(query)
        
        if data and 'me' in data:
            user = data['me']
            logger.info(f"✅ Authentifié en tant que: {user.get('fullName', user.get('email'))}")
            return True
        
        logger.error("❌ Token invalide ou expiré")
        return False
    
    def get_available_desks(
        self, 
        date: datetime,
        site_id: Optional[str] = None,
        floor_id: Optional[str] = None,
        zone_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère les bureaux disponibles pour une date donnée
        
        Args:
            date: Date de réservation
            site_id: ID du site (optionnel)
            floor_id: ID de l'étage (optionnel)
            zone_id: ID de la zone (optionnel)
            
        Returns:
            Liste des bureaux disponibles
        """
        try:
            params = {
                'date': date.strftime('%Y-%m-%d')
            }
            
            if site_id:
                params['site_id'] = site_id
            if floor_id:
                params['floor_id'] = floor_id
            if zone_id:
                params['zone_id'] = zone_id
            
            response = self.session.get(
                f"{self.BASE_URL}/desks/available",
                params=params
            )
            response.raise_for_status()
            
            desks = response.json()
            logger.info(f"📍 {len(desks)} bureau(x) disponible(s) pour le {date.strftime('%d/%m/%Y')}")
            return desks
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur lors de la récupération des bureaux: {e}")
            return []
    
    def book_desk(
        self, 
        desk_id: str, 
        space_id: str,
        date: datetime, 
        moments: List[str] = None,
        desk_name: str = "Bureau"
    ) -> bool:
        """
        Réserve un bureau pour une date donnée via GraphQL
        
        Args:
            desk_id: ID du bureau à réserver
            space_id: ID de l'espace
            date: Date de réservation
            moments: Liste des moments (MORNING, AFTERNOON, ou les deux)
            desk_name: Nom du bureau (pour l'affichage)
            
        Returns:
            tuple: (success: bool, already_existed: bool)
                - (True, False): Nouvelle réservation créée
                - (True, True): Réservation déjà existante
                - (False, False): Échec de la réservation
        """
        # Vérifier si une réservation existe déjà pour cette date (n'importe quel bureau)
        if self.has_booking_for_date(date):
            logger.info(f"✅ Réservation déjà existante pour {desk_name} le {date.strftime('%d/%m/%Y')}")
            return (True, True)
        
        user_id = self.get_my_user_id()
        if not user_id:
            logger.error("❌ Impossible de récupérer l'ID utilisateur")
            return (False, False)
        
        # Par défaut, réserver toute la journée
        if not moments:
            moments = ["MORNING", "AFTERNOON"]
        
        # Créer les datedMoments
        dated_moments = [{"date": date.strftime('%Y-%m-%d'), "moment": moment} for moment in moments]
        
        query = """
        mutation createAffectation($data: CreateSimpleAffectationInput!) {
            createAffectation(data: $data) {
                id
                userId
                guestId
                deskId
                spaceId
                services {
                    id
                    type
                    parkingSpotId
                    __typename
                }
                __typename
            }
        }
        """
        
        variables = {
            'data': {
                'type': 'OFFICE',
                'datedMoments': dated_moments,
                'mainUserIdV2': user_id,
                'usersIdV2': [user_id],
                'teams': [],
                'guestsInfo': [],
                'spacesIdSelection': [space_id],
                'deskId': desk_id,
                'services': [],
                'desksAttributions': [],
                'withUsersSelectedDays': True
            }
        }
        
        data = self._graphql_request(query, variables)
        
        if data and 'createAffectation' in data:
            moments_str = " + ".join(moments)
            logger.info(f"✅ Réservation confirmée: {desk_name} le {date.strftime('%d/%m/%Y')} ({moments_str})")
            return (True, False)  # Nouvelle réservation créée
        
        logger.error(f"❌ Échec de la réservation")
        return (False, False)
    
    def cancel_booking(self, affectation_id: str) -> bool:
        """
        Annule une réservation existante
        
        Args:
            affectation_id: ID de la réservation à annuler
            
        Returns:
            True si l'annulation a réussi
        """
        query = """
        mutation deleteAffectation($affectationId: ID!, $deleteGuestsOf: Boolean!) {
            deleteAffectation(affectationId: $affectationId, deleteGuestsOf: $deleteGuestsOf) {
                success
            }
        }
        """
        
        variables = {
            'affectationId': affectation_id,
            'deleteGuestsOf': False
        }
        
        data = self._graphql_request(query, variables)
        
        if data and 'deleteAffectation' in data:
            result = data['deleteAffectation']
            if result.get('success', False):
                logger.info(f"✅ Réservation annulée: {affectation_id}")
                return True
        
        logger.error(f"❌ Échec de l'annulation de la réservation")
        return False
    
    def get_my_user_id(self) -> Optional[Dict]:
        """
        Récupère l'ID de l'utilisateur connecté
        
        Returns:
            Dict avec l'ID et le type de l'utilisateur
        """
        query = """
        query {
            me(languages: ["fr-FR"], defaultTimezone: "Europe/Paris") {
                id
            }
        }
        """
        
        data = self._graphql_request(query)
        
        if data and 'me' in data:
            return {
                'id': data['me']['id'],
                'type': 'Internal'
            }
        return None
    
    def get_favorite_desks(self) -> List[Dict]:
        """
        Récupère la liste des bureaux favoris de l'utilisateur
        
        Returns:
            Liste des bureaux favoris (desk_id, space_id, name) par ordre de préférence
        """
        user_id = self.get_my_user_id()
        if not user_id:
            return []
        
        # Récupérer les bureaux favoris
        query = """
        query userFavoriteSpacesAndDesks($userId: UserIdType!) {
            user(idV2: $userId) {
                id
                favoriteSpacesAndDesks {
                    id
                    space {
                        id
                        name
                        __typename
                    }
                    desk {
                        id
                        name
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
        """
        
        variables = {'userId': user_id}
        data = self._graphql_request(query, variables)
        
        favorite_desks = []
        
        if data and 'user' in data and 'favoriteSpacesAndDesks' in data['user']:
            favorites = data['user']['favoriteSpacesAndDesks']
            for fav in favorites:
                if fav.get('desk') and fav.get('space'):
                    favorite_desks.append({
                        'desk_id': fav['desk']['id'],
                        'space_id': fav['space']['id'],
                        'name': fav['desk'].get('name', 'Bureau favori')
                    })
        
        # Si aucun favori explicite, utiliser les bureaux les plus réservés
        if not favorite_desks:
            bookings = self.get_my_bookings(days=90)
            if bookings:
                desk_count = {}
                for booking in bookings:
                    if booking.get('desk') and booking.get('space'):
                        desk_id = booking['desk']['id']
                        if desk_id not in desk_count:
                            desk_count[desk_id] = {
                                'count': 0,
                                'desk_id': desk_id,
                                'space_id': booking['space']['id'],
                                'name': booking['desk'].get('name', 'Bureau')
                            }
                        desk_count[desk_id]['count'] += 1
                
                # Trier par nombre de réservations (décroissant)
                sorted_desks = sorted(desk_count.values(), key=lambda x: x['count'], reverse=True)
                for desk_info in sorted_desks:
                    favorite_desks.append({
                        'desk_id': desk_info['desk_id'],
                        'space_id': desk_info['space_id'],
                        'name': desk_info['name']
                    })
        
        return favorite_desks
    
    def get_favorite_desk(self) -> Optional[Dict]:
        """
        Récupère le bureau favori principal de l'utilisateur
        
        Returns:
            Dict avec les infos du bureau favori (desk_id, space_id, name)
        """
        favorites = self.get_favorite_desks()
        
        if favorites:
            desk = favorites[0]
            if len(favorites) > 1:
                logger.info(f"📌 Bureau favori principal: {desk['name']} (+{len(favorites)-1} alternative(s))")
            else:
                logger.info(f"📌 Bureau favori: {desk['name']}")
            return desk
        
        return None
    
    def get_my_bookings(self, days: int = 30) -> List[Dict]:
        """
        Récupère les réservations (affectations) de l'utilisateur
        
        Args:
            days: Nombre de jours à récupérer (par défaut 30)
        
        Returns:
            Liste des réservations
        """
        user_id = self.get_my_user_id()
        if not user_id:
            logger.error("❌ Impossible de récupérer l'ID utilisateur")
            return []
        
        # Générer les dates pour les X prochains jours
        from datetime import datetime, timedelta
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        
        query = """
        query affectationsByUserAndDates($userId: UserIdType!, $affectationsFilter: GetAffectationsFilter!) {
            user(idV2: $userId) {
                id
                affectations(affectationFilter: $affectationsFilter) {
                    id
                    date
                    moment
                    active
                    desk {
                        id
                        name
                        coordinates
                        __typename
                    }
                    space {
                        id
                        name
                        inheritedName
                        serviceType
                        __typename
                    }
                    type
                    description
                    __typename
                }
                __typename
            }
        }
        """
        
        variables = {
            'userId': user_id,
            'affectationsFilter': {
                'dates': dates,
                'withAuthoredSuggestions': True
            }
        }
        
        data = self._graphql_request(query, variables)
        
        if data and 'user' in data and 'affectations' in data['user']:
            affectations = data['user']['affectations']
            logger.info(f"📅 Vous avez {len(affectations)} réservation(s)")
            return affectations
        
        logger.info("📅 Aucune réservation active")
        return []
    
    def has_booking_for_date(self, date: datetime, desk_id: Optional[str] = None) -> bool:
        """
        Vérifie si une réservation existe déjà pour une date donnée
        
        Args:
            date: Date à vérifier
            desk_id: ID du bureau spécifique (optionnel, vérifie n'importe quel bureau si None)
            
        Returns:
            bool: True si une réservation existe déjà
        """
        user_id = self.get_my_user_id()
        if not user_id:
            return False
        
        date_str = date.strftime('%Y-%m-%d')
        
        query = """
        query affectationsByUserAndDates($userId: UserIdType!, $affectationsFilter: GetAffectationsFilter!) {
            user(idV2: $userId) {
                id
                affectations(affectationFilter: $affectationsFilter) {
                    id
                    date
                    active
                    desk {
                        id
                        name
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
        """
        
        variables = {
            'userId': user_id,
            'affectationsFilter': {
                'dates': [date_str],
                'withAuthoredSuggestions': True
            }
        }
        
        data = self._graphql_request(query, variables)
        
        if data and 'user' in data and 'affectations' in data['user']:
            affectations = data['user']['affectations']
            
            # Filtrer uniquement les réservations actives
            active_bookings = [a for a in affectations if a.get('active', False)]
            
            if not active_bookings:
                return False
            
            # Si desk_id spécifié, vérifier si c'est le même bureau
            if desk_id:
                for booking in active_bookings:
                    if booking.get('desk', {}).get('id') == desk_id:
                        desk_name = booking.get('desk', {}).get('name', 'Bureau')
                        logger.info(f"ℹ️ Réservation déjà existante pour {desk_name} le {date_str}")
                        return True
                return False
            else:
                # Sinon, juste vérifier qu'il y a au moins une réservation
                desk_name = active_bookings[0].get('desk', {}).get('name', 'Bureau')
                logger.info(f"ℹ️ Réservation déjà existante pour {desk_name} le {date_str}")
                return True
        
        return False
    

