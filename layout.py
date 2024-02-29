import logging

log = logging.getLogger("abbrgen")

qwerty = [
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"],
    ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
]
colemak = [
    ["q", "w", "f", "p", "g", "j", "l", "u", "y", ";"],
    ["a", "r", "s", "t", "d", "h", "n", "e", "i", "o"],
    ["z", "x", "c", "v", "b", "k", "m", ",", ".", "/"],
]
colemak_dh = [
    ["q", "w", "f", "p", "b", "j", "l", "u", "y", ";"],
    ["a", "r", "s", "t", "g", "m", "n", "e", "i", "o"],
    ["z", "x", "c", "d", "v", "k", "h", ",", ".", "/"],
]
canary = [
    ["w", "l", "y", "p", "b", "z", "f", "o", "u", "'"],
    ["c", "r", "s", "t", "g", "m", "n", "e", "i", "a"],
    ["q", "j", "v", "d", "k", "x", "h", ";", ",", "."],
]

finger_maping = [
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
]

hand_row_maping = [
    [-1, -1, -1, -1, -1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-2, -2, -2, -2, -2, 2, 2, 2, 2, 2],
]

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


class EffortCalculator:
    def __init__(self, layout, effort_map):
        self.layout = layout
        self.effort_map = effort_map
        self.layout_map = {}
        self.effort_map = {}
        self.hand_row_map = {}
        for r in range(0, len(layout)):
            for c in range(0, len(layout[r])):
                self.layout_map[layout[r][c]] = finger_maping[r][c]
                self.effort_map[layout[r][c]] = effort_map[r][c]
                self.hand_row_map[layout[r][c]] = hand_row_maping[r][c]

    def calculate(self, abbr, sfb_penalty, scissor_penalty, chorded_mode):
        result = 0
        if chorded_mode:
            seen = set()
            for char in abbr:
                if char in seen:
                    log.debug(
                        "rejected: duplicate letters not accepted in chorded mode"
                    )
                    return
                seen.add(char)

        for i in range(0, len(abbr)):
            if abbr[i] not in self.layout_map:
                log.debug(f"rejected: letter '{abbr[i]}' not in keyboard layout")
                return

        for i in range(0, len(abbr)):
            result += self.effort_map[abbr[i]]
            # check penalties
            if i < len(abbr) - 1:
                # sfb
                if self.layout_map[abbr[i]] == self.layout_map[abbr[i + 1]]:
                    if chorded_mode:
                        log.debug("rejected: SFBs not accepted in chorded mode")
                        return

                    log.debug("Applying SFB penalty")
                    result += sfb_penalty
                # scissor
                a = self.hand_row_map[abbr[i]]
                b = self.hand_row_map[abbr[i + 1]]
                if a != b:
                    if (a < 0 and b < 0) or (a > 0 and b > 0):
                        if chorded_mode:
                            log.debug("rejected: scissors not accepted in chorded mode")
                            return
                        log.debug("Applying scissor penalty")
                        result += scissor_penalty

        return result
