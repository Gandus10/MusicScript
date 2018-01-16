---
title: Rapport Music Script
lang: fr
author:
- Piquerez Thibaut^[thibaut.piquerez@he-arc.ch]
- Renaud Sylvain^[sylvain.renaud@he-arc.ch]
- Gander Laurent^[laurent.gander@he-arc.ch]
date: \today
pagesize: A4
toc: true
toc-depth: 5
fontsize: 14pt
documentclass: scrreprt
documentoptions: twoside
numbersections: true
---

# Introduction

Le projet a été réalisé dans le cadre du cours "compilateur" par des élèves de troisième année dans la filière "Developpement Logiciel et Multimédia". Le but de ce projet est la programmation d’un compilateur. Il est réalisé en python en utilisant PLY.

Notre projet consiste à pouvoir lire un fichier .mus qui contient du texte décrivant une chanson et de le compiler en .mid. Ce fichier point mid contient de l'hexadécimal.

# Structure d'un fichier mid

## Header Chunk

- un MThd -> 4 bytes
- Lenght -> 4 bytes
- SMF Type -> 2 bytes
- Number of Tracks -> bytes
- PPQ Value -> 2 bytes

## Track Chunk 1 (meta-events and tempo events)

- MThd -> 4 bytes
- PPQ -> Time Signature meta-event 7 bytes
- PPQ -> Key Signature meta-event 5 bytes
- PPQ -> meta-event additionnel (nom de la track, copyright, etc...)
- PPQ -> Tempo meta-event 6 bytes
- PPQ -> changement de Tempo
- PPQ -> End of Track Message

## Track Chunk 2 First track (contient les messages NON NOF)
- MTrk -> 4 bytes
- PPQ -> Patch change messages
- PPQ -> Reset all Controllers Message
- PPQ -> Pan Control Message
- PPQ -> Volume Control Message
- PPQ -> First MIDI Message
- PPQ -> additional MIDI messages
- PPQ -> Last MIDI message
- PPQ Reset All Controllers Message
- PPQ End of Track Message

Pour avoir plusieurs track dans notre fichier, il suffit d'avoir le même format que la Track Chunk 2.

# Conception

## But du projet

Le but de ce compilateur est de pouvoir compiler un fichier mus en un fichier mid, notre fichier mus contiendra certaines instructions :
- assignation de track afin d'être réutilisé
- loop
- refrain
- fonction silence
- fonction tempo
- note

il sera construit de la manière suivante

```
track(
    GUITAR;
    tempo = 2;
    LA;
    SI;
    MI;
    SI;
    LA;
    silence = 2
);

my_tune = (LA,DO,RE,MI,FA);

track (
    PIANO;
    tempo = 2;
    loop 5 {
        FA;
        SOL;
        my_tune;
        FA
    };
    SOL;
    SOL
)
```
## Lex

Nous avons commencés par définir les mots réservé et les tokens

```python
reserved_words = (
    'track',
    'silence',
    'loop',
    'violin',
    'guitar',
    'piano',
    'tempo',
    'do',
    're',
    'mi',
    'fa',
    'sol',
    'la',
    'si'
)

tokens = (
             'NUMBER',
             'IDENTIFIER',
             'NOTE',
             'INSTRUMENT'
         ) + tuple(map(lambda s: s.upper(), reserved_words))

```

Nous avons ensuite utilisé les expression regulière. Exemple pour les instruments.

```python
def t_INSTRUMENT(t):
    r'(GUITAR)|(VIOLIN)|(PIANO)'
    return t
```

## Parser

Nous avons défini notre grammaire

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

Exemple pour les chansonnettes récursives.

```python
def p_chansonnette_recursive(p):
    ''' chansonnette : expression
        | expression ';' chansonnette '''
    try:
        p[0] = AST.ChansonnetteNode([p[1]] + p[3].children)
    except:
        p[0] = AST.ChansonnetteNode(p[1])
```

## Compiler

Pour le compiler, nous avons transformer nos expression en code héxadécimal. Chaque expression, notes, instruments en-tête à un code qui lui correspond.

Exemple pour quelques constantes obligatoire pour les fichier .mid

```python
DEBUG = True
MTHD = "4d546864"
MTRK = "4d54726b"
END_OF_TRACK = "ff2f00"
SMF = "0001"
PPQ = "03e8"
```

Exemple pour les notes et les instruments.

```python
NOTES = {
    'DO': '30',
    'RE': '32',
    'MI': '34',
    'FA': '35',
    'SOL': '37',
    'LA': '39',
    'SI': '3b'
}

INSTRUMENTS = {
    'GUITAR': 'c018',
    'VIOLIN': 'c028',
    'PIANO': 'c001',
    'FLUTE': 'c049',
    'SYNTHPAD': 'c058',
    'HELICOPTER': 'c07d'
}
```








# Conclusion

# Sources
- http://www.shikadi.net/moddingwiki/MID_Format
- https://www.wavosaur.com/download/midi-note-hex.php
- http://www.ccarh.org/courses/253/handout/smf/
- http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html
