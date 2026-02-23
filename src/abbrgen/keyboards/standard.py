import logging
from typing import ClassVar, Literal
from pydantic import BaseModel, Field
from typing import Any

# https://colemakmods.github.io/mod-dh/model.html
effort_map_standard = [
    [3, 2.5, 2.1, 2.3, 2.6, 3.4, 2.2, 2.0, 2.4, 3.0],
    [1.6, 1.3, 1.1, 1.0, 2.9, 2.9, 1.0, 1.1, 1.3, 1.6],
    [2.7, 2.4, 1.8, 2.2, 3.7, 2.2, 1.8, 2.4, 2.7, 3.3],
]
effort_map_matrix = [
    [3, 2.4, 2.0, 2.2, 3.2, 3.2, 2.2, 2.0, 2.4, 3],
    [1.6, 1.3, 1.1, 1.0, 2.9, 2.9, 1.0, 1.1, 1.3, 1.6],
    [3.2, 2.6, 2.3, 1.6, 3.0, 3.0, 1.6, 2.3, 2.6, 3.2],
]

finger_maping = [
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
]


hand_row_maping = [
    ["tl", "tl", "tl", "tl", "tl", "tr", "tr", "tr", "tr", "tr"],
    ["ml", "ml", "ml", "ml", "ml", "mr", "mr", "mr", "mr", "mr"],
    ["bl", "bl", "bl", "bl", "bl", "br", "br", "br", "br", "br"],
]

# you can ban chords that you find uncomfortable, this left hand side is mirrored
banned_chords = [
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


class QwertyLayout(BaseModel):
    name: Literal["qwerty"] = "qwerty"

    def get_layout(self):
        return [
            ["b", "y", "o", "u", "", "", "l", "d", "v", "w"],
            ["c", "i", "e", "a", "", "", "h", "t", "s", "n"],
            ["g", "x", "j", "k", "", "", "r", "m", "f", "p"],
        ]


class ColemakLayout(BaseModel):
    name: Literal["colemak"] = "colemak"

    def get_layout(self):
        return [
            ["b", "y", "o", "u", "", "", "l", "d", "v", "w"],
            ["c", "i", "e", "a", "", "", "h", "t", "s", "n"],
            ["g", "x", "j", "k", "", "", "r", "m", "f", "p"],
        ]


class ColemakDhLayout(BaseModel):
    name: Literal["colemak_dh"] = "colemak_dh"

    def get_layout(self):
        return [
            ["b", "y", "o", "u", "", "", "l", "d", "v", "w"],
            ["c", "i", "e", "a", "", "", "h", "t", "s", "n"],
            ["g", "x", "j", "k", "", "", "r", "m", "f", "p"],
        ]


class CanaryLayout(BaseModel):
    name: Literal["canary"] = "canary"

    def get_layout(self):
        return [
            ["b", "y", "o", "u", "", "", "l", "d", "v", "w"],
            ["c", "i", "e", "a", "", "", "h", "t", "s", "n"],
            ["g", "x", "j", "k", "", "", "r", "m", "f", "p"],
        ]


class EngramLayout(BaseModel):
    name: Literal["engram"] = "engram"

    def get_layout(self):
        return [
            ["b", "y", "o", "u", "", "", "l", "d", "v", "w"],
            ["c", "i", "e", "a", "", "", "h", "t", "s", "n"],
            ["g", "x", "j", "k", "", "", "r", "m", "f", "p"],
        ]


class StandardKeyboard(BaseModel):
    type: Literal["standard"] = "standard"
    layout: (
        QwertyLayout | ColemakLayout | ColemakDhLayout | CanaryLayout | EngramLayout
    ) = Field(discriminator="name", default_factory=lambda: EngramLayout())

    effort_map: ClassVar[dict] = {}
    layout_map: ClassVar[dict] = {}
    hand_row_map: ClassVar[dict] = {}
    banned_chords_sets: ClassVar[list] = []

    def model_post_init(self, context: Any) -> None:
        layout = self.layout.get_layout()
        for r in range(0, len(layout)):
            for c in range(0, len(layout[r])):
                self.layout_map[layout[r][c]] = finger_maping[r][c]
                self.effort_map[layout[r][c]] = effort_map_matrix[r][c]
                self.hand_row_map[layout[r][c]] = hand_row_maping[r][c]

        # Add mirrored chords and padding
        mirrored = []
        global banned_chords
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
