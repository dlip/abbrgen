from typing import TypedDict


class Option(TypedDict):
    combo: str
    score: int


class Abbreviation(TypedDict):
    word: str
    combo: str
    type: str
    alt1: str
    alt2: str
    alt3: str
    options: list[Option] | None
