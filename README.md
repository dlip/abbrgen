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

There is also a training file generated which you can copy a line of 10 words at a time into a typing practice tool like [Monkeytype](https://monkeytype.com/) custom mode to help learn the abbreviations:

[training.txt](training.txt)

```
the and you have that for with this not but
t   a   y   h    th   f   w    ti   n   b
```

## Usage

If you just want to try it out you can [install Espanso](https://espanso.org/install/) and copy the file [abbr.yml](abbr.yml) to its match directory `~/.config/espanso/match/`

If you want to add/update words, the `abbr.yml` file is very verbose so I recommend reading on so you can edit `abbr.tsv` then generate the file again from that.
