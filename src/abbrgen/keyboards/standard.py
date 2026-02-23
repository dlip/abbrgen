import logging
from typing import ClassVar, Literal
from pydantic import BaseModel, Field
from typing import Any

# https://colemakmods.github.io/mod-dh/model.html
EFFORT_MAP_STANDARD = [
    [3, 2.5, 2.1, 2.3, 2.6, 3.4, 2.2, 2.0, 2.4, 3.0],
    [1.6, 1.3, 1.1, 1.0, 2.9, 2.9, 1.0, 1.1, 1.3, 1.6],
    [2.7, 2.4, 1.8, 2.2, 3.7, 2.2, 1.8, 2.4, 2.7, 3.3],
]
EFFORT_MAP_MATRIX = [
    [3, 2.4, 2.0, 2.2, 3.2, 3.2, 2.2, 2.0, 2.4, 3],
    [1.6, 1.3, 1.1, 1.0, 2.9, 2.9, 1.0, 1.1, 1.3, 1.6],
    [3.2, 2.6, 2.3, 1.6, 3.0, 3.0, 1.6, 2.3, 2.6, 3.2],
]

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

# you can ban chords that you find uncomfortable, this left hand side is mirrored
BANNED_CHORDS = [
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0],
    ],
    [
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ],
    [
        [1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ],
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


class StandardKeyboard(BaseModel):
    type: Literal["standard"] = "standard"
    layout: Literal[tuple(LAYOUTS.keys())] = "engram"
    effort_map: ClassVar[dict] = {}
    layout_map: ClassVar[dict] = {}
    hand_row_map: ClassVar[dict] = {}
    banned_chords_sets: ClassVar[list] = []

    def model_post_init(self, context: Any) -> None:
        layout = LAYOUTS[self.layout]
        for r in range(0, len(layout)):
            for c in range(0, len(layout[r])):
                self.layout_map[layout[r][c]] = FINGER_MAPPING[r][c]
                self.effort_map[layout[r][c]] = EFFORT_MAP_MATRIX[r][c]
                self.hand_row_map[layout[r][c]] = HAND_ROW_MAPPING[r][c]

        # Add mirrored chords and padding
        mirrored = []
        global BANNED_CHORDS
        padding = [0, 0, 0, 0, 0]
        for ban in BANNED_CHORDS:
            mirror = []
            for r in range(0, len(ban)):
                mirror.append(padding + list(reversed(ban[r])))
                ban[r] += padding
            mirrored.append(mirror)
        BANNED_CHORDS += mirrored

        for ban in BANNED_CHORDS:
            s = set()
            for r in range(0, len(ban)):
                for c in range(0, len(ban[r])):
                    if ban[r][c]:
                        s.add(layout[r][c])
            self.banned_chords_sets.append(s)

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
            indexes[self.hand_row_map[abbr[i]]] += 1

        if indexes["tl"] and indexes["bl"]:
            result += min(indexes["tl"], indexes["bl"])

        if indexes["tr"] and indexes["br"]:
            result += min(indexes["tr"], indexes["br"])

        return result

    def get_sfb_count(self, abbr):
        result = 0
        indexes = {}
        for i in range(0, len(abbr)):
            index = self.layout_map[abbr[i]]
            if index not in indexes:
                indexes[index] = 1
            else:
                indexes[index] += 1
        for x in indexes.values():
            if x > 1:
                result += x - 1

        return result

    def score(self, abbr: str) -> int:
        for i in range(0, len(abbr)):
            if abbr[i] not in self.layout_map:
                logging.debug(f"rejected: letter '{abbr[i]}' not in keyboard layout")
                return -1

        scissor_count = self.get_scissor_count(abbr)
        sfb_count = self.get_sfb_count(abbr)
        seen = set()
        for char in abbr:
            if char in seen:
                logging.debug("rejected: duplicate letters")
                return -1
            seen.add(char)

        for ban in self.banned_chords_sets:
            if ban.issubset(seen):
                logging.debug("rejected: banned chord")
                return -1

        if scissor_count:
            logging.debug("rejected: scissor")
            return -1

        if sfb_count:
            logging.debug("rejected: SFBs")
            return -1

        result = 0
        for i in range(0, len(abbr)):
            result += self.effort_map[abbr[i]]

        return result
