import logging
from chordgen.chord import Chord
from chordgen.config import Config

from pattern import en


class AltGenerator:
    def __init__(self, config: Config) -> None:
        self.config = config

    def add_alt(self, chord: Chord) -> Chord:
        word = chord["word"]
        type = chord["type"]
        if self.config.overwrite_alts:
            chord["alt1"] = ""
            chord["alt2"] = ""
            chord["alt3"] = ""

        if type == "VERB":
            if not chord["alt1"]:
                chord["alt1"] = en.conjugate(word, "3sg")
            if not chord["alt2"]:
                chord["alt2"] = en.conjugate(word, "1sgp")
            if not chord["alt3"]:
                chord["alt3"] = en.conjugate(word, "part")
        elif type == "NOUN":
            if not chord["alt1"]:
                chord["alt1"] = en.pluralize(word, pos=en.NOUN)
        logging.debug(
            f"Alts for word {word}: {chord['alt1']}, {chord['alt2']}, {chord['alt3']}"
        )
        return chord
