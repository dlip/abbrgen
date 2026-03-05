from pathlib import Path
from chordgen.chord import Chord
from pydantic import BaseModel
from chordgen.pydantic import File


key_map = {
    " ": "spc",
    "←": "bspc",
}


class KanataOutput(BaseModel):
    file: File = Path.cwd() / "kanata_chords.kbd"
    combo_keys: list[str] = ["prtsc"]
    shift_keys: list[str] = ["ralt"]
    alt1_keys: list[str] = ["lalt"]
    alt2_keys: list[str] = ["spc"]
    alt3_keys: list[str] = ["lalt", "spc"]
    limit: int = 0
    combo_timeout: int = 100

    key_mapping: dict[str, str] = {
        "b": "tab",
        "y": "q",
        "o": "w",
        "u": "e",
        "c": "caps",
        "i": "a",
        "e": "s",
        "a": "d",
        "g": "lsft",
        "x": "z",
        "j": "x",
        "k": "c",
        "l": "i",
        "d": "o",
        "w": "p",
        "v": "[",
        "h": "k",
        "t": "l",
        "s": ";",
        "n": "'",
        "r": ",",
        "m": ".",
        "f": "/",
        "p": "rsft",
        " ": "spc",
    }

    def output(self, chords: list[Chord]):
        output = "(defchordsv2-experimental\n"

        def translate_macro(word):
            result = []
            for k in word:
                if k in key_map:
                    result.append(key_map[k])
                elif k.isupper():
                    result.append("S-" + k.lower())
                else:
                    result.append(k)
            return result

        def translate_combo(abbr):
            result = []
            for i, k in enumerate(abbr):
                if k in self.key_mapping:
                    result.append(self.key_mapping[k])
                else:
                    raise Exception(f"No key_map for {k}")
            return result

        alt_keys = [self.alt1_keys, self.alt2_keys, self.alt3_keys]
        count = 0
        for chord in chords:
            c = chord["chord"]
            if not c:
                continue

            count += 1
            if self.limit != 0 and count > self.limit:
                print(f"Stopping at line {self.limit} due to limit setting")
                break

            words = [chord["word"], chord["alt1"], chord["alt2"], chord["alt3"]]
            for i, word in enumerate(words):
                if not word:
                    continue
                alt = []
                if i > 0:
                    alt = alt_keys[i - 1]

                chord = translate_combo(c)
                macro = translate_macro(word + " ")

                output += f"  ({' '.join(self.combo_keys + alt)} {' '.join(chord)}) (macro {' '.join(macro)}) {self.combo_timeout} first-release ()\n"
                shifted_macro = translate_macro(word.capitalize() + " ")
                output += f"  ({' '.join(self.combo_keys + alt + self.shift_keys)} {' '.join(chord)}) (macro {' '.join(shifted_macro)}) {self.combo_timeout} first-release ()\n"

        output += ")"

        print(f"Writing {self.file}")
        with open(self.file, "w") as file:
            file.write(output)
