import csv
import logging
import os
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from abbrgen.config import load_or_create_config


from .utils import find_combinations

from pattern import en


min_len = 3
config = load_or_create_config()
keyboard = config.keyboard


def score(line: tuple[str, str]) -> dict:
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


def abbrgen() -> None:
    logging.basicConfig(level="INFO")
    with open("words.tsv") as file:
        file = csv.reader(file, delimiter="\t")

        alt_data = {}
        if os.path.isfile("alt.tsv"):
            logging.debug("loading alt.tsv")
            with open("alt.tsv") as alt_file:
                alt_file = csv.reader(alt_file, delimiter="\t")
                for abbr in alt_file:
                    if abbr:
                        alt_data[abbr[0]] = abbr[1:]
        logging.info("Finding combinations")
        rows = [line for line in file if len(line[0]) >= min_len]
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

    logging.info("Writing abbr.tsv")
    with open("abbr.tsv", "w", newline="") as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter="\t")

        tsv_writer.writerow(["word", "combo", "alt1", "alt2", "alt3"])
        for abbr in selected_abbrs:
            alt = abbr["alt"]
            tsv_writer.writerow(
                [abbr["word"], abbr["option"]["combination"], alt[0], alt[1], alt[2]]
            )
