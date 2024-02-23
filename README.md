# abbrgen

Abbreviation generator for [Espanso](https://espanso.org/)

There are many frequent words we type repeatedly every day, using text expansion we can save keystrokes by shortening these to unique abbreviations so we might type 't' followed by a trigger key and it will result in 'the ' being outputed. The goal here isn't to have abbreviations for every word, just ones with a high return for the effort it takes to memorize them. When creating a list like this, it can be very time consuming so you can use this to help to automate at least the initial file you can improve on.

## Usage

- [Install Espanso](https://espanso.org/install/)
- Copy the file [abbr.yml](abbr.yml) to its match directory `~/.config/espanso/match/`
- The default trigger is ',;'. Read below about setting up a trigger key so you can automate typing this on one key
- Have a look at [abbr.tsv](abbr.tsv) to see the the second column for the abbrevation
- Try typing `lo,;` to output 'look '

| Word | Abbr | Alt1 | Alt2 | Alt3 |
| ---- | ---- | ---- | ---- | ---- |
| look | lo | looked | looking | looks |
| give | gi | given | giving | gives |

You can access the alt versions of a word by adding a suffix on the end of the word before the trigger. The default suffixes are 'qjz', here is how you can use it:

| Input | Output |
| ----- | ------ |
| lo    | look   |
| loq   | looked |
| loj   | looking |
| loz   | looks  |

Other features are auto capitalization and suffixes for punctuation characters '.,;' so you don't have to backspace to remove the automatic spacing then add the punctuation:

| Input | Output |
| ----- | ------ |
| Lo    | Look   |
| Lo.   | Look.  |
| Lo,   | Look,  |
| Lo;   | Look;  |

It might be preferable to disable `undo_backspace` in `~/.config/espanso/config/default.yml` in case you want to backspace without loosing the whole word

```
undo_backspace: false
```

The `abbr.yml` file is very verbose, so if you want to add/update words I recommend reading on so you can edit `abbr.tsv` then generate the file again from that.

### Setup

#### Python

- Install [Python 3.11+](https://www.python.org/downloads/)
- Run `pip install -r requirements.txt`

#### Nix (Alternative to Python setup)

If you have [Nix](https://nixos.org/download) you can run `nix develop` to get into a shell with Python and the required dependencies. If you have [direnv](https://direnv.net/docs/installation.html) also, you can run `direnv allow` instead to have the dependencies available as soon as you change to the directory.

#### Running

Clone the repo `git clone https://github.com/dlip/abbrgen.git` and change to the directory with `cd abbrgen`

To run the commands use `python <file.py>`

## Commands

### abbrgen.py

This reads `words.txt` and outputs abbreviations in tsv format to `abbr.tsv`. The approach it uses is:

- Read word frequency list `words.txt`
- Generate all combinations of the letters in the word which start with the first letter and keep the order from left to right
- Reject abbreviations it has already used
- Reject abbreviations that are shorter than a minimum amount of characters or don't provide a minimum percentage improvement over typing the full word
- Add verb tenses with the data in `verbs-conjugations.json`
- Add plurals using [inflect](https://pypi.org/project/inflect/)
- Try to avoid abbreviations which involve "Same Finger Bigrams" (SFBs) which is pressing two keys with the same finger in succession
- Outputs the result in tsv format to `abbr.tsv`

I recommend changing the keyboard layout to ensure the SFBs feature works for you

Here are some other settings you might want to change in [abbrgen.py](abbrgen.py):

```python
# stop after processing this many lines in words.txt
limit = 0
# any word shorter than this will be excluded
min_chars = 3
# any percent improvement below this will not be considered and the word might be excluded if there are no other options
min_improvement = 40
# the abbreviations will not end with any of these characters so you can use them as a suffix to access the alternate abbreviation forms
banned_suffixes = "qjz;,."
# output the words with no abbreviation found so you can add them by hand
output_all = False
# avoid same finger bigrams (sequences which use the same key in a row)
avoid_sfb = True
# change this to your keyboard layout to avoid sfbs, ensure its listed above
keyboard_layout = layout_canary
```

### espanso.py

Reads `abbr.tsv` and generates `abbr.yml` which you can then copy to `~/.config/espanso/match/`. The yaml file is quite verbose since it adds multiple matches for all the possible suffixes, so you'll probably want to make any changes to `abbr.tsv` then run this command again.

Here are some settings you might want to change:

```python
# suffix to add to the end of an abbreviation to trigger the expansion
expand_trigger = ",;"
# suffix to add before the trigger to use the alternate forms in `abbr.tsv`
alt_suffix_1 = "q"
alt_suffix_2 = "j"
alt_suffix_3 = "z"
```

### training.py

This generates a [training.txt](training.txt) file generated which you can copy a line of 10 words at a time into a typing practice tool like [Monkeytype](https://monkeytype.com/) custom mode to help learn the abbreviations:

```
the and you have that for with this not but
t   a   y   h    th   f   w    ti   n   b
```

## Setting up a trigger key

Having to type 2 characters eg. ',;' reduces the improvement gain considerably, especially for shorter words. You can bind a key on your keyboard that you don't usually use eg. right alt, caps lock via softwarwe or programmable keyboard firmware

### Kanata (software)

Install [Kanata](https://github.com/jtroo/kanata) and add this alias to your config. You and then bind `@tgr` to a key of your choosing.

```
(defalias
  tgr (macro , ;)
)
```

### ZMK (firmware)

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

### QMK (firmware)

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

- [English frequency list](https://github.com/frekwencja/most-common-words-multilingual/blob/main/data/wordfrequency.info/en.txt)
- [Verb conjugations](https://github.com/Drulac/English-Verbs-Conjugates/blob/master/verbs-conjugations.json)
- [inflect](https://pypi.org/project/inflect/)
