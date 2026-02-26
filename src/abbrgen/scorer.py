import logging
from abbrgen.abbreviation import Abbreviation, Option
from abbrgen.config import Config
from abbrgen.utils import find_combinations


class Scorer:
    def __init__(self, config: Config) -> None:
        self.config = config

    def score(self, abbr: Abbreviation) -> Abbreviation:
        if not self.config.overwrite_abbreviations and abbr["combo"]:
            return abbr

        abbr["combo"] = ""

        if len(abbr["word"]) < self.config.min_word_length:
            return abbr

        combinations = find_combinations(abbr["word"].lower())
        scores = [
            self.config.keyboard.score(combination) for combination in combinations
        ]
        options: list[Option] = [
            {"combo": combination, "score": scores[i]}
            for i, combination in enumerate(combinations)
            if scores[i] != -1
        ]
        options = sorted(options, key=lambda x: x["score"])
        abbr["options"] = options
        logging.debug(f"Computed options for {abbr['word']}")
        return abbr
