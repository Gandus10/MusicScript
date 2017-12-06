# MusicScript

Program who convert text to music.

## Functionality
- function note(int time)
- loop to play a note several times or a note sequence
- function silence(int time)
- assign track to var to be reused

## Input/Output
- Input = text file
- Output = mid file

## Exemple
- text file :

```
Track (
	instrument = 'violon'
	tempo = 1
	DO
	RE
	MI
	FA
)

Track (
	instrument = 'guitare'
	tempo = 1
	RE
	DO
	FA
	MI
)

my_tune = Track
```

- mid file

```
4d 54 68 64 00 00 00 06 00 01 00 01 01 e0 4d 54
72 6b 00 00 00 44 00 c0 0e 00 b0 79 00 00 b0 40
00 00 b0 5b 30 00 b0 0a 40 00 b0 07 64 00 ff 03
01 20 00 90 3e 48 81 70 80 3e 00 00 90 3e 48 81
70 80 3e 00 00 90 3e 48 81 70 80 3e 00 00 90 3e
48 81 70 80 3e 00 01 ff 2f 00
```


## Documentation

- http://www.shikadi.net/moddingwiki/MID_Format
- https://www.wavosaur.com/download/midi-note-hex.php
- http://www.ccarh.org/courses/253/handout/smf/
- http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html


## Eleves
- Piquerez Thibaut
- Renaud Sylvain
- Gander Laurent
