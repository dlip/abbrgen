import csv
import logging
import sys
import json
import inflect
import layout

# stop after processing this many lines in words.txt
limit = 0
# any word shorter than this will be excluded
min_chars = 3
# any percent improvement below this will not be considered and the word might be excluded if there are no other options
min_improvement = 40
# the abbreviations will not end with any of these characters so you can use them as a suffix to access the alternate abbreviation forms
banned_suffixes = "qjz;,."
# output the words with no abbreviation found so you can add them by hand
output_all = False
# change this to your keyboard layout, ensure its listed in layout.py
keyboard_layout = layout.canary
# change this to the effort map for your keyboard shape: effort_map_standard, effort_map_matrix
effort_map = layout.effort_map_matrix
# this is the effort multiplier to penalize same finger bigrams (sequences which use the same key in a row)
sfb_multiplier = 2

# internal variables
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

calc = layout.EffortCalculator(keyboard_layout, effort_map, sfb_multiplier)
p = inflect.engine()

used = {}
seen = {}
line_no = 0


def find_combinations(s, prefix="", index=0):
    """
    Recursively find every combination of letters in a string from left to right
    starting with the first character.

    Args:
    - s: The input string.
    - prefix: The current combination being built.
    - index: The current index in the string.

    Returns:
    - result: A list containing all combinations starting with the first character
              and excluding the empty string, sorted by shortest string first.
    """
    result = []
    if index == len(s):
        if prefix:
            result.append(prefix)
        return result

    # Include the current character only if it's the first character or part of a previous combination
    if index == 0 or prefix:
        result.extend(find_combinations(s, prefix + s[index], index + 1))

    # Exclude the current character
    result.extend(find_combinations(s, prefix, index + 1))

    return result


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
    combinations = find_combinations(word)
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
                try:
                    effort = calc.calculate(abbr)
                    log.debug(f"effort: {effort}")
                    options.append({"abbr": abbr, "effort": effort})
                except Exception as e:
                    log.debug(e)
            else:
                log.debug(f"rejected: improvement insufficient ({improvement}%)")
                break
        else:
            log.debug("rejected: already used")

    if options:
        options.sort(key=lambda x: x["effort"])
        abbr = options[0]["abbr"]
        log.debug(f"selected: {abbr}")
        used[abbr] = word
        return abbr

    log.debug("dropped: no abbr found")
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

            line = f"{word}\t{abbr}\t" + "\t".join(alt)
            log.info(line)
            output += line + "\n"

    with open("abbr.tsv", "w") as file:
        file.write(output)
