from pathlib import Path
from chordgen.chord import Chord
from pydantic import BaseModel
from chordgen.pydantic import File

trigger_keys = ["COMBO"]
shifted_keys = ["COMBO_SFT"]
alt_keys = [["COMBO_ALT1"], ["COMBO_ALT2"], ["COMBO_ALT1", "COMBO_ALT2"]]

key_map = {
    "'": "QUOT",
    ";": "SEMI",
    ",": "COMMA",
    ".": "DOT",
    " ": "SPC",
    "@": "AT",
    "?": "QUESTION",
    "←": "BSPC",
}


class ZmkOutput(BaseModel):
    chords_file: File = Path.cwd() / "zmk_chords.def"
    macros_file: File = Path.cwd() / "zmk_macros.def"
    combo_keys: list[str] = ["COMBO"]
    shift_keys: list[str] = ["COMBO_SFT"]
    alt1_keys: list[str] = ["COMBO_ALT1"]
    alt2_keys: list[str] = ["COMBO_ALT2"]
    alt3_keys: list[str] = ["COMBO_ALT1", "COMBO_ALT2"]
    limit: int = 0
    combo_timeout: int = 100

    key_positions: list[list[str]] = [
        ["", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", ""],
        ["", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", ""],
        ["", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", ""],
        ["", "COMBO_ALT1", "COMBO_ALT2", "COMBO_SFT", "COMBO", ""],
    ]

    def output(self, chords: list[Chord]):
        key_positions = [item for items in self.key_positions for item in items]
        macros = """#define MACRO(NAME, BINDINGS) \\
        macro_##NAME: macro_##NAME { \\
            compatible = "zmk,behavior-macro"; \\
            #binding-cells = <0>; \\
            wait-ms = <0>; \\
            tap-ms = <10>; \\
            bindings = <BINDINGS>; \\
        };

        """

        combos = (
            """#define COMBO(NAME, BINDINGS, KEYPOS) \\
        combo_##NAME { \\
            timeout-ms = <"""
            + str(self.combo_timeout)
            + """>; \\
            bindings = <BINDINGS>; \\
            key-positions = <KEYPOS>; \\
            layers = <0>; \\
        };

        """
        )

        key_positions_map = {}
        for i, key in enumerate(key_positions):
            key_positions_map[key] = i

        def translate_keys(abbr):
            result = []
            for k in abbr:
                k = k.upper()
                if k in key_positions_map:
                    result.append(key_positions_map[k])
                else:
                    raise Exception(
                        f'Unable to find key position for {k}, is it in "key_positions"?'
                    )
            result = [str(i) for i in result]
            return result

        def translate_macro(word, capitalize=False):
            result = []
            for i, k in enumerate(word):
                k = k.upper()
                kp = "&kp "
                if capitalize and i == 0:
                    kp += "LS("

                if k in key_map:
                    kp += key_map[k]
                else:
                    kp += k

                if capitalize and i == 0:
                    kp += ")"

                result.append(kp)
            return result

        # Convienience macros for punctuation
        for p in [";", ",", "."]:
            name = f"c_{key_map[p]}"
            macro = translate_macro(f"←{p} ")
            positions = translate_keys([p] + trigger_keys)
            macros += f"MACRO({name}, {' '.join(macro)})\n"
            combos += f"COMBO({name}, &macro_{name}, {' '.join(positions)})\n"

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
                name = f"c_{c}{'_' * i}".replace("'", "_")
                macro = translate_macro(word + " ")

                positions = translate_keys(list(c) + trigger_keys + alt)
                macros += f"MACRO({name}, {' '.join(macro)})\n"
                combos += f"COMBO({name}, &macro_{name}, {' '.join(positions)})\n"

                # shifted
                positions = translate_keys(list(c) + trigger_keys + alt + shifted_keys)
                macro = translate_macro(word + " ", True)
                macros += f"MACRO(s_{name}, {' '.join(macro)})\n"
                combos += f"COMBO(s_{name}, &macro_s_{name}, {' '.join(positions)})\n"

        print(f"Writing {self.macros_file}")
        with open(self.macros_file, "w") as file:
            file.write(macros)

        print(f"Writing {self.chords_file}")
        with open(self.chords_file, "w") as file:
            file.write(combos)
