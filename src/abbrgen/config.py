from pathlib import Path
from typing import Literal
import yaml
import shutil

from abbrgen.generators.qmk import QmkGenerator
from pydantic import BaseModel, Field, field_serializer, field_validator
from .keyboards import Keyboard

CONFIG_DIR = Path.home() / ".config" / "abbrgen"
DEFAULT_CONFIG = CONFIG_DIR / "config.yaml"
DEFAULT_ABBREVIATION_FILE = CONFIG_DIR / "abbreviations.csv"


class Generators(BaseModel):
    qmk: QmkGenerator = QmkGenerator()


class Config(BaseModel):
    keyboard: Keyboard = Field(
        discriminator="type",
        default_factory=lambda: StandardKeyboard(),
    )
    abbreviation_file: Path = DEFAULT_ABBREVIATION_FILE
    overwrite_abbreviations: bool = False
    overwrite_alts: bool = False
    min_word_length: int = 3

    generators: list[Literal[tuple(Generators.model_fields.keys())]] = ["qmk"]
    generator_options: Generators = Generators()

    @field_serializer("abbreviation_file")
    def serialize_path(self, value: Path) -> str:
        try:
            return f"~/{value.relative_to(Path.home())}"
        except ValueError:
            return str(value)

    @field_validator("abbreviation_file", mode="before")
    @classmethod
    def expand_user(cls, v):
        # Ensure "~" gets expanded if user provides it
        return Path(v).expanduser()

    @field_validator("abbreviation_file", mode="after")
    @classmethod
    def ensure_parent_dir(cls, v: Path):
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("abbreviation_file", mode="after")
    @classmethod
    def create_abbreviation_file(cls, v: Path):
        if not v.exists() and v == DEFAULT_ABBREVIATION_FILE:
            here = Path(__file__).resolve().parent
            source = here / "assets" / "abbreviations.csv"
            shutil.copyfile(source, v)
        return v


def load_or_create_config(config_file: Path = DEFAULT_CONFIG) -> Config:
    if config_file != DEFAULT_CONFIG and not config_file.exists():
        raise Exception(f"Config file does not exist: {config_file}")

    config_file.parent.mkdir(parents=True, exist_ok=True)

    if config_file.exists():
        raw = yaml.safe_load(config_file.read_text()) or {}
    else:
        print(f"Creating config {config_file}")
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
