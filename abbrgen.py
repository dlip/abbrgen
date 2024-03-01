import csv
import logging
import sys
import json
import inflect
import layout
import utils

# stop after processing this many lines in words.txt
limit = 0
# any word shorter than this will be excluded
min_chars = 3
# any percent improvement below this will not be considered and the word might be excluded if there are no other options
min_improvement = 40
# the abbreviations will not end with any of these characters so you can use them as a suffix to access the alternate abbreviation forms or punctuation
banned_suffixes = "qjzx;,.:'?"
# output the words with no abbreviation found so you can add them by hand
output_all = False
# change this to your keyboard layout, ensure its listed in layout.py
keyboard_layout = layout.canary
# change this to the effort map for your keyboard shape: effort_map_standard, effort_map_matrix
effort_map = layout.effort_map_matrix
# chorded mode will ensure its possible to chord and remove sfb's and scissors completely
chorded_mode = True
# this is the effort penalty added to sequences with same finger bigrams (using the same finger for 2 keys in a row)
sfb_penalty = 0.8
# this is the effort penalty added to sequences with scissors (travelling between the top and bottom rows on the same hand)
scissor_penalty = 0.5

# internal variables
log = logging.getLogger("abbrgen")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

calc = layout.EffortCalculator(keyboard_layout, effort_map)
p = inflect.engine()

used = {}
seen = {}
line_no = 0


def find_abbr(word):
    word = word.lower()
    log.debug(f"=== {word} ===")
    if len(word) < min_chars:
        log.debug(f"rejected: minimum chars less than {min_chars}")
        return None
    if word in seen:
        log.debug(f"rejected: already seen")
        return None

    seen[word] = True
    combinations = utils.find_combinations(word)
    combinations.sort(key=len)
    sfb_option = None
    options = []
    for abbr in combinations:
        log.debug(abbr)
        if not abbr in used:
            if len(abbr) > 1 and abbr[-1] in banned_suffixes:
                log.debug(f"rejected: '{abbr[-1]}' is a banned suffix")
                continue
            improvement = ((len(word) - len(abbr)) / len(word)) * 100
            if improvement >= min_improvement:
                effort = calc.calculate(
                    abbr, sfb_penalty, scissor_penalty, chorded_mode
                )
                if not effort:
                    continue
                log.debug(f"effort: {effort}")
                options.append({"abbr": abbr, "effort": effort})
            else:
                log.debug(f"rejected: improvement insufficient ({improvement}%)")
                break
        else:
            log.debug("rejected: already used")

    if options:
        options.sort(key=lambda x: x["effort"])
        abbr = options[0]["abbr"]
        log.debug(f"selected: {abbr}")
        if chorded_mode:
            # need to mark every possible combination as used
            combinations = utils.find_all_combinations(abbr)
            for a in combinations:
                used[a] = word
        else:
            used[abbr] = word
        return abbr

    log.debug("dropped: no abbreviation found")
    return None


with open("words.txt") as file:
    verb_data = {}
    with open("verbs-conjugations.json") as verbs_file:
        data = json.load(verbs_file)
        for verb in data:
            verb_data[verb["verb"]] = verb

    output = ""
    while True:
        line_no += 1
        if limit > 0 and line_no > limit:
            break
        word = file.readline()
        if not word:
            break
        word = word.strip()
        abbr = find_abbr(word)

        if output_all or abbr:
            abbr = abbr or ""
            alt = ["", "", ""]
            if word in verb_data:
                verb = verb_data[word]
                if "participle" in verb:
                    alt[0] = verb["participle"][0]
                if "gerund" in verb:
                    alt[1] = verb["gerund"][0]
            plural = p.plural_noun(word)
            if plural:
                alt[2] = plural

            for a in alt:
                if a:
                    seen[a] = True

            line = f"{word}\t{abbr}\t" + "\t".join(alt)
            log.info(line)
            output += line + "\n"

    with open("abbr.tsv", "w") as file:
        file.write(output)
