import csv
import logging
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from chordgen.alt_generator import AltGenerator
from chordgen.config import Config
from chordgen.scorer import Scorer


def gen(config: Config) -> None:
    scorer = Scorer(config)
    with open(config.chords_file) as f:
        reader = csv.DictReader(f)
        print("Finding and scoring chords")
        chords = [line for line in reader]
        if len(chords) == 0:
            raise Exception("No rows found in abbreviation file")
        with ProcessPoolExecutor() as executor:
            chords = list(
                tqdm(
                    executor.map(scorer.score, chords, chunksize=10),
                    total=len(chords),
                )
            )

    used = {}
    seen = {}
    no_options = []
    duplicate = []

    print("Setting reserved chords")
    for chord in tqdm(chords):
        reserved_chord = chord["reserved_chord"]
        chord["chord"] = reserved_chord
        if not reserved_chord:
            continue
        sorted_chord = "".join(sorted(reserved_chord))
        if sorted_chord in used:
            raise Exception(
                f"Reserved chord for word {chord['word']} already used for {used[sorted_chord]['word']}"
            )
        used[sorted_chord] = chord

    print("Selecting chords")
    for chord in tqdm(chords):
        word = chord["word"].lower()
        if word in seen:
            duplicate.append(word)
            continue
        seen[word] = True
        if len(word) < config.min_word_length:
            continue
        reserved_chord = chord["reserved_chord"]
        if reserved_chord:
            continue
        for option in chord["options"]:
            sorted_chord = "".join(sorted(option["chord"]))
            if sorted_chord not in used:
                chord["chord"] = option["chord"]
                used[sorted_chord] = chord
                break

        if not chord["chord"]:
            no_options.append(word)

    if len(no_options) > 0:
        print(
            f"Unable to find any options for {len(no_options)} words: {', '.join(no_options)}"
        )
    if len(duplicate) > 0:
        print(f"Ignored {len(duplicate)} duplicate words: {', '.join(duplicate)}")

    print("Generating alts")
    alt_generator = AltGenerator(config)
    with ProcessPoolExecutor() as executor:
        chords = list(
            tqdm(
                executor.map(alt_generator.add_alt, chords, chunksize=10),
                total=len(chords),
            )
        )

    print(f"Writing {config.chords_file}")
    with open(config.chords_file, "w", newline="") as f:
        fieldnames = list(chords[0].keys())
        if "options" in fieldnames:
            fieldnames.remove("options")
        writer = csv.DictWriter(
            f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(chords)
