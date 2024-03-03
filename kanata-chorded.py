import csv
import utils

# Limit how many rows to process
limit = 0
# How long in ms you have to press the combo keys together, you can be pretty relaxed here if combo is its own unique key
combo_timeout = 100
# Configure your base mappings here
# Note: there are some issues with tap-holds in combos https://github.com/jtroo/kanata/issues/743
output = (
    f"(defchords combos {combo_timeout}"
    + """
  (w) w
  (l) l
  (y) y
  (p) p
  (b) b
  (c) (tap-hold $tap-timeout $hold-timeout c lsft)
  (r) (tap-hold $tap-timeout $hold-timeout r lalt)
  (s) (tap-hold $tap-timeout $hold-timeout s lmet)
  (t) (tap-hold $tap-timeout $hold-timeout t lctl)
  (g) g
  (q) q
  (j) j
  (d) d
  (v) v
  (k) k
  (z) z
  (f) f
  (o) o
  (u) u
  (') '
  (m) m
  (n) (tap-hold $tap-timeout $hold-timeout n rctl)
  (e) (tap-hold $tap-timeout $hold-timeout e rmet)
  (i) (tap-hold $tap-timeout $hold-timeout i lalt)
  (a) (tap-hold $tap-timeout $hold-timeout a lsft)
  (;) ;
  (x) x
  (h) h
  (,) ,
  (.) .
  (alt1) (tap-hold-press $tap-timeout $hold-timeout tab (layer-toggle nav))
  (alt2) (tap-hold $tap-timeout $hold-timeout spc (layer-toggle media))
  (sft) (tap-hold-press $tap-timeout $hold-timeout bspc lsft)
  (cbo) XX
"""
)

seen = {}
line_no = 0

combo_keys = ["cbo"]
shifted_keys = ["sft"]
alt_keys = [["alt1"], ["alt2"], ["alt1", "alt2"]]

key_map = {
    " ": "spc",
    "←": "bspc",
}


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
        if k in key_map:
            result.append(key_map[k])
        else:
            result.append(k.lower())
    return result


print("Processing abbr.tsv")
with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")

    for p in [";", ",", "."]:
        combo = translate_combo(p)
        macro = translate_macro(f"←{p} ")
        output += (
            f'  ({" ".join(combo_keys)} {" ".join(combo)}) (macro {" ".join(macro)})\n'
        )

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

                output += f'  ({" ".join(combo_keys + alt)} {" ".join(combo)}) (macro {" ".join(macro)})\n'
                shifted_macro = translate_macro(word.capitalize() + " ")
                output += f'  ({" ".join(combo_keys + alt + shifted_keys)} {" ".join(combo)}) (macro {" ".join(shifted_macro)})\n'
    output += ")"


print("writing abbr.kbd")
with open("abbr.kbd", "w") as file:
    file.write(output)
print("done")
