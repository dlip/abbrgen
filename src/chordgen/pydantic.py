from pathlib import Path
from typing import Annotated
from pydantic import BeforeValidator, PlainSerializer


def serialize_path(value: Path) -> str:
    try:
        return f"~/{value.relative_to(Path.home())}"
    except ValueError:
        return str(value)


def expand_user(v):
    # Ensure "~" gets expanded if user provides it
    return Path(v).expanduser()


File = Annotated[
    Path, BeforeValidator(expand_user), PlainSerializer(serialize_path, return_type=str)
]
