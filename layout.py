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


def get_layout_mapping(layout):
    finger_maping = """
    1234455678
    1234455678
    1234455678
    """
    layout_map = {}
    for i in range(0, len(layout)):
        layout_map[layout[i]] = finger_maping[i]
    return layout_map
