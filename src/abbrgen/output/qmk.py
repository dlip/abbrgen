from abbrgen.abbreviation import Abbreviation, load_abbreviation_file, validate_combos
from pydantic import BaseModel


class QmkOutput(BaseModel):
    combo_keys: list[str] = ["KC_COMBO"]
    shift_keys: list[str] = ["KC_COMBO_SFT"]
    alt1_keys: list[str] = ["KC_COMBO_ALT1"]
    alt2_keys: list[str] = ["KC_COMBO_ALT2"]
    alt3_keys: list[str] = ["KC_COMBO_ALT1", "KC_COMBO_ALT2"]
    key_codes: dict[str, str] = {
        "C": "KC_SFT_C",
        "I": "KC_ALT_I",
        "E": "KC_GUI_E",
        "A": "KC_CTL_A",
        "H": "KC_CTL_H",
        "T": "KC_GUI_T",
        "S": "KC_ALT_S",
        "N": "KC_SFT_N",
        "J": "KC_CAG_J",
        "M": "KC_CAG_M",
        ";": "KC_SCLN",
        ",": "KC_COMMA",
        ".": "KC_DOT",
        "'": "KC_QUOT",
        "-": "KC_MINUS",
    }

    def translate_keys(self, combo):
        result = self.combo_keys.copy()
        for k in combo:
            k = k.upper()
            if k in self.key_codes:
                result.append(self.key_codes[k])
            else:
                result.append(f"KC_{k}")

        return result

    def generate(self, abbrs: list[Abbreviation]):
        output = ""
        for abbr in abbrs:
            combo = abbr["combo"]
            if combo:
                words = [abbr["word"], abbr["alt1"], abbr["alt2"], abbr["alt3"]]
                for i, word in enumerate(words):
                    if not word:
                        continue
                    keys = self.translate_keys(abbr["combo"])
                    alt_keys = [self.alt1_keys, self.alt2_keys, self.alt3_keys]
                    alt = []
                    if i > 0:
                        alt = alt_keys[i - 1]
                    name = f"c_{word}{i}".replace("'", "_").replace("-", "_")

                    output += f'SUBS({name}, "{word} ", {", ".join(keys + alt)})\n'
                    output += f'SUBS({name}s, "{word.capitalize()} ", {", ".join(keys + alt + self.shift_keys)})\n'

        print("writing abbr.def")
        with open("abbr.def", "w") as file:
            file.write(output)
        print("done")
