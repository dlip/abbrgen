from pathlib import Path
from typing import Literal
import yaml
import shutil

from chordgen.keyboards.standard import StandardKeyboardOptions
from chordgen.keyboards import Keyboard
from chordgen.output.qmk import QmkOutput
from pydantic import BaseModel, field_serializer, field_validator

CONFIG_DIR = Path.home() / ".config" / "chordgen"
DEFAULT_CONFIG = CONFIG_DIR / "config.yaml"
DEFAULT_CHORDS_FILE = CONFIG_DIR / "chords.csv"


class OutputOptions(BaseModel):
    qmk: QmkOutput = QmkOutput()


class KeyboardOptions(BaseModel):
    standard: StandardKeyboardOptions = StandardKeyboardOptions()


class Config(BaseModel):
    keyboard: Literal[tuple(KeyboardOptions.model_fields.keys())] = "standard"
    keyboard_options: KeyboardOptions = KeyboardOptions()

    chords_file: Path = DEFAULT_CHORDS_FILE
    overwrite_alts: bool = False
    min_word_length: int = 3

    outputs: list[Literal[tuple(OutputOptions.model_fields.keys())]] = ["qmk"]
    output_options: OutputOptions = OutputOptions()

    _keyboard: Keyboard | None = None

    def get_keyboard(self):
        if not self._keyboard:
            self._keyboard = getattr(self.keyboard_options, self.keyboard).create()
        return self._keyboard

    @field_serializer("chords_file")
    def serialize_path(self, value: Path) -> str:
        try:
            return f"~/{value.relative_to(Path.home())}"
        except ValueError:
            return str(value)

    @field_validator("chords_file", mode="before")
    @classmethod
    def expand_user(cls, v):
        # Ensure "~" gets expanded if user provides it
        return Path(v).expanduser()

    @field_validator("chords_file", mode="after")
    @classmethod
    def ensure_parent_dir(cls, v: Path):
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("chords_file", mode="after")
    @classmethod
    def create_abbreviation_file(cls, v: Path):
        if not v.exists() and v == DEFAULT_CHORDS_FILE:
            here = Path(__file__).resolve().parent
            source = here / "assets" / "chords.csv"
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
