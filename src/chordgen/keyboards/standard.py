import logging
from typing import Literal
from pydantic import BaseModel
import copy

# https://colemakmods.github.io/mod-dh/model.html
EFFORT_MAP = {
    "row": [
        [3, 2.5, 2.1, 2.3, 2.6, 3.4, 2.2, 2.0, 2.4, 3.0],
        [1.6, 1.3, 1.1, 1.0, 2.9, 2.9, 1.0, 1.1, 1.3, 1.6],
        [2.7, 2.4, 1.8, 2.2, 3.7, 2.2, 1.8, 2.4, 2.7, 3.3],
    ],
    "column": [
        [3, 2.4, 2.0, 2.2, 3.2, 3.2, 2.2, 2.0, 2.4, 3],
        [1.6, 1.3, 1.1, 1.0, 2.9, 2.9, 1.0, 1.1, 1.3, 1.6],
        [3.2, 2.6, 2.3, 1.6, 3.0, 3.0, 1.6, 2.3, 2.6, 3.2],
    ],
}

FINGER_MAPPING = [
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
]


HAND_ROW_MAPPING = [
    ["tl", "tl", "tl", "tl", "tl", "tr", "tr", "tr", "tr", "tr"],
    ["ml", "ml", "ml", "ml", "ml", "mr", "mr", "mr", "mr", "mr"],
    ["bl", "bl", "bl", "bl", "bl", "br", "br", "br", "br", "br"],
]

LAYOUTS = {
    "qwerty": [
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
    ],
    "colemak": [
        ["q", "w", "f", "p", "g", "j", "l", "u", "y", ";"],
        ["a", "r", "s", "t", "d", "h", "n", "e", "i", "o"],
        ["z", "x", "c", "v", "b", "k", "m", ",", ".", "/"],
    ],
    "colemak_dh": [
        ["q", "w", "f", "p", "b", "j", "l", "u", "y", ";"],
        ["a", "r", "s", "t", "g", "m", "n", "e", "i", "o"],
        ["z", "x", "c", "d", "v", "k", "h", ",", ".", "/"],
    ],
    "canary": [
        ["w", "l", "y", "p", "b", "z", "f", "o", "u", "'"],
        ["c", "r", "s", "t", "g", "m", "n", "e", "i", "a"],
        ["q", "j", "v", "d", "k", "x", "h", ";", ",", "."],
    ],
    "engram": [
        ["b", "y", "o", "u", "", "", "l", "d", "v", "w"],
        ["c", "i", "e", "a", "", "", "h", "t", "s", "n"],
        ["g", "x", "j", "k", "", "", "r", "m", "f", "p"],
    ],
}


class StandardKeyboardOptions(BaseModel):
    layout: Literal[tuple(LAYOUTS.keys())] = "engram"
    stagger: Literal[tuple(EFFORT_MAP.keys())] = "column"
    scissor_penalty: int = 3
    same_column_combo_penalty: int = 2
    same_row_combo_penalty: int = 2

    def create(self):
        return StandardKeyboard(self)


