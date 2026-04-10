from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

import yaml
from yaml import SafeLoader


class Config:
    """Loads and provides access to configuration from app.yaml."""

    def __init__(self, config_path: str | Path = "conf/application.yaml"):
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = self._load_yaml()

        # Tenant & API
        self.tenant_base_url: str = self.data["tenant"]["base_url"].rstrip("/")
        self.scim_base_url: str = f"{self.tenant_base_url}{self.data['tenant']['scim_path']}"
        self.token_url: str = f"{self.tenant_base_url}{self.data['auth']['token_path']}"
        self.client_id: str = self.data["auth"]["client_id"]
        self.client_secret: str = self.data["auth"]["client_secret"]

        # Import settings
        self.csv_file: Path = Path(self.data["import"]["csv_file"])
        self.batch_size: int = self.data["import"]["batch_size"]
        # self.reg_status_urn: str = self.data["import"]["registration_status_urn"]

        # Attribute rules
        self.attribute_rules: list[dict] = self.data.get("import", {}).get("attribute_rules", [])

        # Logging settings
        self.logging_cfg = self.data.get("logging", {})

    def _load_yaml(self) -> Dict[str, Any]:
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with self.config_path.open("r", encoding="utf-8") as f:
            return yaml.load(f, Loader=SafeLoader)