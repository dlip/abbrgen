# Generates training.txt for the user to practice abbrs
import csv

expand_trigger = ",;"
alt_suffix_1 = "q"
alt_suffix_2 = "j"
seen = {}
output = "matches:\n"
line_no = 0

with open("abbr.tsv") as abbr_file:
    abbr_file = csv.reader(abbr_file, delimiter="\t")
    index = 0
    words = ""
    abbrs = ""
    with open("training.txt", "w") as training_file:
        for line in abbr_file:
            word = line[0]
            abbr = line[1]
            words += f"{word} "
            abbrs += abbr + (" " * (len(word) + 1 - len(abbr)))
            index += 1
            if index % 10 == 0:
                training_file.write(words.rstrip())
                training_file.write("\n")
                training_file.write(abbrs.rstrip())
                training_file.write("\n")
                words = ""
                abbrs = ""
