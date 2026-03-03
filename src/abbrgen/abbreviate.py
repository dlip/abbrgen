import csv
import logging
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from abbrgen.alt_generator import AltGenerator
from abbrgen.config import Config
from abbrgen.scorer import Scorer


def abbreviate(config: Config) -> None:
    scorer = Scorer(config)
    with open(config.abbreviation_file) as f:
        reader = csv.DictReader(f)
        logging.info("Finding combos")
        abbrs = [line for line in reader]
        if len(abbrs) == 0:
            raise Exception("No rows found in abbreviation file")
        with ProcessPoolExecutor() as executor:
            abbrs = list(
                tqdm(
                    executor.map(scorer.score, abbrs, chunksize=10),
                    total=len(abbrs),
                )
            )

    used = {}
    seen = {}
    no_options = []
    duplicate = []

    logging.info("Reserving combos")
    for abbr in tqdm(abbrs):
        reserved_combo = abbr["reserved_combo"]
        abbr["combo"] = reserved_combo
        if not reserved_combo:
            continue
        sorted_combo = "".join(sorted(reserved_combo))
        if sorted_combo in used:
            raise Exception(
                f"Reserved combo for word {abbr['word']} already used for {used[sorted_combo]['word']}"
            )
        used[sorted_combo] = abbr

    logging.info("Selecting combos")
    for abbr in tqdm(abbrs):
        word = abbr["word"].lower()
        if word in seen:
            duplicate.append(word)
            continue
        seen[word] = True
        if len(word) < config.min_word_length:
            continue
        reserved_combo = abbr["reserved_combo"]
        if reserved_combo:
            continue
        for option in abbr["options"]:
            sorted_combo = "".join(sorted(option["combo"]))
            if sorted_combo not in used:
                abbr["combo"] = option["combo"]
                used[sorted_combo] = abbr
                break

        if not abbr["combo"]:
            no_options.append(word)

    if len(no_options) > 0:
        logging.info(
            f"Unable to find any options for {len(no_options)} words: {', '.join(no_options)}"
        )
    if len(duplicate) > 0:
        logging.info(
            f"Ignored {len(duplicate)} duplicate words: {', '.join(duplicate)}"
        )

    logging.info("Adding alternate modifiers")
    alt_generator = AltGenerator(config)
    with ProcessPoolExecutor() as executor:
        abbrs = list(
            tqdm(
                executor.map(alt_generator.add_alt, abbrs, chunksize=10),
                total=len(abbrs),
            )
        )

    logging.info(f"Writing {config.abbreviation_file}")
    with open(config.abbreviation_file, "w", newline="") as f:
        fieldnames = list(abbrs[0].keys())
        if "options" in fieldnames:
            fieldnames.remove("options")
        writer = csv.DictWriter(
            f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(abbrs)
