import logging
from chordgen.abbreviation import Abbreviation, Option
from chordgen.config import Config
from chordgen.utils import find_combinations


class Scorer:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._keyboard = config.get_keyboard()

    def score(self, abbr: Abbreviation) -> Abbreviation:
        if abbr["reserved_combo"]:
            return abbr

        if len(abbr["word"]) < self.config.min_word_length:
            return abbr

        combinations = find_combinations(abbr["word"].lower())
        scores = [self._keyboard.score(combination) for combination in combinations]
        options: list[Option] = [
            {"combo": combination, "score": scores[i]}
            for i, combination in enumerate(combinations)
            if scores[i] != -1
        ]
        options = sorted(options, key=lambda x: x["score"])
        abbr["options"] = options
        logging.debug(f"Computed options for {abbr['word']}")
        return abbr
