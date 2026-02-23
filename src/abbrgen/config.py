from datetime import datetime

from pathlib import Path
import yaml

from pydantic import BaseModel, Field
from .keyboards.standard import StandardKeyboard

DEFAULT_CONFIG = Path.home() / ".abbrgen" / "config.yaml"


class Config(BaseModel):
    keyboard: StandardKeyboard = Field(
        discriminator="type",
        default_factory=lambda: StandardKeyboard(),
    )


def load_or_create_config(config_file: Path = DEFAULT_CONFIG) -> Config:
    if config_file != DEFAULT_CONFIG and not config_file.exists():
        raise Exception(f"Config file does not exist: {config_file}")

    config_file.parent.mkdir(parents=True, exist_ok=True)

    if config_file.exists():
        raw = yaml.safe_load(config_file.read_text()) or {}
    else:
        raw = {}
        # write defaults immediately
        default_config = Config()
        config_file.write_text(yaml.safe_dump(default_config.model_dump()))
        return default_config

    # Validate + apply defaults
    config = Config.model_validate(raw)

    # Optionally rewrite file if missing fields were added
    config_file.write_text(yaml.safe_dump(config.model_dump()))

    return config
