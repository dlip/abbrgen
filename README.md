# abbrgen

Abbreviation generator to make writing common english words quicker.

There are many frequent words we type every day, this goal is to be able to type a letter eg. 't' followed by a trigger eg. ',;' and it will result in 'the ' being outputed.
The trigger just needs to be a character or two that is unique so you wouldn't type it normally.
The current approach uses [Espanso](https://espanso.org/) but it could be made to work with other text expander software.
There is software/programmable keyboards which allow you to bind multiple characters to a key so it becomes a single press.

The program reads a file of words listed by frequency eg. `words.txt` and generates a file that looks like the following:

[abbr.tsv](abbr.tsv)

| Word | Abbr | Alt1 | Alt2 | Alt3 |
| ---- | ---- | ---- | ---- | ---- |
| look | lo | looked | looking | looks |
| give | gi | given | giving | gives |

It also adds the past, continuing and plural version of each word. You can select the alt versions by adding extra character on the end of the word before the trigger. My alt suffixes are 'qjz', here is how I use it:

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

## Usage

If you just want to try it out you can [install Espanso](https://espanso.org/install/) and copy the file [abbr.yml](abbr.yml) to its match directory `~/.config/espanso/match/`

The `abbr.yml` file is very verbose, so if you want to add/update words I recommend reading on so you can edit `abbr.tsv` then generate the file again from that.

### Setup

#### Python

- Install [Python 3.11+](https://www.python.org/downloads/)
- Run `pip install -r requirements.txt`

#### Nix

If you have [Nix](https://nixos.org/download) you can run `nix develop` to get into a shell with Python and the required dependencies. If you have [direnv](https://direnv.net/docs/installation.html) also, you can run `direnv allow` instead to have the dependencies available as soon as you change to the directory.

#### Running

Clone the repo `git clone https://github.com/dlip/abbrgen.git` and change to the directory with `cd abbrgen`

To run the commands use `python <file>`

## Commands

### abbrgen.py

This reads `words.txt` and outputs abbreviations in tsv format to `abbr.tsv`. It also tries to add verb tenses with the data in `verbs-conjugations.json`, and plurals using [inflect](https://pypi.org/project/inflect/). Its not perfect, so if someone knows a better way please let me know.

I recommend changing the keyboard layout to whatever you use qwerty etc. Since it uses that to try to avoid abbreviations with "Same Finger Bigrams" (SFBs) which is pressing two keys with the same finger in succession.

```python
keyboard_layout = layout_canary
```

Here are some other settings you might want to change:

```python
# any word shorter than this will be excluded
min_chars = 3
# any percent improvement this will not be considered and the word might be excluded if there are no other options
min_improvement = 40
# the abbreviations will not end with any of these characters so you can use them as a suffix to access the alternate abbreviation forms
banned_suffixes = "qjz;,."
# avoid same finger bigrams (sequences which use the same key in a row)
avoid_sfb = True
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
