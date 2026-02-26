from pathlib import Path
from typing import TypedDict
import csv


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


def load_abbreviation_file(abbreviation_file: Path) -> list[Abbreviation]:
    with open(abbreviation_file) as f:
        reader = csv.DictReader(f)
        abbrs: list[Abbreviation] = [line for line in reader]
        return abbrs


def validate_combos(abbrs: list[Abbreviation]):
    used = {}

    for abbr in abbrs:
        combo = abbr["combo"]
        if combo:
            sorted_combo = "".join(sorted(combo))
            if sorted_combo in used:
                raise Exception(
                    f"Error: combo '{combo}' for word {abbr['word']} already used by {used[sorted_combo]}"
                )

            used[sorted_combo] = abbr["word"]
