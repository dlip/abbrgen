import csv
import utils

# Limit how many rows to process since microcontrollers such as pro micro have quite limited memory
# You'll need to lower this if you get memory errors when compiling
limit = 0
# Needs to match what you have defined in your keymap. If you have other mod tap with alphas you need to map each to a letter. If you aren't using mod tap you can remove the alpha mappings here and restore `KC_SCLN` for semicolon.
key_map = {
    "S": "KC_ALT_S",
    "T": "KC_GUI_T",
    "A": "KC_CTL_A",
    "W": "KC_CAG_W",
    "N": "KC_CTL_N",
    "E": "KC_GUI_E",
    "D": "KC_ALT_D",
    "U": "KC_CAG_U",
    ";": "KC_SCLN",
    ",": "KC_SFT_CMA",
    ".": "KC_SFT_DOT",
    "'": "KC_QUOT",
    "-": "KC_MINUS",
    "←": "KC_BSPC",
}

seen = {}
output = ""
line_no = 0

trigger_keys = ["KC_COMBO"]
shifted_keys = ["KC_COMBO_SFT"]
alt_keys = [["KC_COMBO_ALT1"], ["KC_COMBO_ALT2"], ["KC_COMBO_ALT1", "KC_COMBO_ALT2"]]


def translate_keys(abbr):
    result = trigger_keys.copy()
    for k in abbr:
        k = k.upper()
        if k in key_map:
            result.append(key_map[k])
        else:
            result.append(f"KC_{k}")
    return result


print("Processing abbr.tsv")
with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")
    for p in [";", ",", "."]:
        name = f"c_{key_map[p]}"
        keys = translate_keys(p)
        output += f'SUBS({name}, SS_TAP(X_BSPC)"{p} ", {", ".join(keys)})\n'

    for line in file:
        line_no += 1
        if limit != 0 and line_no > limit:
            print(f"Stopping at line {limit} due to limit setting")
            break

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
            no_combo = keys.copy()
            no_combo.pop(0)  # quick hack to make shifted_keys individual for harite
            for i, word in enumerate(line):
                if not word:
                    continue
                alt = []
                if i != 0:
                    alt = alt_keys[i - 1]
                name = f"c_{abbr}{i}".replace("'", "_").replace("-", "_")

                output += f'SUBS({name}, "{word} ", {", ".join(keys + alt)})\n'
                output += f'SUBS({name}s, "{word.capitalize()} ", {", ".join(no_combo + alt + shifted_keys)})\n'

print("writing abbr.def")
with open("abbr.def", "w") as file:
    file.write(output)
print("done")
