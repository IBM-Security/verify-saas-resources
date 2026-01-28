#!/usr/bin/env python3
"""
Bulk user deletion script for IBM Security Verify (SCIM).

Uses the same configuration and utilities as bulk_import.py,
but performs DELETE operations via SCIM Bulk API.

Behavior:
- Reads CSV (same format as import)
- Searches for each user by userName (preferred_username) or externalId
- Collects real SCIM IDs
- Sends bulk DELETE requests in batches
- Dry-run mode supported via app.yaml
"""

from __future__ import annotations

import csv, json, logging, sys
from pathlib import Path
from typing import List, Optional

from util.config_loader import Config
from util.logger import Logger
from util.access_token_util import AccessTokenUtil
from util.scim_client import ScimClient

logger = logging.getLogger(__name__)


class BulkDeleter:
    """Handles bulk deletion of users based on CSV input."""

    def __init__(self, config: Config, access_token: str):
        self.config = config
        self.client = ScimClient(
            base_url=config.scim_base_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/scim+json",
                "Accept": "application/scim+json",
            }
        )
        self.dry_run = config.data.get("delete", {}).get("dry_run", True)
        self.batch_size = config.batch_size

    def run(self) -> None:
        logger.info(f"Starting bulk deletion from CSV: {self.config.csv_file}")
        if self.dry_run:
            logger.warning("DRY-RUN MODE ENABLED → no actual deletions will occur")

        user_ids_to_delete = self._collect_user_ids()
        if not user_ids_to_delete:
            logger.info("No users found to delete.")
            return

        logger.info(f"Found {len(user_ids_to_delete)} users to delete")

        for start in range(0, len(user_ids_to_delete), self.batch_size):
            batch = user_ids_to_delete[start : start + self.batch_size]
            batch_nr = (start // self.batch_size) + 1

            logger.info(f"Processing deletion batch {batch_nr} ({len(batch)} users)")

            result = self._delete_batch(batch)
            self._log_batch_result(result, batch_nr)

        logger.info("Bulk deletion process completed.")

    def _collect_user_ids(self) -> List[str]:
        """Search for each user in CSV and collect real SCIM IDs."""
        found_ids = []
        skipped = 0

        with self.config.csv_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = row.get("preferred_username", "").strip()
                external_id = row.get("externalId", "").strip()

                if not username and not external_id:
                    skipped += 1
                    continue

                user_id = self.client.find_user_id(username=username, external_id=external_id)

                if user_id:
                    found_ids.append(user_id)
                    logger.debug(f"User found → {username} / {external_id} → ID: {user_id}")
                else:
                    skipped += 1
                    logger.warning(f"User not found → {username} / {external_id}")

        logger.info(f"Collected {len(found_ids)} user IDs to delete (skipped {skipped})")
        return found_ids

    def _delete_batch(self, user_ids: List[str]) -> dict:
        """Perform bulk DELETE via SCIM /Bulk endpoint."""
        operations = [
            {
                "method": "DELETE",
                "path": f"/Users/{uid}",
                "bulkId": f"del-{i+1:04d}"
            }
            for i, uid in enumerate(user_ids)
        ]

        payload = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": operations
        }

        if self.dry_run:
            logger.info(f"[DRY-RUN] Would send deletion batch with {len(operations)} operations")
            logger.debug(json.dumps(payload, indent=2))
            return {"dry_run": True, "operations_count": len(operations)}

        try:
            return self.client.send_bulk(payload)
        except Exception as exc:
            logger.exception("Bulk deletion batch failed")
            return {"error": str(exc)}

    def _log_batch_result(self, result: dict, batch_nr: int) -> None:
        if self.dry_run:
            return

        if "Operations" not in result:
            logger.error(f"Batch {batch_nr} - Invalid bulk response format")
            return

        successes = 0
        for op in result["Operations"]:
            status = int(op.get("status", 0))
            bulk_id = op.get("bulkId", "unknown")

            if 200 <= status < 300:
                successes += 1
            else:
                detail = op.get("response", {}).get("detail", "no detail")
                logger.warning(f"Batch {batch_nr} - {bulk_id} failed ({status}): {detail}")

        logger.info(f"Batch {batch_nr} complete: {successes}/{len(result['Operations'])} succeeded")


def main():
    try:
        config = Config()
        Logger(config)  # init logging
        token_util = AccessTokenUtil(config)
        token = token_util.get_access_token()

        deleter = BulkDeleter(config, token)
        deleter.run()

    except Exception as exc:
        if "logger" in locals():
            logger.exception("Fatal error in bulk deletion")
        else:
            logging.error("Fatal error before logger initialized", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()