import csv

expand_trigger = ",;"
alt_suffix_1 = "q"
alt_suffix_2 = "j"
alt_suffix_3 = "z"
seen = {}
output = "matches:\n"
line_no = 0


def add_abbr(word, trigger):
    global output
    if trigger in seen:
        raise Exception(
            f'Error line {line_no}: already used trigger "{trigger}" for word "{seen[trigger]}"'
        )
    output += (
        f'  - trigger: "{trigger}{expand_trigger}"\n'
        f'    replace: "{word} "\n'
        f"    propagate_case: true\n"
        f'    uppercase_style: "capitalize_words"\n'
        f'  - trigger: "{trigger}.{expand_trigger}"\n'
        f'    replace: "{word}. "\n'
        f"    propagate_case: true\n"
        f'    uppercase_style: "capitalize_words"\n'
        f'  - trigger: "{trigger},{expand_trigger}"\n'
        f'    replace: "{word}, "\n'
        f"    propagate_case: true\n"
        f'    uppercase_style: "capitalize_words"\n'
        f'  - trigger: "{trigger};{expand_trigger}"\n'
        f'    replace: "{word}; "\n'
        f"    propagate_case: true\n"
        f'    uppercase_style: "capitalize_words"\n'
    )
    seen[trigger] = word


with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")
    for line in file:
        line_no += 1
        if line[1]:
            add_abbr(line[0], line[1])
        if line[2]:
            add_abbr(line[2], f"{line[1]}{alt_suffix_1}")
        if line[3]:
            add_abbr(line[3], f"{line[1]}{alt_suffix_2}")
        if line[4]:
            add_abbr(line[4], f"{line[1]}{alt_suffix_3}")

with open("abbr.yml", "w") as file:
    file.write(output)
