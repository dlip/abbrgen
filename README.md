# abbrgen

Abbreviation generator for chording and text expansion

Every day, we find ourselves typing commonly used words repetitively, consuming time and effort. Text expansion offers a solution by allowing us to replace these frequently used words with unique abbreviations, thereby saving keystrokes. For instance, typing 't' with a trigger key could automatically generate 'the '. The objective isn't to abbreviate every word, but rather to focus on those that offer significant savings for the effort invested in memorization. Ideally you also want the abbreviations to be the most comfortable effort wise for your particular keyboard layout (qwerty, colemak, canary etc).

However, compiling such a list manually can be a daunting task. This is where abbrgen comes in handy, it helps by automating the generation of the initial list and streamlines the process of importing them into different tools, so you can enhance and customize them over time.

Given a list of common words it can generate a list like the following, the way you input each word and alternate word depends on if you are using chording or text expansion

| Word | Abbreviation | Alt1   | Alt2    | Alt3  |
| ---- | ------------ | ------ | ------- | ----- |
| look | l            | looked | looking | looks |
| give | ge           | given  | giving  | gives |

## Chording vs text expansion

Chording involves pressing multiple keys at the same time, while text expansion is typing as usual followed by a trigger key. There are pros and cons of each approach to consider:

- Chording is quicker since the time taken is about the same as a single key press
- Text expansion can feel more natural in the flow of typing other words
- Chording can be heaver on the fingers especially if you have heavy key switches
- There are more possible combinations with text expansion since you can use abbreviatons that repeat letters
- Text expansion is easier to setup with a standard keyboard

### Chording

The approach it takes with combos is to define combo, shift, and alt1/2 keys that are pressed in combination with the abbreviation to get the desired output. These keys work well on the thumbs to ensure all the abbreviations are possible to press with them. There are some extra combos to help with punctuation.

| Input                           | Output                  |
| ------------------------------- | ----------------------- |
| l + combo                       | look`<space>`           |
| l + combo + shift               | Look`<space>`           |
| l + combo + alt1                | looked`<space>`         |
| l + combo + alt2                | looking`<space>`        |
| l + combo + alt1 + alt2         | looks`<space>`          |
| l + combo + shift + alt1 + alt2 | Looks`<space>`          |
| . + combo                       | `<backspace>`.`<space>` |
| , + combo                       | `<backspace>`,`<space>` |
| ; + combo                       | `<backspace>`;`<space>` |

### Text Expansion

The approach it takes with text expansion is to define a trigger which you type after the abbreviation. The default trigger is ',;'. Read below about setting up a trigger key so you can automate typing this on one key. Alternate versions and punctuation is accessed by adding an extra suffix after the abbreviation.

| Input         | Output           |
| ------------- | ---------------- |
| l`<trigger>`  | look`<space>`    |
| lq`<trigger>` | looked`<space>`  |
| lj`<trigger>` | looking`<space>` |
| lz`<trigger>` | looks`<space>`   |
| L`<trigger>`  | Look`<space>`    |
| L.`<trigger>` | Look.`<space>`   |
| L,`<trigger>` | Look,`<space>`   |
| L;`<trigger>` | Look;`<space>`   |

## Setup

Clone the repo `git clone https://github.com/dlip/abbrgen.git` and change to the directory with `cd abbrgen`

### Python

