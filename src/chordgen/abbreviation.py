from pathlib import Path
from typing import TypedDict
import csv


class Option(TypedDict):
    chord: str
    score: int


class Chord(TypedDict):
    word: str
    chord: str
    reserved_chord: str
    type: str
    alt1: str
    alt2: str
    alt3: str
    options: list[Option] | None


def load_chords_file(file: Path) -> list[Chord]:
    with open(file) as f:
        reader = csv.DictReader(f)
        abbrs: list[Chord] = [line for line in reader]
        return abbrs


def validate_chords(abbrs: list[Chord]):
    used = {}

    for abbr in abbrs:
        chord = abbr["chord"]
        if chord:
            sorted_chord = "".join(sorted(chord))
            if sorted_chord in used:
                raise Exception(
                    f"Error: chord '{chord}' for word {abbr['word']} already used by {used[sorted_chord]}"
                )

            used[sorted_chord] = abbr["word"]
