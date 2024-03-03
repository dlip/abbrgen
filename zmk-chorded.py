import csv
import utils

# Limit how many rows to process since microcontrollers such as nice nano have quite limited memory
# You'll need to lower this if you get "region `RAM' overflowed errors" when compiling
limit = 100
# How long in ms you have to press the combo keys together, you can be pretty relaxed here if combo is its own unique key
combo_timeout = 100
# You need to map all of your keys here since zmk combos are offset based
# You can use an empty string ("") for anything other than letters, punctuation and combo positions such that it adds up to the total numbers of keys on your keyboard, check the example below
key_positions = [
    ["W", "L", "Y", "P", "B", "Z", "F", "O", "U", "'"],
    ["C", "R", "S", "T", "G", "M", "N", "E", "I", "A"],
    ["Q", "J", "V", "D", "K", "X", "H", ";", ",", "."],
    ["COMBO_ALT1", "COMBO_ALT2", "COMBO_SFT", "COMBO"],
]

# 42-key keyboard example
# key_positions = [
#     ["", "W", "L", "Y", "P", "B", "Z", "F", "O", "U", "'", ""],
#     ["", "C", "R", "S", "T", "G", "M", "N", "E", "I", "A", ""],
#     ["", "Q", "J", "V", "D", "K", "X", "H", ";", ",", ".", ""],
#     ["", "COMBO_ALT1", "COMBO_ALT2", "COMBO_SFT", "COMBO", ""],
# ]

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

key_positions = [item for items in key_positions for item in items]
seen = {}
output = ""
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
    + str(combo_timeout)
    + """>; \\
    bindings = <BINDINGS>; \\
    key-positions = <KEYPOS>; \\
    layers = <0>; \\
  };

"""
)
line_no = 0


key_positions_map = {}
for i, key in enumerate(key_positions):
    key_positions_map[key] = i

seen_positions = {}


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
    # ensure there is no duplicate positions used since zmk doesn't check
    result.sort()
    result = [str(i) for i in result]
    name = " ".join(result)
    if name in seen_positions:
        raise Exception(
            f"Error: duplicate combos on lines {seen_positions[name]} and {line_no}"
        )
    seen_positions[name] = line_no
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


print("Processing abbr.tsv")
with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")
    for p in [";", ",", "."]:
        name = f"c_{key_map[p]}"
        macro = translate_macro(f"←{p} ")
        positions = translate_keys([p] + trigger_keys)
        macros += f'MACRO({name}, {" ".join(macro)})\n'
        combos += f'COMBO({name}, &macro_{name}, {" ".join(positions)})\n'

    for line in file:
        line_no += 1
        if line_no > limit:
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

            for i, word in enumerate(line):
                if not word:
                    continue
                alt = []
                if i != 0:
                    alt = alt_keys[i - 1]
                name = f'c_{abbr}{"_" * i}'.replace("'", "_")
                macro = translate_macro(word + " ")

                positions = translate_keys(list(abbr) + trigger_keys + alt)
                macros += f'MACRO({name}, {" ".join(macro)})\n'
                combos += f'COMBO({name}, &macro_{name}, {" ".join(positions)})\n'

                # shifted
                positions = translate_keys(
                    list(abbr) + trigger_keys + alt + shifted_keys
                )
                macro = translate_macro(word + " ", True)
                macros += f'MACRO(s_{name}, {" ".join(macro)})\n'
                combos += f'COMBO(s_{name}, &macro_s_{name}, {" ".join(positions)})\n'

print("writing macros.dtsi")
with open("macros.dtsi", "w") as file:
    file.write(macros)

with open("combos.dtsi", "w") as file:
    file.write(combos)
print("writing combos.dtsi")
print("done")
