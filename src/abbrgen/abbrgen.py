import csv
import logging
import os
from itertools import count
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from abbrgen.keyboard import Keyboard
from abbrgen.standard_keyboard import StandardKeyboard


from .utils import find_combinations


def compute(line: tuple[int, tuple[str, str]], keyboard: Keyboard) -> str:
    combinations = find_combinations(line[1][0])
    scores = [keyboard.score(combination) for combination in combinations]
    return f"{line[0]}: {line[1][0].upper()} : {combinations} : {scores}"


def file_with_line_numbers(f):
    for i, line in zip(count(1), f):
        yield (i, line)


def abbrgen() -> None:
    logging.basicConfig(level="DEBUG")
    keyboard = StandardKeyboard("engram")
    with open("words.tsv") as file:
        file = csv.reader(file, delimiter="\t")

        alt_data = {}
        if os.path.isfile("alt.tsv"):
            logging.debug("loading alt.tsv")
            with open("alt.tsv") as alt_file:
                alt_file = csv.reader(alt_file, delimiter="\t")
                for line in alt_file:
                    if line:
                        alt_data[line[0]] = line[1:]
        lines = list(file_with_line_numbers(file))
        logging.info("Finding combinations")
        with ProcessPoolExecutor() as executor:
            results = list(
                tqdm(
                    executor.map(compute, lines, [keyboard], chunksize=10),
                    total=len(lines),
                )
            )
            print(results[0])
