import logging
from chordgen.abbreviation import Chord, Option
from chordgen.config import Config
from chordgen.utils import find_combinations


class Scorer:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._keyboard = config.get_keyboard()

    def score(self, chord: Chord) -> Chord:
        if chord["reserved_chord"]:
            return chord

        if len(chord["word"]) < self.config.min_word_length:
            return chord

        combinations = find_combinations(chord["word"].lower())
        scores = [self._keyboard.score(combination) for combination in combinations]
        options: list[Option] = [
            {"chord": combination, "score": scores[i]}
            for i, combination in enumerate(combinations)
            if scores[i] != -1
        ]
        options = sorted(options, key=lambda x: x["score"])
        chord["options"] = options
        logging.debug(f"Computed options for {chord['word']}")
        return chord
