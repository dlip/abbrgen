# abbrgen

Abbreviation generator for chording and text expansion

Every day, we find ourselves typing commonly used words repetitively, consuming time and effort. Text expansion offers a solution by allowing us to replace these frequently used words with unique abbreviations, thereby saving keystrokes. For instance, typing 't' with a trigger key could automatically generate 'the '. The objective isn't to abbreviate every word, but rather to focus on those that offer significant savings for the effort invested in memorization.

However, compiling such a list manually can be a daunting task. This is where abbrgen comes in handy, it helps by automating the generation of the initial list and streamlines the process of importing them into different tools, so you can enhance and customize them over time.

## Chording vs text expansion

Chording involves pressing multiple keys at the same time, while text expansion is typing as usual followed by a trigger key. There are pros and cons of each approach to consider:

- Chording is quicker since the time taken is about the same as a single key press
- Text expansion can feel more natural in the flow of typing other words
- Chording can be heaver on the fingers especially if you have heavy key switches
- There are more possible combinations with text expansion since you can use abbreviatons that repeat letters

## Setup

### Python

- Install [Python 3.11+](https://www.python.org/downloads/)
- Run `pip install -r requirements.txt`

### Nix (Alternative to Python setup)

If you have [Nix](https://nixos.org/download) you can run `nix develop` to get into a shell with Python and the required dependencies. If you have [direnv](https://direnv.net/docs/installation.html) also, you can run `direnv allow` instead to have the dependencies available as soon as you change to the directory.

### Running

Clone the repo `git clone https://github.com/dlip/abbrgen.git` and change to the directory with `cd abbrgen`

To run the commands use `python <file.py>`

## Commands

### abbrgen.py

This reads `words.txt` and outputs abbreviations in tsv format to `abbr.tsv`:

| Word | Abbr | Alt1   | Alt2    | Alt3  |
| ---- | ---- | ------ | ------- | ----- |
| look | l    | looked | looking | looks |
| give | ge   | given  | giving  | gives |

The approach it uses is:

- Generate all combinations of the letters in the word which start with the first letter and keep the order from left to right
- Reject abbreviations it has already used
- Reject abbreviations that are shorter than a minimum amount of characters or don't provide a minimum percentage improvement over typing the full word
- Score remaining abbreviations by effort and select the best option
- Add verb tenses with the data in `verbs-conjugations.json`
- Add plurals using [inflect](https://pypi.org/project/inflect/)

There are some options that you might want to change near the top of [abbrgen.py](abbrgen.py). In particular set `chorded_mode` to `True` or `False` depending on what method you are using.

### training.py

This generates a [training.txt](training.txt) file from `abbr.tsv` for you to copy a line of 10 words at a time into a typing practice tool like [Monkeytype](https://monkeytype.com/) custom mode to help learn the abbreviations:

```
the and you have that for with this not but
t   a   y   h    th   f   w    ti   n   b
```

### espanso.py

This is a text expansion importer for [Espanso](https://espanso.org)

- The default trigger is ',;'. Read below about setting up a trigger key so you can automate typing this on one key
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

### WIP qmk-chording.py

Chorded importer for QMK

## Credits

- [English frequency list](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Contemporary_fiction)
- [Verb conjugations](https://github.com/Drulac/English-Verbs-Conjugates/blob/master/verbs-conjugations.json)
- [inflect](https://pypi.org/project/inflect/)
