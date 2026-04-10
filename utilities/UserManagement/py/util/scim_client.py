# util/scim_client.py
"""
SCIM client for IBM Security Verify operations.
Supports bulk create/update/delete, user/group lookup.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, List, Optional, Union

import requests

logger = logging.getLogger(__name__)


class ScimClient:
    """Low-level SCIM client for IBM Verify."""

    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.bulk_endpoint = f"{self.base_url}/Bulk"

    def send_bulk(
        self,
        payload_or_operations: Union[Dict[str, Any], List[Dict[str, Any]]],
        /,
    ) -> Dict[str, Any]:
        """
        Send a SCIM Bulk request.
        Accepts either:
          - full payload dict (with "schemas" and "Operations")
          - or just the list of operations (legacy compatibility with bulk import)

        Logs a warning if the input type is unexpected, but continues processing.
        """
        if isinstance(payload_or_operations, list):
            # Legacy mode: caller passed only the operations list
            operations = payload_or_operations
            payload = {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                "Operations": operations
            }
        elif isinstance(payload_or_operations, dict):
            # Modern mode: caller passed full payload
            payload = payload_or_operations
            operations = payload.get("Operations", [])
        else:
            logger.warning(
                "send_bulk received unexpected type %s (expected dict or list). "
                "Attempting to proceed assuming list of operations.",
                type(payload_or_operations)
            )
            # Fallback: treat as list (best-effort)
            operations = payload_or_operations
            payload = {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                "Operations": operations
            }

        logger.info(f"Sending bulk request with {len(operations)} operations")
        logger.debug("Bulk payload:\n%s", json.dumps(payload, indent=2))

        try:
            resp = requests.post(
                self.bulk_endpoint,
                headers=self.headers,
                json=payload,
                timeout=180
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Bulk request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            raise

    def find_user_id(
        self,
        username: str = "",
        external_id: str = "",
        email: str = ""
    ) -> Optional[str]:
        """
        Lookup SCIM user ID by username, externalId or email.
        Returns the first matching ID or None.
        """
        filters = []
        if username:
            filters.append(f'userName eq "{username}"')
        if external_id:
            filters.append(f'externalId eq "{external_id}"')
        if email:
            filters.append(f'emails.value eq "{email}"')

        if not filters:
            logger.warning("No search criteria provided for user lookup")
            return None

        filter_expr = " or ".join(filters)
        params = {
            "filter": filter_expr,
            "attributes": "id,userName,externalId,emails.value",
            "count": 2   # expect at most 1, but ask for 2 to detect duplicates
        }

        try:
            resp = requests.get(
                f"{self.base_url}/Users",
                headers=self.headers,
                params=params,
                timeout=20
            )
            resp.raise_for_status()
            data = resp.json()
            resources = data.get("Resources", [])

            if len(resources) == 0:
                logger.debug(f"No user found for {username or external_id or email}")
                return None

            if len(resources) > 1:
                logger.warning(f"Multiple users match criteria: {username or external_id or email}")

            return resources[0]["id"]

        except requests.RequestException as e:
            logger.error(f"User lookup failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.debug(f"Response: {e.response.text}")
            return None

    def find_group_id(self, display_name: str) -> Optional[str]:
        """
        Lookup SCIM group ID by displayName.
        Returns the first matching ID or None.
        """
        params = {
            "filter": f'displayName eq "{display_name}"',
            "attributes": "id,displayName",
            "count": 2
        }

        try:
            resp = requests.get(
                f"{self.base_url}/Groups",
                headers=self.headers,
                params=params,
                timeout=20
            )
            resp.raise_for_status()
            data = resp.json()
            resources = data.get("Resources", [])

            if len(resources) == 0:
                logger.debug(f"Group not found: {display_name}")
                return None

            if len(resources) > 1:
                logger.warning(f"Multiple groups match name: {display_name}")

            return resources[0]["id"]

        except requests.RequestException as e:
            logger.error(f"Group lookup failed for '{display_name}': {e}")
            return None