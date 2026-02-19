from abbrgen.keyboard import Keyboard


class StandardKeyboard(Keyboard):
    _layouts = {
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

    def __init__(self, layout: str) -> None:
        if layout not in self._layouts.keys():
            raise Exception("Unknown Layout")
        self._layout = layout

    def get_layouts(self) -> list[str]:
        return list(self._layouts.keys())
