"""
Configuration loader for the voting system.
Loads configuration from JSON files and environment variables.
"""

import json
import os
from typing import Dict, Any, Tuple
from pathlib import Path


class ConfigLoader:
    """Loads and parses configuration from JSON files and env vars."""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file

    def load(self) -> Tuple[bool, Dict[str, Any]]:
        default_config = self.get_default_config()

        file_success, file_config = self.load_from_file(self.config_file)
        if not file_success:
            file_config = {}

        env_config = self.load_from_env()
        merged = self.merge_configs(default_config, file_config)
        merged = self.merge_configs(merged, env_config)

        valid, error = self.validate_config(merged)
        if not valid:
            return False, {"error": error}

        return True, merged

    def load_from_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        path = Path(file_path)

        if not path.exists():
            return False, {}

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return False, {}

            return True, data

        except (json.JSONDecodeError, OSError):
            return False, {}

    def load_from_env(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {}

        def set_nested(section: str, key: str, value: Any) -> None:
            config.setdefault(section, {})[key] = value

        if os.getenv("SERVER_HOST"):
            set_nested("server", "host", os.getenv("SERVER_HOST"))

        if os.getenv("SERVER_PORT"):
            set_nested("server", "port", int(os.getenv("SERVER_PORT")))

        if os.getenv("DB_HOST"):
            set_nested("database", "host", os.getenv("DB_HOST"))

        if os.getenv("DB_PORT"):
            set_nested("database", "port", int(os.getenv("DB_PORT")))

        if os.getenv("DB_NAME"):
            set_nested("database", "database", os.getenv("DB_NAME"))

        if os.getenv("DB_USER"):
            set_nested("database", "user", os.getenv("DB_USER"))

        if os.getenv("DB_PASSWORD"):
            set_nested("database", "password", os.getenv("DB_PASSWORD"))

        if os.getenv("BLOCKCHAIN_DIFFICULTY"):
            set_nested("blockchain", "difficulty", int(os.getenv("BLOCKCHAIN_DIFFICULTY")))

        if os.getenv("BLOCKCHAIN_BLOCK_SIZE"):
            set_nested("blockchain", "block_size", int(os.getenv("BLOCKCHAIN_BLOCK_SIZE")))

        if os.getenv("LOG_LEVEL"):
            set_nested("logging", "level", os.getenv("LOG_LEVEL"))

        return config

    def merge_configs(self, file_config: Dict, env_config: Dict) -> Dict:
        merged = dict(file_config)

        for key, value in env_config.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        required_sections = ["server", "database", "blockchain", "voting", "logging"]

        for section in required_sections:
            if section not in config:
                return False, f"Missing config section: {section}"

        if not isinstance(config["server"].get("port"), int):
            return False, "Server port must be an integer"

        if not 1 <= config["server"]["port"] <= 65535:
            return False, "Server port must be between 1 and 65535"

        if not isinstance(config["database"].get("port"), int):
            return False, "Database port must be an integer"

        if not 1 <= config["database"]["port"] <= 65535:
            return False, "Database port must be between 1 and 65535"

        if int(config["blockchain"].get("difficulty", 0)) < 0:
            return False, "Blockchain difficulty must be non-negative"

        if int(config["blockchain"].get("block_size", 0)) <= 0:
            return False, "Blockchain block size must be positive"

        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = str(config["logging"].get("level", "INFO")).upper()

        if level not in valid_levels:
            return False, "Invalid logging level"

        config["logging"]["level"] = level

        return True, ""

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 5000,
                "timeout": 30
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "voting_system",
                "user": "postgres",
                "password": "postgres"
            },
            "blockchain": {
                "difficulty": 4,
                "mining_reward": 1,
                "block_size": 100
            },
            "voting": {
                "enable_anonymous": True,
                "require_registration": True,
                "voting_duration_hours": 24
            },
            "logging": {
                "level": "INFO",
                "file": "logs/voting_system.log"
            }
        }

    @staticmethod
    def get_server_config(config: Dict) -> Dict[str, Any]:
        return config.get("server", {})

    @staticmethod
    def get_database_config(config: Dict) -> Dict[str, Any]:
        return config.get("database", {})

    @staticmethod
    def get_blockchain_config(config: Dict) -> Dict[str, Any]:
        return config.get("blockchain", {})

    @staticmethod
    def get_logging_config(config: Dict) -> Dict[str, Any]:
        return config.get("logging", {})