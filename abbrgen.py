import csv
import logging
import sys
import json
import inflect

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

p = inflect.engine()

used = {}
seen = {}
limit = 0
line_no = 0
min_chars = 3
min_improvement = 40
banned_suffixes = "qj"
# avoid same finger bigrams (sequences which use the same key in a row)
avoid_sfb = True
layout_qwerty = """
qwertyuiop
asdfghjkl;
zxcvbnm,./
"""
layout_colemak = """
qwfpgjluy;
arstdhneio
zxcvbkm,./
"""
layout_colemak_dh = """
qwfpbjluy;
arstgmneio
zxcdvkh,./
"""
layout_canary = """
wlypkzfou'
crstbxneia
qjvdgmh/,.
"""
keyboard_layout = layout_canary
keyboard_finger_maping = """
1234455678
1234455678
1234455678
"""
keyboard_layout_map = {}
for i in range(0, len(keyboard_layout)):
    keyboard_layout_map[keyboard_layout[i]] = keyboard_finger_maping[i]


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


def has_sfb(abbr):
    for i in range(0, len(abbr) - 1):
        if keyboard_layout_map[abbr[i]] == keyboard_layout_map[abbr[i + 1]]:
            return True
    return False


def find_abbr(word):
    log.debug(f"=== {word} ===")
    if len(word) < min_chars:
        log.debug(f"rejected: minimum chars less than {min_chars}")
        return None
    if word in seen:
        log.debug(f"rejected: already seen")
        return None
    for c in word:
        if c not in keyboard_layout:
            log.debug(f"rejected: letter '{c}' not in keyboard layout")
            return None

    seen[word] = True
    combinations = find_combinations(word)
    combinations.sort(key=len)
    sfb_option = None
    for abbr in combinations:
        log.debug(abbr)
        if not abbr in used:
            if len(abbr) > 1 and abbr[-1] in banned_suffixes:
                log.debug(f"rejected: '{abbr[-1]}' is a banned suffix")
                continue
            improvement = ((len(word) - len(abbr)) / len(word)) * 100
            if improvement > min_improvement:
                if avoid_sfb and has_sfb(abbr):
                    if not sfb_option:
                        sfb_option = abbr
                    log.debug(f"avoided: has sfb. improvement: {improvement}")
                    continue
                log.debug(f"selected: improvement: {improvement}")
                used[abbr] = word
                return abbr
            else:
                log.debug(f"rejected: improvement insufficient: {improvement}")
                if sfb_option:
                    log.debug(f"fallback to sfb option: {sfb_option}")
                    used[sfb_option] = word
                    return sfb_option
                return None
        else:
            log.debug("rejected: already used")

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

        if abbr:
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

    with open("abbr.txt", "w") as file:
        file.write(output)
