import aiocron
import json
import jwt
import requests

from jwt import algorithms,InvalidTokenError

from .config import config
from .core import Service
from .decorators import with_logger
from .exceptions import AuthenticationError


@with_logger
class OAuthService(Service):
    """
        Service for managing the OAuth token logins and verification.
    """

    def __init__(self):
        self.public_keys = None

    async def initialize(self) -> None:
        await self.retrieve_public_keys()
        # crontab: min hour day month day_of_week
        # Run every Wednesday because GeoLite2 is updated every first Tuesday
        # of the month.
        self._update_cron = aiocron.crontab(
            "0 0 * * *", func=self.retrieve_public_keys()
        )

    async def retrieve_public_keys(self) -> None:
        """
            Get the latest jwks from the hydra endpoint
        """
        self.public_keys = {}
        jwks = requests.get(config.HYDRA_JWKS_URI).json()
        for jwk in jwks['keys']:
            kid = jwk['kid']
            self.public_keys[kid] = algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    async def get_player_id_from_token(self, token: str) -> int:
        """
            Decode the JWT
        """
        try:
            kid = jwt.get_unverified_header(token)['kid']
            key = self.public_keys[kid]
            return jwt.decode(token, key=key, algorithms="RS256")["user_id"]
        except (InvalidTokenError, KeyError):
            raise AuthenticationError("Token signature was invalid")
