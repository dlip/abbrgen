from abbrgen.abbreviation import load_abbreviation_file, validate_combos
from abbrgen.config import Config


key_map = {
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
    "←": "KC_BSPC",
}

trigger_keys = ["KC_COMBO"]
shifted_keys = ["KC_COMBO_SFT"]
alt_keys = [["KC_COMBO_ALT1"], ["KC_COMBO_ALT2"], ["KC_COMBO_ALT1", "KC_COMBO_ALT2"]]


def translate_keys(combo):
    result = trigger_keys.copy()
    for k in combo:
        k = k.upper()
        if k in key_map:
            result.append(key_map[k])
        else:
            result.append(f"KC_{k}")
    return result


class QmkGenerator:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._abbrs = load_abbreviation_file(self._config.abbreviation_file)
        validate_combos(self._abbrs)

    def generate(self):
        output = ""
        for abbr in self._abbrs:
            combo = abbr["combo"]
            if combo:
                words = [abbr["word"], abbr["alt1"], abbr["alt2"], abbr["alt3"]]
                for i, word in enumerate(words):
                    if not word:
                        continue
                    keys = translate_keys(abbr["combo"])
                    alt = []
                    if i > 0:
                        alt = alt_keys[i - 1]
                    name = f"c_{word}{i}".replace("'", "_").replace("-", "_")

                    output += f'SUBS({name}, "{word} ", {", ".join(keys + alt)})\n'
                    output += f'SUBS({name}s, "{word.capitalize()} ", {", ".join(keys + alt + shifted_keys)})\n'

        print("writing abbr.def")
        with open("abbr.def", "w") as file:
            file.write(output)
        print("done")
