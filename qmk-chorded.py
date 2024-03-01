import csv
import utils

seen = {}
output = ""
line_no = 0

trigger_keys = ["KC_COMBO"]
shifted_keys = ["KC_COMBO_SFT"]
alt_keys = [["KC_COMBO_ALT1"], ["KC_COMBO_ALT2"], ["KC_COMBO_ALT1", "KC_COMBO_ALT2"]]

key_map = {
    "R": "KC_ALT_R",
    "S": "KC_GUI_S",
    "T": "KC_CTL_T",
    "D": "KC_SFT_D",
    "V": "KC_CAG_V",
    ";": "KC_CAG_SCLN",
    ",": "KC_COMMA",
    ".": "KC_DOT",
    "'": "KC_QUOT",
    "H": "KC_SFT_H",
    "N": "KC_CTL_N",
    "E": "KC_GUI_E",
    "I": "KC_ALT_I",
}


def translate_keys(abbr):
    result = trigger_keys.copy()
    for k in abbr:
        k = k.upper()
        if k in key_map:
            result.append(key_map[k])
        else:
            result.append(f"KC_{k}")
    return result


with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")
    for line in file:
        line_no += 1

        if line[1]:
            abbr = line.pop(1)
            if abbr in seen:
                raise Exception(
                    f'Error line {line_no}: already used trigger "{abbr}" for word "{seen[abbr]}"'
                )

            combinations = utils.find_all_combinations(abbr)
            for a in combinations:
                seen[a] = line[0]

            keys = translate_keys(abbr)
            for i, word in enumerate(line):
                if not word:
                    continue
                alt = []
                if i != 0:
                    alt = alt_keys[i - 1]
                name = f"c_{abbr}{i}".replace("'", "_")

                output += f'SUBS({name}, "{word}", {", ".join(keys + alt)})\n'
                output += f'SUBS({name}s, "{word.capitalize()}", {", ".join(keys + alt + shifted_keys)})\n'

with open("abbr.def", "w") as file:
    file.write(output)