class StandardKeyboard:
    def __init__(self, options: StandardKeyboardOptions) -> None:
        self._layout = LAYOUTS[options.layout]
        self._options = options

        # self._finger_map = {}
        self._effort_map = {}
        self._hand_row_map = {}
        self._banned_chords_sets = []
        self._combo_map = copy.deepcopy(self._layout)
        self._combo_lookup = {}

        for r in range(0, len(self._layout)):
            for c in range(0, len(self._layout[r])):
                # self._finger_map[self._layout[r][c]] = FINGER_MAPPING[r][c]
                self._effort_map[self._layout[r][c]] = EFFORT_MAP[
                    self._options.stagger
                ][r][c]
                self._hand_row_map[self._layout[r][c]] = HAND_ROW_MAPPING[r][c]
                self._combo_map[r][c] = 0
                self._combo_lookup[self._layout[r][c]] = (r, c)

        # Add mirrored chords and padding
        mirrored = []
        # banned chords, this left hand side is mirrored
        banned_chords = [
            [
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ],
            [
                [0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0],
            ],
            [
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
            ],
        ]
        padding = [0, 0, 0, 0, 0]
        for ban in banned_chords:
            mirror = []
            for r in range(0, len(ban)):
                mirror.append(padding + list(reversed(ban[r])))
                ban[r] += padding
            mirrored.append(mirror)
        banned_chords += mirrored

        for ban in banned_chords:
            s = set()
            for r in range(0, len(ban)):
                for c in range(0, len(ban[r])):
                    if ban[r][c]:
                        s.add(self._layout[r][c])
            self._banned_chords_sets.append(s)

    def get_scissor_count(self, abbr):
        result = 0
        indexes = {
            "tl": 0,
            "ml": 0,
            "bl": 0,
            "tr": 0,
            "mr": 0,
            "br": 0,
        }
        for i in range(0, len(abbr)):
            indexes[self._hand_row_map[abbr[i]]] += 1

        if indexes["tl"] and indexes["bl"]:
            result += min(indexes["tl"], indexes["bl"])

        if indexes["tr"] and indexes["br"]:
            result += min(indexes["tr"], indexes["br"])

        return result

    # def get_sfb_count(self, abbr):
    #     result = 0
    #     indexes = {}
    #     for i in range(0, len(abbr)):
    #         index = self._finger_map[abbr[i]]
    #         if index not in indexes:
    #             indexes[index] = 1
    #         else:
    #             indexes[index] += 1
    #     for x in indexes.values():
    #         if x > 1:
    #             result += x - 1
    #
    #     return result

    def get_combo_map(self, abbr: str):
        map = copy.deepcopy(self._combo_map)
        for c in abbr:
            offset = self._combo_lookup[c]
            map[offset[0]][offset[1]] = 1
        return map

    def get_same_column_combo(self, combo_map) -> int:
        count = 0
        for i in range(0, len(combo_map[0])):
            if combo_map[0][i] and combo_map[1][i]:
                if self._options.same_column_combo_penalty == -1:
                    return -1

                count += 1

            # Top and bottom row on same finger is excluded
            if combo_map[0][i] and combo_map[2][i]:
                return -1

        return count

    def get_same_row_combo(self, combo_map) -> int:
        count = 0
        for r in range(0, len(combo_map)):
            for c in range(0, len(combo_map[r]) - 1):
                if (
                    combo_map[r][c]
                    and combo_map[r][c + 1]
                    and FINGER_MAPPING[r][c] == FINGER_MAPPING[r][c + 1]
                ):
                    if self._options.same_row_combo_penalty == -1:
                        return -1
                    count += 1

        return count

    def score(self, abbr: str) -> int:
        for i in range(0, len(abbr)):
            if abbr[i] not in self._effort_map:
                logging.debug(f"rejected: letter '{abbr[i]}' not in keyboard layout")
                return -1

        seen = set()
        for char in abbr:
            if char in seen:
                logging.debug("rejected: duplicate letters")
                return -1
            seen.add(char)

        for ban in self._banned_chords_sets:
            if ban.issubset(seen):
                logging.debug("rejected: banned chord")
                return -1

        # sfb_count = self.get_sfb_count(abbr)
        # if sfb_count:
        #     logging.debug("rejected: SFBs")
        #     return -1

        combo_map = self.get_combo_map(abbr)
        result = 0
        same_column_combo = self.get_same_column_combo(combo_map)
        if same_column_combo == -1:
            logging.debug("rejected: same column combo")
            return -1

        result += same_column_combo * self._options.same_column_combo_penalty

        same_row_combo = self.get_same_row_combo(combo_map)
        if same_row_combo == -1:
            logging.debug("rejected: same column combo")
            return -1

        result += same_row_combo * self._options.same_row_combo_penalty

        scissor_count = self.get_scissor_count(abbr)
        if scissor_count:
            if self._options.scissor_penalty == -1:
                logging.debug("rejected: scissor")
                return -1
            result += self._options.scissor_penalty * scissor_count

        for i in range(0, len(abbr)):
            result += self._effort_map[abbr[i]]

        return result
