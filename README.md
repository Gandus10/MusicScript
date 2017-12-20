# MusicScript

Program who convert text to music.

## Functionality
- function note, ex : DO
- loop to play a note several times or a note sequence, ex : loop(10){...}
- function silence, ex : silence = 12
- assign track to var to be reused

## Input/Output
- Input = text file (.mus)
- Output = MIDI file (.mid)

## Example
- text file :

```
track (
    VIOLIN;
    SOL;
    DO
);

track (
    tempo = 29;
    DO
);

track (
    silence = 2
);

track (
    loop 2 {
        DO;
        RE;
        silence = 4;
        loop 89 {
            DO
        }
    }
)
```

- MIDI file (not corresponding)

```
4d 54 68 64 00 00 00 06 00 01 00 01 01 e0 4d 54
72 6b 00 00 00 44 00 c0 0e 00 b0 79 00 00 b0 40
00 00 b0 5b 30 00 b0 0a 40 00 b0 07 64 00 ff 03
01 20 00 90 3e 48 81 70 80 3e 00 00 90 3e 48 81
70 80 3e 00 00 90 3e 48 81 70 80 3e 00 00 90 3e
48 81 70 80 3e 00 01 ff 2f 00
```


## Grammar

```
song : partition
song : partition ';' song
partition : track | assignation
track : TRACK '(' instruction ')'
instruction : statement ';' instruction
instruction : statement
statement : silence | tempo | note | instrument | structure
structure : LOOP NUMBER '{' chansonnette '}'
chansonnette : expression
chansonnette : expression ';' chansonnette
expression : IDENTIFIER | group | silence | structure
assignation : IDENTIFIER '=' '(' group ')'
group : NOTE
group : NOTE ';' group
tempo : TEMPO '=' NUMBER
silence : SILENCE '=' NUMBER
note : NOTE
instrument : INSTRUMENT
```

## Documentation

- http://www.shikadi.net/moddingwiki/MID_Format
- https://www.wavosaur.com/download/midi-note-hex.php
- http://www.ccarh.org/courses/253/handout/smf/
- http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html


## Authors
- Piquerez Thibaut
- Renaud Sylvain
- Gander Laurent

