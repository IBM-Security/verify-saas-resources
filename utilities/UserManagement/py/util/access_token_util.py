from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import requests

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .config_loader import Config


class AccessTokenUtil:
    """Handles OAuth2 client credentials flow for access tokens."""

    def __init__(self, config: 'Config'):
        self.token_url = config.token_url
        self.client_id = config.client_id
        self.client_secret = config.client_secret

    def get_access_token(self) -> str:
        logger.info(f"Fetching access token from {self.token_url}...")
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            resp = requests.post(self.token_url, data=data, headers=headers, timeout=30)
            resp.raise_for_status()
            token_data = resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("No access_token in response")
            logger.info("Access token fetched successfully")
            return access_token
        except requests.RequestException as e:
            logger.error(f"Failed to fetch access token: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise