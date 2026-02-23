import csv
import logging
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from tqdm import tqdm

from abbrgen.config import load_or_create_config


from .utils import find_combinations

from pattern import en


min_len = 3
keyboard = None


def score(line: dict) -> dict:
    result = line
    if result["abbr"]:
        return result

    combinations = find_combinations(line[0].lower())
    scores = [keyboard.score(combination) for combination in combinations]
    options = [
        {"combination": combination, "score": scores[i]}
        for i, combination in enumerate(combinations)
        if scores[i] != -1
    ]
    options = sorted(options, key=lambda x: x["score"])
    result = {
        "word": line[0],
        "type": line[1],
        "options": options,
    }
    logging.debug(f"Computed: {result}")
    return result


def add_alt(abbr):
    alt = ["", "", ""]
    word = abbr["word"]
    type = abbr["type"]
    # if word in alt_data:
    #     alt = alt_data[word]
    if type == "VERB":
        alt[0] = en.conjugate(word, "3sg")
        alt[1] = en.conjugate(word, "1sgp")
        alt[2] = en.conjugate(word, "part")
    elif type == "NOUN":
        alt[0] = en.pluralize(word, pos=en.NOUN)
    abbr["alt"] = alt
    return abbr


def abbreviate(config_path: Path) -> None:
    logging.basicConfig(level="INFO")

    config = load_or_create_config(config_path)
    global keyboard
    keyboard = config.keyboard
    with open(config.abbreviation_file) as f:
        reader = csv.DictReader(f)
        logging.info("Finding combinations")
        for l in reader:
            raise Exception(l)
        rows = [line for line in reader if len(line[0]) >= min_len]
        with ProcessPoolExecutor() as executor:
            abbrs = list(
                tqdm(
                    executor.map(score, rows, chunksize=10),
                    total=len(rows),
                )
            )

    # output = ""
    used = {}
    seen = {}
    selected_abbrs = []
    no_options = []
    duplicate = []

    logging.info("Selecting combinations")
    for abbr in tqdm(abbrs):
        word = abbr["word"].lower()
        if word in seen:
            duplicate.append(word)
            continue
        seen[word] = True
        for option in abbr["options"]:
            combination = option["combination"]
            # ensure combination is sorted so we can quickly check if they have been used
            sorted_combination = "".join(sorted(combination))
            if sorted_combination not in used:
                abbr["option"] = option
                used[sorted_combination] = word
                break
        if "option" not in abbr:
            no_options.append(word)
            continue
        selected_abbrs.append(abbr)

    logging.info(
        f"Unable to find any options for {len(no_options)} words: {', '.join(no_options)}"
    )
    logging.info(f"Ignored {len(duplicate)} duplicate words: {', '.join(duplicate)}")

    logging.info("Adding alternate modifiers")
    with ProcessPoolExecutor() as executor:
        selected_abbrs = list(
            tqdm(
                executor.map(add_alt, selected_abbrs, chunksize=10),
                total=len(selected_abbrs),
            )
        )

    logging.info(f"Writing {config.abbreviation_file}")
    with open(config.abbreviation_file, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["word", "combo", "alt1", "alt2", "alt3"])
        for abbr in selected_abbrs:
            alt = abbr["alt"]
            writer.writerow(
                [abbr["word"], abbr["option"]["combination"], alt[0], alt[1], alt[2]]
            )