- Install [Python 3.11+](https://www.python.org/downloads/)
- Run `pip install -r requirements.txt`

### Nix (Alternative to Python setup)

If you have [Nix](https://nixos.org/download) you can run `nix develop` to get into a shell with Python and the required dependencies. If you have [direnv](https://direnv.net/docs/installation.html) also, you can run `direnv allow` instead to have the dependencies available as soon as you change to the directory.

### Running

To run the commands use `python <file.py>`

## Commands

### abbrgen.py

This reads `words.txt` and outputs abbreviations in tsv format to `abbr.tsv`:

The approach it uses is:

- Generate all combinations of the letters in the word which start with the first letter and keep the order from left to right
- Reject abbreviations it has already used
- Reject abbreviations that are shorter than a minimum amount of characters or don't provide a minimum percentage improvement over typing the full word
- Score remaining abbreviations by effort and select the best option depending on your particular keyboard layout and if you are using chorded mode
- Add verb tenses with the data in `verbs-conjugations.json`
- Add plurals using [inflect](https://pypi.org/project/inflect/)

There are some options that you might want to change near the top of [abbrgen.py](abbrgen.py). In particular set `chorded_mode` to `True` or `False` depending on what method you are using.

### training.py

This generates a [training.txt](training.txt) file from `abbr.tsv` for you to copy a line of 10 words at a time into a typing practice tool like [Monkeytype](https://monkeytype.com/) custom mode to help learn the abbreviations:

```
the and you have that for with this not but
t   a   y   h    th   f   w    ti   n   b
```

### qmk-chorded.py

This is a chorded importer for [QMK](https://qmk.fm) which is a firmware for custom keyboards.

#### Setup

- Setup combos as per this [gboards guide](https://combos.gboards.ca/docs/install/)
- Add definitions for KC_COMBO, KC_COMBO_SFT, KC_COMBO_ALT1, KC_COMBO_ALT2, and your other thumb keys to your `keymap.c`
- Move the `#include "g/keymap_combo.h"` line below all your definitions

```
enum custom_keycodes {
    KC_COMBO = SAFE_RANGE,
};

// Other definitions

#define KC_SFT_BSPC MT(MOD_LSFT, KC_BSPC)
#define KC_NNM_TAB LT(1, KC_TAB)
#define KC_MED_SPC LT(2, KC_SPC)

#define KC_COMBO_SFT KC_SFT_BSPC
#define KC_COMBO_ALT1 KC_NNM_TAB
#define KC_COMBO_ALT2 KC_MED_SPC

#include "g/keymap_combo.h"
```

- Add the definitions to your thumb keys in the keymap

```
KC_NNM_TAB, KC_MED_SPC, KC_SFT_BSPC, KC_COMBO,
```

- Add the following to your `combos.def`. It includes shortcuts for punctuation eg. combo + dot will backspace then add dot plus space for the start of a new sentence. If you have mod tap keys you will have to add a definition for it and change it eg. `KC_S` to `KC_GUI_S`. It also includes `abbr.def` which you will generate next

```
#include "abbr.def"

// Punctuation
SUBS(dot, SS_TAP(X_BSPC)". ", KC_COMBO, KC_DOT)
SUBS(comma, SS_TAP(X_BSPC)", ", KC_COMBO, KC_COMMA)
SUBS(scln, SS_TAP(X_BSPC)"; ", KC_COMBO, KC_SCLN)
SUBS(quot, SS_TAP(X_BSPC)"' ", KC_COMBO, KC_QUOT)
SUBS(quotS, SS_TAP(X_BSPC)"\" ", KC_COMBO, KC_COMBO_SFT, KC_QUOT)
SUBS(appve, SS_TAP(X_BSPC)"'ve ", KC_COMBO, KC_QUOT, KC_V)
SUBS(apps, SS_TAP(X_BSPC)"'s ", KC_COMBO, KC_QUOT, KC_S)
SUBS(appnt, SS_TAP(X_BSPC)"n't ", KC_COMBO, KC_QUOT, KC_T)
```

- Open [qmk-chorded.py](qmk-chorded.py) and ensure `key_map` matches any other custom definitions you may have
- Run `python qmk-chorded.py`
- It will generate `abbr.def` which you can then copy to your qmk keymap folder
- Flash your keyboard

### zmk-chorded.py

This is a chorded importer for [ZMK](https://zmk.dev/) which is a firmware for custom keyboards.

- Open [zmk-chorded.py](zmk-chorded.py) and ensure `key_positions` matches all the key positions on your keyboard
- Run `python zmk-chorded.py`
- It will generate `macros.dtsi` and `combos.dtsi` which you can then copy to your zmk keymap folder
- Include these lines in your zmk keymap keymap file

```
  macros {
    #include "macros.dtsi"
  };

  combos {
    compatible = "zmk,combos";
    #include "combos.dtsi"
  };
```

- Include these lines in your zmk keymap conf file, you may have to increase `CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY` if you are able to fit more combos on your controller

```
CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY=512
CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO=10
CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=10
```

- Flash your keyboard

### espanso-text-expansion.py

This is a text expansion importer for [Espanso](https://espanso.org)

- Have a look at [abbr.tsv](abbr.tsv) to see the the second column for the abbrevation
- For example typing `l,;` will output 'look '

You can access the alt versions of a word by adding a suffix on the end of the word before the trigger. The default suffixes are 'qjz', here is how you can use it:

| Input | Output  |
| ----- | ------- |
| l     | look    |
| lq    | looked  |
| lj    | looking |
| lz    | looks   |

Other features are auto capitalization and suffixes for punctuation characters '.,;' so you don't have to backspace to remove the automatic spacing then add the punctuation:

| Input | Output |
| ----- | ------ |
| L     | Look   |
| L.    | Look.  |
| L,    | Look,  |
| L;    | Look;  |

It reads `abbr.tsv` and generates `abbr.yml` which you can then copy to `~/.config/espanso/match/`. The yaml file is quite verbose since it adds multiple matches for all the possible suffixes, so you'll probably want to make any changes to `abbr.tsv` then run this command again.

Here are some settings you might want to change:

```python
# suffix to add to the end of an abbreviation to trigger the expansion
expand_trigger = ",;"
# suffix to add before the trigger to use the alternate forms in `abbr.tsv`
alt_suffix_1 = "q"
alt_suffix_2 = "j"
alt_suffix_3 = "z"
```

It might be preferable to disable `undo_backspace` in `~/.config/espanso/config/default.yml` in case you want to backspace without loosing the whole word

```
undo_backspace: false
```

The `abbr.yml` file is very verbose, so if you want to add/update words I recommend reading on so you can edit `abbr.tsv` then generate the file again from that.

### Setting up a trigger key

Having to type 2 characters eg. ',;' reduces the improvement gain considerably, especially for shorter words. You can bind a key on your keyboard that you don't usually use eg. right alt, caps lock via softwarwe or programmable keyboard firmware

#### Kanata (software)

Install [Kanata](https://github.com/jtroo/kanata) and add this alias to your config. You and then bind `@tgr` to a key of your choosing.

```
(defalias
  tgr (macro , ;)
)
```

#### ZMK (firmware)

Add this macro to your config, then you can bind `&tgr` to a key

```
  macros {
    ZMK_MACRO (tgr,
      wait-ms = <30>;
      tap-ms = <40>;
      bindings = <&kp COMMA &kp SEMI>;
    )
  };
```

#### QMK (firmware)

Add this custom keycode to your config, then you can bind `TGR` to a key

```
enum custom_keycodes {
    TGR = SAFE_RANGE,
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
    case TGR:
        if (record->event.pressed) {
            SEND_STRING(",;");
        }
        break;
    }
    return true;
};
```

## Credits

- [English frequency list](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Contemporary_fiction)
- [Verb conjugations](https://github.com/Drulac/English-Verbs-Conjugates/blob/master/verbs-conjugations.json)
- [inflect](https://pypi.org/project/inflect/)
