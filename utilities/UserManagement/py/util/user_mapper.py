# util/user_mapper.py
"""
Mapper from CSV row to SCIM User payload for IBM Security Verify.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from .attribute_applicator import AttributeApplicator

logger = logging.getLogger(__name__)


class UserMapper:
    """Converts CSV row data into a valid SCIM User creation payload."""

    def __init__(self, attribute_rules: list[dict]):
        """
        Args:
            attribute_rules: List of attribute rule dicts from config
        """
        self.applicator = AttributeApplicator(attribute_rules)

    def map_row_to_scim_user(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Maps a CSV row to a SCIM User object.
        Returns None if the row is invalid (no username or email).
        """
        username = row.get("preferred_username", "").strip()
        if not username:
            logger.debug("Skipping row: missing preferred_username")
            return None

        email_value = row.get("email", "").strip()
        if not email_value:
            logger.warning(f"Skipping user '{username}': missing email")
            return None

        # Start with minimal core payload
        payload: Dict[str, Any] = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:extension:ibm:2.0:User"   
                # Extension schemas are added automatically by applicator if needed
            ],
            "userName": username,
            "externalId": row.get("externalId", username),
            "name": {
                "givenName": row.get("given_name", "").strip() or None,
                "familyName": row.get("family_name", "").strip() or None,
            },
            "emails": [
                {
                    "value": email_value,
                    "primary": True,
                    "type": "work"          # or "other" — adjust if needed
                }
            ],
        }

        # Optional password
        password = row.get("password", "").strip()
        if password:
            payload["password"] = password

        # Clean up name
        name_dict = payload["name"]
        name_dict = {k: v for k, v in name_dict.items() if v and v.strip()}
        if name_dict:
            payload["name"] = name_dict
        else:
            payload.pop("name", None)

        # 1. Apply all configurable rules from app.yaml first
        self.applicator.apply_to(payload, row)

        # 2. Then apply hard-coded tenant-specific defaults / fallbacks
        #    (this ensures registrationstatus is always set, even if not in rules)
        ibm_urn = "urn:ietf:params:scim:schemas:extension:ibm:2.0:User"
        if ibm_urn not in payload:
            payload[ibm_urn] = {}

        custom_attrs = payload[ibm_urn].get("customAttributes", [])

        # Optional debug
        # logger.debug("Final payload:\n%s", json.dumps(payload, indent=2))

        return payload