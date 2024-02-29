import csv
import utils

seen = {}
output = ""
line_no = 0

key_map = {
    "R": "KC_ALT_R",
    "S": "KC_GUI_S",
    "T": "KC_CTL_T",
    "D": "KC_SFT_D",
    "V": "KC_CAG_V",
    "SCLN": "KC_CAG_SCLN",
    "H": "KC_SFT_H",
    "N": "KC_CTL_N",
    "E": "KC_GUI_E",
    "I": "KC_ALT_I",
}


def translate_keys(abbr):
    result = ["KC_TRIGGER"]
    for k in abbr:
        k = k.upper()
        if k in key_map:
            result.append(key_map[k])
        else:
            result.append(f"KC_{k}")
    return ", ".join(result)


with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")
    for line in file:
        line_no += 1

        if line[1]:
            word = line[0]
            abbr = line[1]
            if abbr in seen:
                raise Exception(
                    f'Error line {line_no}: already used trigger "{abbr}" for word "{seen[abbr]}"'
                )

            combinations = utils.find_all_combinations(abbr)
            for a in combinations:
                seen[a] = word
            keys = translate_keys(abbr)
            output += f'SUBS({abbr}, "{word}", {keys})\n'
            if line[2]:
                output += f'SUBS({abbr}1, "{line[2]}", {keys}, KC_COMBO_ALT1)\n'
            if line[3]:
                output += f'SUBS({abbr}2, "{line[3]}", {keys}, KC_COMBO_ALT2)\n'
            if line[4]:
                output += f'SUBS({abbr}3, "{line[4]}", {keys}, KC_COMBO_ALT3)\n'

with open("abbr.def", "w") as file:
    file.write(output)
