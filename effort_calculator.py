import logging

log = logging.getLogger("abbrgen")

finger_maping = [
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
    [1, 2, 3, 4, 4, 5, 5, 6, 7, 8],
]

hand_row_maping = [
    ["tl", "tl", "tl", "tl", "tl", "tr", "tr", "tr", "tr", "tr"],
    ["ml", "ml", "ml", "ml", "ml", "mr", "mr", "mr", "mr", "mr"],
    ["bl", "bl", "bl", "bl", "bl", "br", "br", "br", "br", "br"],
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
        self.banned_chords_sets = []

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

    def calculate(self, abbr, sfb_penalty, scissor_penalty, chorded_mode):
        for i in range(0, len(abbr)):
            if abbr[i] not in self.layout_map:
                log.debug(f"rejected: letter '{abbr[i]}' not in keyboard layout")
                return

        scissor_count = self.get_scissor_count(abbr)
        sfb_count = self.get_sfb_count(abbr)
        if chorded_mode:
            seen = set()
            for char in abbr:
                if char in seen:
                    log.debug(
                        "rejected: duplicate letters not accepted in chorded mode"
                    )
                    return
                seen.add(char)

            for ban in self.banned_chords_sets:
                if ban.issubset(seen):
                    log.debug("rejected: banned chord")
                    return

            # if scissor_count:
            #     log.debug("rejected: scissors not accepted in chorded mode")
            #     return

            if sfb_count:
                log.debug("rejected: SFBs not accepted in chorded mode")
                return

        result = 0
        for i in range(0, len(abbr)):
            result += self.effort_map[abbr[i]]

        if scissor_count:
            log.debug("Applying scissor penalty")
            result += scissor_count * scissor_penalty

        if not chorded_mode:
            if sfb_count:
                log.debug("Applying SFB penalty")
                result += sfb_count * sfb_penalty

        return result
