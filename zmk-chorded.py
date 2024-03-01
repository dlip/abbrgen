import csv
import utils

# Needs to map all of your keys
key_positions = [
    "W",
    "L",
    "Y",
    "P",
    "B",
    "Z",
    "F",
    "O",
    "U",
    "'",
    "C",
    "R",
    "S",
    "T",
    "G",
    "M",
    "N",
    "E",
    "I",
    "A",
    "Q",
    "J",
    "V",
    "D",
    "K",
    "X",
    "H",
    ";",
    ",",
    ".",
    "COMBO_ALT1",
    "COMBO_ALT2",
    "COMBO_SFT",
    "COMBO",
]

key_map = {
    "'": "QUOT",
    ";": "SEMI",
    ",": "COMMA",
    ".": "DOT",
    " ": "SPC",
    "@": "AT",
    "?": "QUESTION",
}

seen = {}
output = ""
macros = """#define str(s) #s
#define MACRO(NAME, BINDINGS)
  macro_##NAME: macro_##NAME {
      compatible = "zmk,behavior-macro";
      label = str(macro_##NAME);
      #binding-cells = <0>;
      wait-ms = <0>;
      tap-ms = <10>;
      bindings = <BINDINGS>;
  };

"""

combos = """#define COMBO(NAME, BINDINGS, KEYPOS)
  combo_##NAME {
    timeout-ms = <80>;
    bindings = <BINDINGS>;
    key-positions = <KEYPOS>;
    layers = <0>;
  };

"""
line_no = 0

trigger_keys = ["COMBO"]
shifted_keys = ["COMBO_SFT"]
alt_keys = [["COMBO_ALT1"], ["COMBO_ALT2"], ["COMBO_ALT1", "COMBO_ALT2"]]

key_positions_map = {}
for i, key in enumerate(key_positions):
    key_positions_map[key] = i


def translate_keys(abbr):
    result = []
    for k in abbr:
        k = k.upper()
        if k in key_positions_map:
            result.append(str(key_positions_map[k]))
        else:
            raise Exception(
                f'Unable to find key position for {k}, is it in "key_positions"?'
            )
    return result


def translate_macro(abbr):
    result = []
    for k in abbr:
        k = k.upper()
        if k in key_map:
            result.append(f"&kp {key_map[k]}")
        else:
            result.append(f"&kp {k}")
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

            for i, word in enumerate(line):
                if not word:
                    continue
                alt = []
                if i != 0:
                    alt = alt_keys[i - 1]
                name = f"c_{abbr}{i}".replace("'", "_")
                macro = translate_macro(abbr + " ")

                positions = translate_keys(list(abbr) + trigger_keys + alt)
                macros += f'MACRO({name}, {" ".join(macro)})\n'
                combos += f'COMBO({name}, &macro_{name}, {" ".join(positions)})\n'

with open("macros.def", "w") as file:
    file.write(macros)

with open("combos.def", "w") as file:
    file.write(combos)
