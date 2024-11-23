import csv

expand_trigger = ":"
# suffix to add before the trigger to use the alternate forms in `abbr.tsv`
alt_suffix_1 = "q"
alt_suffix_2 = "j"
alt_suffix_3 = "z"

output = ""
line_no = 0
limit = 0
seen = {}


def add_abbr(word, trigger):
    global output
    if trigger in seen:
        raise Exception(
            f'Error line {line_no}: already used trigger "{trigger}" for word "{seen[trigger]}"'
        )
    output += f"{expand_trigger}{trigger}{expand_trigger} -> {word}\n"
    seen[trigger] = word


print("Processing abbr.tsv")
with open("abbr.tsv") as file:
    file = csv.reader(file, delimiter="\t")
    for line in file:
        line_no += 1

        if line[1]:
            add_abbr(line[0], line[1])
            if line[2]:
                add_abbr(line[2], f"{line[1]}{alt_suffix_1}")

print("writing qmk-autocorrect.txt")
with open("qmk-autocorrect.txt", "w") as file:
    file.write(output)
print("done")
