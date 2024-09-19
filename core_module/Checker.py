import datetime
import math
import random
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Set
from abc import ABC, abstractmethod

class Checker:
    def __init__(self, reference_structure: Dict[str, Any]):
        self.reference = reference_structure["metadata_schema"]

    def check_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        self._check_dict(metadata, self.reference, "", errors)
        if errors:
            return False, errors
        return True, ["Validation passed"]

    def _check_dict(self, data: Dict[str, Any], schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        for key, value_schema in schema.items():
            new_path = f"{path}.{key}" if path else key
            if key == "*":
                for sub_key, sub_value in data.items():
                    self._check_value(sub_value, value_schema, f"{path}.{sub_key}", errors)
            elif key in data:
                self._check_value(data[key], value_schema, new_path, errors)
            elif value_schema.get("required", False):
                errors.append(f"Missing required field: {new_path}")
        
        # Check for extra keys
        for key in data:
            if key not in schema and "*" not in schema:
                errors.append(f"Unexpected field: {path}.{key}")

    def _check_value(self, value: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        if "type" not in schema:
            errors.append(f"Invalid schema for {path}: missing 'type'")
            return

        if not self._check_type(value, schema["type"]):
            errors.append(f"Invalid type for {path}: expected {schema['type']}, got {type(value).__name__}")
            return

        if schema["type"] == "dict" and "schema" in schema:
            if not isinstance(value, dict):
                errors.append(f"Expected dict for {path}, got {type(value).__name__}")
            else:
                self._check_dict(value, schema["schema"], path, errors)

    def _check_type(self, value: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "list":
            return isinstance(value, list)
        elif expected_type == "dict":
            return isinstance(value, dict)
        elif expected_type == "tuple":
            return isinstance(value, tuple) and len(value) == 2
        elif expected_type == "boolean":
            return isinstance(value, bool)
        return False

