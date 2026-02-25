import logging
from abbrgen.abbreviation import Abbreviation, Option
from abbrgen.config import Config
from abbrgen.utils import find_combinations

from pattern import en


class AltGenerator:
    def __init__(self, config: Config) -> None:
        self.config = config

    def add_alt(self, abbr: Abbreviation) -> Abbreviation:
        word = abbr["word"]
        type = abbr["type"]
        if type == "VERB":
            if self.config.overwrite_alts or not abbr["alt1"]:
                abbr["alt1"] = en.conjugate(word, "3sg")
            if self.config.overwrite_alts or not abbr["alt2"]:
                abbr["alt2"] = en.conjugate(word, "1sgp")
            if self.config.overwrite_alts or not abbr["alt3"]:
                abbr["alt3"] = en.conjugate(word, "part")
        elif type == "NOUN":
            if self.config.overwrite_alts or not abbr["alt1"]:
                abbr["alt1"] = en.pluralize(word, pos=en.NOUN)
        return abbr
