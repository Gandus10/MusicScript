# MusicScript
Compiler who convert text to music.

## Functionality
- Note : `DO`, `RE`, etc.
- Note figure 
    - Ronde : `@DO`
    - Blanche :`$DO`
    - Noire : `?DO`
    - Croche : `!DO`
    - Double croche : `.DO`
- Change octave witch `+` or `-` : `DO+2`, `RE-1`
- Loop to play a note several times or a note sequence : `loop 10 {...}`
- Silence before or after a note : `silence = 1000`
- Assign some notes to var to be reused : `ding_dong = (DO,SOL-1,$DO);`
- Set tempo for a track : `TEMPO = 500`

## Input/Output
- Input = text file (.mus)
- Output = MIDI file (.mid), playable by music player like Windows Media Player

## Example : Frère Jacques
- text file :

```
frere_jacques = (DO;RE;MI;DO);
dormez_vous = (MI,FA,$SOL);
matines = (!SOL,!LA,!SOL,!FA,MI,DO);
ding_dong = (DO,SOL-1,$DO);

track(
    INSTRUMENT=PIANO;
    TEMPO=400;
    loop 10{
        loop 2 {
            frere_jacques
        };
        loop 2 {
            dormez_vous
        };
        loop 2 {
            matines
        };
        loop 2{
            ding_dong
        }
    }
)
```

- MIDI file (not complete)

```
4d54 6864 0000 0006 0001 0001 03e8 4d54
726b 0000 0b60 00c0 5800 b079 0000 b040
0000 b05b 3000 b00a 4000 b007 6400 ff03
0120 0090 3048 8620 8030 0000 9032 4886
2080 3200 0090 3448 8620 8034 0000 9030
4886 2080 3000 0090 3048 8620 8030 0000
9032 4886 2080 3200 0090 3448 8620 8034
0000 9030 4886 2080 3000 0090 3448 8620
8034 0000 9035 4886 2080 3500 0090 3748
8c40 8037 0000 9034 4886 2080 3400 0090
...
```


## Grammar

```
song -> partition | partition ; song
partition -> track | assignation
track -> TRACK ( instruction )
instruction -> statement | statement ; instruction
statement -> silence | tempo | time | notepp | instrument | structure | IDENTIFIER
structure -> LOOP NUMBER { chansonnette }
chansonnette -> expression | expression ; chansonnette
expression -> IDENTIFIER | notepp | silence | structure
assignation -> IDENTIFIER = ( group )
group -> notepp , group | notepp ; group | notepp
tempo -> TEMPO = NUMBER
time -> TIME = NUMBER
silence -> SILENCE = NUMBER
note -> NOTE
notepp -> note | FIGURE note ADD_OP NUMBER | FIGURE note | note ADD_OP NUMBER
instrument -> IDENTIFIER = INSTRUMENT
```

## Documentation
- http://www.shikadi.net/moddingwiki/MID_Format
- https://www.wavosaur.com/download/midi-note-hex.php
- http://www.ccarh.org/courses/253/handout/smf/
- http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html
- https://www.noterepeat.com/articles/how-to/213-midi-basics-common-terms-explained
- https://www.csie.ntu.edu.tw/~r92092/ref/midi/
- http://www.electronics.dit.ie/staff/tscarff/Music_technology/midi/midi_note_numbers_for_octaves.htm
- http://www.ccarh.org/courses/253/handout/gminstruments/



## Authors
- Piquerez Thibaut
- Renaud Sylvain
- Gander Laurent

