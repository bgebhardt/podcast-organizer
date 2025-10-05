"""Configuration management for podcast organizer."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class AIConfig:
    """AI provider configuration."""
    provider: str = "claude"  # claude or openai
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    model: Optional[str] = None


@dataclass
class OutputConfig:
    """Output configuration."""
    default_file: str = "podcasts.md"


@dataclass
class FetchingConfig:
    """RSS fetching configuration."""
    timeout: int = 30
    max_concurrent: int = 10


@dataclass
class Config:
    """Main configuration object."""
    ai: AIConfig = field(default_factory=AIConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    fetching: FetchingConfig = field(default_factory=FetchingConfig)


def find_config_file() -> Optional[Path]:
    """
    Find config file in standard locations.

    Search order:
    1. .podcast-organizer.yaml in current directory
    2. ~/.podcast-organizer.yaml in home directory

    Returns:
        Path to config file if found, None otherwise
    """
    # Check current directory
    current_dir_config = Path(".podcast-organizer.yaml")
    if current_dir_config.exists():
        return current_dir_config

    # Check home directory
    home_config = Path.home() / ".podcast-organizer.yaml"
    if home_config.exists():
        return home_config

    return None


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file and environment variables.

    Args:
        config_path: Optional explicit config file path

    Returns:
        Config object with merged settings
    """
    config = Config()

    # Find config file if not explicitly provided
    if config_path is None:
        config_path = find_config_file()

    # Load from YAML file if found
    if config_path and config_path.exists():
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # AI configuration
        if 'ai' in data:
            ai_data = data['ai']
            config.ai.provider = ai_data.get('provider', config.ai.provider)
            config.ai.anthropic_api_key = ai_data.get('anthropic_api_key')
            config.ai.openai_api_key = ai_data.get('openai_api_key')
            config.ai.model = ai_data.get('model')

        # Output configuration
        if 'output' in data:
            output_data = data['output']
            config.output.default_file = output_data.get('default_file', config.output.default_file)

        # Fetching configuration
        if 'fetching' in data:
            fetching_data = data['fetching']
            config.fetching.timeout = fetching_data.get('timeout', config.fetching.timeout)
            config.fetching.max_concurrent = fetching_data.get('max_concurrent', config.fetching.max_concurrent)

    # Override with environment variables
    if os.getenv('ANTHROPIC_API_KEY'):
        config.ai.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    if os.getenv('OPENAI_API_KEY'):
        config.ai.openai_api_key = os.getenv('OPENAI_API_KEY')

    return config


def validate_config(config: Config, require_ai: bool = True) -> list[str]:
    """
    Validate configuration.

    Args:
        config: Config object to validate
        require_ai: Whether AI configuration is required

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if require_ai:
        provider = config.ai.provider.lower()

        if provider not in ['claude', 'openai']:
            errors.append(f"Invalid AI provider: {provider}. Must be 'claude' or 'openai'")

        if provider == 'claude' and not config.ai.anthropic_api_key:
            errors.append("Claude provider selected but no anthropic_api_key found in config or ANTHROPIC_API_KEY environment variable")

        if provider == 'openai' and not config.ai.openai_api_key:
            errors.append("OpenAI provider selected but no openai_api_key found in config or OPENAI_API_KEY environment variable")

    if config.fetching.timeout <= 0:
        errors.append(f"Invalid timeout: {config.fetching.timeout}. Must be positive")

    if config.fetching.max_concurrent <= 0:
        errors.append(f"Invalid max_concurrent: {config.fetching.max_concurrent}. Must be positive")

    return errors
