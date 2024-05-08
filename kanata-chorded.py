import csv
import utils

# Limit how many rows to process
limit = 0
# How long in ms you have to press the combo keys together, you can be pretty relaxed here if combo is its own unique key
combo_timeout = 100
# Configure your base mappings here
mapping = {
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

combo_keys = ["prtsc"]
shifted_keys = ["ralt"]
alt_keys = [["lalt"], ["spc"], ["lalt", "spc"]]

seen = {}
line_no = 0

key_map = {
    " ": "spc",
    "←": "bspc",
}

output = "(defchordsv2-experimental\n"


def translate_macro(word):
    result = []
    for i, k in enumerate(word):
        kp = ""
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
        if k in mapping:
            result.append(mapping[k])
        else:
            raise Exception(f"No key_map for {k}")
    return result


print("Processing abbr.tsv")
with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")

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

            for i, word in enumerate(line):
                if not word:
                    continue
                alt = []
                if i != 0:
                    alt = alt_keys[i - 1]

                combo = translate_combo(abbr)
                macro = translate_macro(word + " ")

                output += f'  ({" ".join(combo_keys + alt)} {" ".join(combo)}) (macro {" ".join(macro)}) {combo_timeout} first-release ()\n'
                shifted_macro = translate_macro(word.capitalize() + " ")
                output += f'  ({" ".join(combo_keys + alt + shifted_keys)} {" ".join(combo)}) (macro {" ".join(shifted_macro)}) {combo_timeout} first-release ()\n'
    output += ")"


print("writing abbr.kbd")
with open("abbr.kbd", "w") as file:
    file.write(output)
print("done")
