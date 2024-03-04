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

### Chording Pros and Cons

- Quicker since the time taken is about the same as a single key press
- Can take time to get used to pressing multiple keys together
- Heavier on the fingers especially if you have heavy key switches

### Text Expansion Pros and Cons

- More possible combinations since you can use abbreviations that reverse and repeat letters
- Easier to set up with a standard keyboard
- Can be buggy with some programs due to the way it replaces text
- Can be a security issue at work since it captures key presses and might need administrator privilages to install

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

This is how I have set up my 4 key thumb cluster from left to right:

- alt1 (normally tab on tap or my navigation/number/symbol layer on hold, with hold preferred setting)
- alt2 (normally space on tap or my media/function layer on hold, with tap preferred setting)
- shift (normally backspace on tap or shift on hold, with hold preferred setting)
- combo (normally delete word, this is great when making mistakes while learning)

### Text Expansion

The approach it takes with text expansion is to define a trigger which you type after the abbreviation. The default trigger is `,;`. Read below about setting up a trigger key so you can automate typing this on one key. Alternate versions and punctuation is accessed by adding an extra suffix after the abbreviation.

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

You can check my config [here](https://github.com/dlip/qmk_firmware/tree/dlip/keyboards/mushi/keymaps/dlip) for reference

- Setup combos as per this [gboards guide](https://combos.gboards.ca/docs/install/)
- Add definitions for KC_COMBO, KC_COMBO_SFT, KC_COMBO_ALT1, KC_COMBO_ALT2 thumb keys to your `keymap.c`. Feel free to change the actions here to whatever works for you. If you have other special keys on your letters eg. home row mods, add definitions for these also so they can be referred to in the script. Use these in your keymap.
- Move the `#include "g/keymap_combo.h"` line below all your definitions

```
// Other definitions

#define KC_COMBO_ALT1 LT(1, KC_TAB)
#define KC_COMBO_ALT2 LT(2, KC_SPC)
#define KC_COMBO_SFT MT(MOD_LSFT, KC_BSPC)
#define KC_COMBO C(KC_BSPC)

#include "g/keymap_combo.h"
```

- Open [qmk-chorded.py](qmk-chorded.py) and ensure `key_map` matches any other custom definitions you may have
- Run `python qmk-chorded.py`
- It will generate `abbr.def` which you need to copy to your QMK keymap directory
- Add `#include "abbr.def"` to the top of your QMK `combos.def` file
- Flash your keyboard

### zmk-chorded.py

This is a chorded importer for [ZMK](https://zmk.dev/) which is a firmware for custom keyboards.

You can check my config [here](https://github.com/dlip/zmk-sweep/blob/main/config/cradio.keymap) for reference

- Open [zmk-chorded.py](zmk-chorded.py) and ensure `key_positions` matches all the key positions on your keyboard
- Run `python zmk-chorded.py`
- It will generate `macros.dtsi` and `combos.dtsi` which you can then copy to your zmk keymap directory
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

### kanata-chorded.py

This is a chorded importer for [Kanata](https://github.com/jtroo/kanata) which is a software keyboard remapper.

Be aware that many keyboards, especially laptop ones do not support having many keys held at the same time. You can check what combinations work for your one [here](https://www.mechanical-keyboard.org/key-rollover-test/)

- Open [kanata-chorded.py](kanata-chorded.py) and customize the `output` with your base mappings
- Run `python kanata-chorded.py` and copy [abbr.kbd](./abbr.kbd) to your keymap directory
- Copy from the example [canary-chorded.kbd](./canary-chorded.kbd) and update your keymap
  - Add `(include abbr.kbd)
`
  - Add the `defalias` references to the `combos` chords
  - Include all the references in your base layer using the `@` symbol
- Run `sudo kanata -c <keymap.kbd>`

### espanso-text-expansion.py

This is a text expansion importer for [Espanso](https://espanso.org)

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

### Setting up a trigger key for text expansion

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
