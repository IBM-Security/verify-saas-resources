# util/attribute_applicator.py
"""
Handles configurable application of SCIM attributes (core + custom extensions)
based on rules defined in app.yaml.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AttributeApplicator:
    """
    Applies a list of attribute rules to a SCIM payload.
    Supports:
    - core attributes (active, userName, etc.)
    - custom attributes in extension objects (simple or nested customAttributes array)
    - static values or values from CSV row
    """

    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Args:
            rules: List of attribute rule dictionaries from config
                   Example:
                   [
                       {"name": "active", "value": true, "type": "static"},
                       {"name": "registrationstatus", "value": "completed", "type": "static",
                        "extension_urn": "...", "custom_container": "customAttributes", ...}
                   ]
        """
        self.rules = rules or []

    def apply_to(self, payload: Dict[str, Any], row: Dict[str, str]) -> None:
        """
        Modify the payload in-place by applying all configured rules.
        """
        for rule in self.rules:
            attr_name = rule.get("name")
            if not attr_name:
                logger.warning("Rule missing 'name' field → skipped")
                continue

            value = self._resolve_value(rule, row)
            if value is None:
                continue  # no value to apply

            urn = rule.get("extension_urn")
            if urn:
                self._apply_extension_attribute(payload, urn, attr_name, value, rule)
            else:
                self._apply_core_attribute(payload, attr_name, value)

    def _resolve_value(self, rule: Dict[str, Any], row: Dict[str, str]) -> Optional[Any]:
        value_type = rule.get("type", "static")

        if value_type == "static":
            return rule.get("value")

        elif value_type == "from_csv":
            csv_col = rule.get("csv_column")
            if not csv_col:
                logger.warning(f"Rule for {rule.get('name')} has type 'from_csv' but no csv_column")
                return None
            return row.get(csv_col)

        else:
            logger.warning(f"Unknown attribute rule type '{value_type}' for {rule.get('name')}")
            return None

    def _apply_core_attribute(self, payload: Dict[str, Any], name: str, value: Any) -> None:
        """Set a standard SCIM core attribute directly on the root payload."""
        if value is not None:
            payload[name] = value
            logger.debug(f"Applied core attribute: {name} = {value}")

    def _apply_extension_attribute(
        self,
        payload: Dict[str, Any],
        urn: str,
        name: str,
        value: Any,
        rule: Dict[str, Any]
    ) -> None:
        """Apply attribute inside an extension object (simple or nested in customAttributes)."""
        if urn not in payload:
            payload[urn] = {}

        target = payload[urn]

        container = rule.get("custom_container")  # e.g. "customAttributes"
        if container:
            if container not in target:
                target[container] = []

            name_key = rule.get("custom_name_key", "name")
            value_key = rule.get("custom_value_key", "values")

            # Look for existing entry with matching name
            found = False
            for item in target[container]:
                if item.get(name_key) == name:
                    item[value_key] = [value] if not isinstance(value, list) else value
                    found = True
                    break

            if not found:
                new_item = {name_key: name, value_key: [value] if not isinstance(value, list) else value}
                target[container].append(new_item)

            logger.debug(f"Applied extension attribute: {urn}:{container}:{name} = {value}")