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
                logger.info("🔄 Refresh token disponible pour renouvellement automatique")
    
    def _graphql_request(self, query: str, variables: Optional[Dict] = None, retry_on_auth_error: bool = True) -> Optional[Dict]:
        """
        Exécute une requête GraphQL avec rafraîchissement automatique du token
        
        Args:
            query: Requête GraphQL
            variables: Variables de la requête
            retry_on_auth_error: Réessayer après rafraîchissement du token si erreur 401
            
        Returns:
            Données de la réponse ou None en cas d'erreur
        """
        try:
            payload = {'query': query}
            if variables:
                payload['variables'] = variables
            
            response = self.session.post(self.GQL_ENDPOINT, json=payload)
            
            # Si erreur 401 et qu'on a un refresh_token, essayer de rafraîchir
            if response.status_code == 401 and retry_on_auth_error and self.refresh_token:
                logger.warning("⚠️ Token expiré, tentative de rafraîchissement...")
                if self.refresh_access_token():
                    # Réessayer la requête avec le nouveau token
                    return self._graphql_request(query, variables, retry_on_auth_error=False)
                else:
                    logger.error("❌ Impossible de rafraîchir le token")
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
    
    def refresh_access_token(self) -> bool:
        """
        Rafraîchit le token d'accès en utilisant le refresh_token
        
        Returns:
            bool: True si le rafraîchissement est réussi
        """
        if not self.refresh_token:
            logger.error("❌ Aucun refresh token disponible")
            return False
        
        try:
            # Endpoint pour rafraîchir le token
            response = self.session.post(
                f"{self.BASE_URL}/auth/refresh",
                json={'refresh_token': self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                
                if new_token:
                    self.token = new_token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    
                    # Mettre à jour le fichier .env avec le nouveau token
                    self._update_env_token(new_token)
                    
                    logger.info("✅ Token rafraîchi avec succès")
                    return True
            
            logger.error(f"❌ Échec du rafraîchissement: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            
            # Alerter si le refresh token ne fonctionne plus
            if notification_service:
                error_msg = f"Impossible de rafraîchir le token (HTTP {response.status_code})"
                notification_service.send_token_expired_alert(error_msg)
            
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur lors du rafraîchissement: {e}")
            if notification_service:
                notification_service.send_token_expired_alert(str(e))
            return False
    
    def _update_env_token(self, new_token: str):
        """
        Met à jour le token dans le fichier .env
        
        Args:
            new_token: Le nouveau token d'accès
        """
        try:
            import os
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            
            if not os.path.exists(env_path):
                return
            
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('ONEFLEX_TOKEN='):
                        f.write(f'ONEFLEX_TOKEN={new_token}\n')
                    else:
                        f.write(line)
            
            logger.info("📝 Fichier .env mis à jour avec le nouveau token")
            
        except Exception as e:
            logger.warning(f"⚠️ Impossible de mettre à jour .env: {e}")
        
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
            bool: True si la réservation est réussie
        """
        user_id = self.get_my_user_id()
        if not user_id:
            logger.error("❌ Impossible de récupérer l'ID utilisateur")
            return False
        
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
            return True
        
        logger.error(f"❌ Échec de la réservation")
        return False
    
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
    

