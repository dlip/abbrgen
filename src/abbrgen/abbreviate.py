import csv
import logging
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from abbrgen.alt_generator import AltGenerator
from abbrgen.config import Config
from abbrgen.scorer import Scorer


def abbreviate(config: Config) -> None:
    global keyboard
    keyboard = config.keyboard
    scorer = Scorer(config)
    with open(config.abbreviation_file) as f:
        reader = csv.DictReader(f)
        logging.info("Finding combinations")
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

    logging.info("Selecting combinations")
    for abbr in tqdm(abbrs):
        word = abbr["word"].lower()
        if word in seen:
            duplicate.append(word)
            continue
        seen[word] = True
        options = abbr.get("options")
        if options:
            for option in options:
                combination = option["combination"]
                # ensure combination is sorted so we can quickly check if they have been used
                sorted_combination = "".join(sorted(combination))
                if sorted_combination not in used:
                    abbr["abbreviation"] = option["combination"]
                    break
            if not abbr["abbreviation"]:
                no_options.append(word)

        if abbr["abbreviation"]:
            sorted_abbreviation = "".join(sorted(abbr["abbreviation"]))
            used[sorted_abbreviation] = word

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
