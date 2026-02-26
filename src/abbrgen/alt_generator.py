import logging
from abbrgen.abbreviation import Abbreviation
from abbrgen.config import Config

from pattern import en


class AltGenerator:
    def __init__(self, config: Config) -> None:
        self.config = config

    def add_alt(self, abbr: Abbreviation) -> Abbreviation:
        word = abbr["word"]
        type = abbr["type"]
        if self.config.overwrite_alts:
            abbr["alt1"] = ""
            abbr["alt2"] = ""
            abbr["alt3"] = ""

        if type == "VERB":
            if not abbr["alt1"]:
                abbr["alt1"] = en.conjugate(word, "3sg")
            if not abbr["alt2"]:
                abbr["alt2"] = en.conjugate(word, "1sgp")
            if not abbr["alt3"]:
                abbr["alt3"] = en.conjugate(word, "part")
        elif type == "NOUN":
            if not abbr["alt1"]:
                abbr["alt1"] = en.pluralize(word, pos=en.NOUN)
        logging.debug(
            f"Alts for word {word}: {abbr['alt1']}, {abbr['alt2']}, {abbr['alt3']}"
        )
        return abbr
