import csv, logging, sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from util.logger import Logger
from util.access_token_util import AccessTokenUtil
from util.config_loader import Config
from util.scim_client import ScimClient
from util.user_mapper import UserMapper

logger = logging.getLogger(__name__)


class BulkImporter:
    """
    Orchestrates reading users from CSV, mapping them to SCIM format,
    batching, and sending bulk create requests via SCIM /Bulk endpoint.
    """

    def __init__(self, config: 'Config', access_token: str):
        """
        Args:
            config: Loaded configuration object
            access_token: Valid OAuth2 bearer token with manageUsers scope/entitlement
        """
        self.config = config
        # self.mapper = UserMapper(config.reg_status_urn)
        self.mapper = UserMapper(
            attribute_rules=config.attribute_rules   # ← pass the rules from config
        )

        self.client = ScimClient(
            base_url=config.scim_base_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/scim+json",
                "Accept": "application/scim+json",
            }
        )

    def run(self) -> None:
        """Main execution flow: read → map → batch → send → log results."""
        logger.info(f"Starting bulk import from {self.config.csv_file}")

        users = self._read_and_map_users()
        if not users:
            logger.warning("No valid users found in CSV. Nothing to import.")
            return

        logger.info(f"Prepared {len(users)} valid users for import")

        total_success = 0
        total_failed = 0

        for batch_start in range(0, len(users), self.config.batch_size):
            batch_end = min(batch_start + self.config.batch_size, len(users))
            batch_users = users[batch_start:batch_end]
            batch_number = (batch_start // self.config.batch_size) + 1

            logger.info(
                f"Processing batch {batch_number} "
                f"({len(batch_users)} users, {batch_start+1}–{batch_end})"
            )

            operations = self._create_operations(batch_users)

            try:
                result = self.client.send_bulk(operations)
                successes, failures = self._log_batch_result(result, batch_number)
                total_success += successes
                total_failed += failures
            except Exception as exc:
                logger.exception(f"Batch {batch_number} failed completely")
                total_failed += len(batch_users)

        logger.info(
            f"Bulk import finished. "
            f"Total succeeded: {total_success} / {len(users)} "
            f"({total_failed} failed)"
        )

    def _read_and_map_users(self) -> List[Dict[str, Any]]:
        """Read CSV and convert each valid row to SCIM user object."""
        users = []
        csv_path = self.config.csv_file

        if not csv_path.is_file():
            logger.error(f"CSV file not found: {csv_path}")
            return users

        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                scim_user = self.mapper.map_row_to_scim_user(row)
                if scim_user:
                    users.append(scim_user)
                else:
                    logger.debug("Skipped invalid/empty row")

        return users

    def _create_operations(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate SCIM Bulk operations (POST /Users) for the given users."""
        return [
            {
                "method": "POST",
                "path": "/Users",
                "bulkId": f"create-user-{i+1:04d}",
                "data": user
            }
            for i, user in enumerate(users, start=1)
        ]

    def _log_batch_result(self, result: Dict[str, Any], batch_number: int) -> tuple[int, int]:
        """
        Parse bulk response and log per-operation outcome.
        Returns (success_count, failure_count) for this batch.
        """
        if "Operations" not in result:
            logger.error(f"Batch {batch_number} - Invalid bulk response format")
            return 0, len(result.get("Operations", []))

        successes = 0
        failures = 0

        for op in result["Operations"]:
            bulk_id = op.get("bulkId", "unknown")

            # Safely convert status (IBM Verify returns it as string)
            status_str = op.get("status")
            try:
                status = int(status_str) if status_str is not None else 0
            except (ValueError, TypeError):
                logger.warning(f"Batch {batch_number} - invalid status value: {status_str!r} "
                               f"(bulkId={bulk_id})")
                status = 0

            if 200 <= status < 300:
                successes += 1
                # Optional: logger.debug(f"bulkId={bulk_id} → success ({status})")
            else:
                failures += 1
                detail = op.get("response", {}).get("detail", "no detail provided")
                scim_type = op.get("response", {}).get("scimType", "")
                logger.warning(
                    f"Batch {batch_number} - bulkId={bulk_id} failed "
                    f"({status}) {scim_type}: {detail}"
                )

        logger.info(f"Batch {batch_number} summary: {successes} succeeded, {failures} failed")
        return successes, failures

def main():
    try:
        config = Config()
        logger = Logger(config)
        token_util = AccessTokenUtil(config)
        access_token = token_util.get_access_token()

        importer = BulkImporter(config, access_token)
        importer.run()
    except Exception as exc:
        if 'logger' in locals():
            logger.exception("Fatal error during bulk import")
        else:
            logging.error("Fatal error before logger initialized", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
