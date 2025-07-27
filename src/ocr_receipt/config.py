import os
import yaml
from typing import Any, Optional

class ConfigManager:
    """
    Manages application configuration using a YAML file with environment variable overrides.
    """
    def __init__(self, config_path: str = "config.yaml") -> None:
        """
        Initialize the ConfigManager and load configuration from a YAML file.
        :param config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """
        Load configuration from the YAML file.
        :return: Configuration dictionary.
        """
        default_config = {
            'database': {
                'path': 'ocr_receipts.db',
                'timeout': 30
            },
            'logging': {
                'level': 'INFO',
                'file': 'app.log'
            },
            'app': {
                'mode': 'development',
                'ocr_language': 'eng',
                'ui_language': 'en'
            },
            'gui': {
                'window_size': [1200, 800],
                'auto_save': True,
                'show_preview': True
            },
            'ocr': {
                'confidence_threshold': 0.6,
                'max_retries': 3
            },
            'file_naming': {
                'templates': {
                    'default': {
                        'name': 'Default Template',
                        'description': 'Standard template with project, date, company, and total',
                        'template': '{project}_{documentType}_{date}_{company}_{total}',
                        'active': True
                    }
                },
                'active_template': 'default',
                'date_format': '%Y-%m-%d',
                'include_invoice_number': True
            }
        }
        
        if not os.path.exists(self.config_path):
            # Create default config file
            self._config = default_config
            self.save()
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f) or {}
            
        # Merge with defaults to ensure all keys exist
        merged_config = self._merge_configs(default_config, loaded_config)
        return merged_config

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value, checking environment variables first.
        :param key: Configuration key (dot notation supported for nested keys).
        :param default: Default value if key is not found.
        :return: Configuration value.
        """
        env_key = key.upper().replace('.', '_')
        if env_key in os.environ:
            return os.environ[env_key]
        return self._get_nested(self._config, key.split('.'), default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value at runtime.
        :param key: Configuration key (dot notation supported for nested keys).
        :param value: Value to set.
        """
        self._set_nested(self._config, key.split('.'), value)

    def save(self) -> None:
        """
        Save the current configuration back to the YAML file.
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self._config, f)

    @staticmethod
    def _get_nested(config: dict, keys: list, default: Any) -> Any:
        d = config
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    @staticmethod
    def _set_nested(config: dict, keys: list, value: Any) -> None:
        d = config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    @staticmethod
    def _merge_configs(default: dict, loaded: dict) -> dict:
        """
        Merge loaded configuration with defaults, ensuring all default keys exist.
        """
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                result[key] = value
        return result 