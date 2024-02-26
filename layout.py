qwerty = """
qwertyuiop
asdfghjkl;
zxcvbnm,./
"""
colemak = """
qwfpgjluy;
arstdhneio
zxcvbkm,./
"""
colemak_dh = """
qwfpbjluy;
arstgmneio
zxcdvkh,./
"""
canary = """
wlypkzfou'
crstbxneia
qjvdgmh/,.
"""

finger_maping = """
1234455678
1234455678
1234455678
"""


def get_layout_mapping(layout):
    layout_map = {}
    for i in range(0, len(layout)):
        layout_map[layout[i]] = finger_maping[i]
    return layout_map
