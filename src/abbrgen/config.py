from datetime import datetime

from pathlib import Path
import yaml

from pydantic import BaseModel, Field
from .keyboards.standard import StandardKeyboard


class Config(BaseModel):
    keyboard: StandardKeyboard = Field(
        discriminator="type",
        default_factory=lambda: StandardKeyboard(),
    )


def load_or_create_config() -> Config:
    config_dir = Path.home() / ".abbrgen"
    config_path = config_dir / "config.yaml"
    config_dir.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text()) or {}
    else:
        raw = {}
        # write defaults immediately
        default_config = Config()
        config_path.write_text(yaml.safe_dump(default_config.model_dump()))
        return default_config

    # Validate + apply defaults
    config = Config.model_validate(raw)

    # Optionally rewrite file if missing fields were added
    config_path.write_text(yaml.safe_dump(config.model_dump()))

    return config
