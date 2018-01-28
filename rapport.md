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

Le projet a été réalisé dans le cadre du cours "Compilateurs" par des élèves de troisième année dans la filière "Développement Logiciel et Multimédia". Le but de ce projet est la programmation d’un compilateur. Il est réalisé en python en utilisant PLY.

Notre projet consiste à pouvoir écrire un fichier `.mus` qui contient du texte décrivant une chanson et de le compiler en un fichier midi, jouable par les logiciels de lecture audio. Ce fichier `.mid` contient de l'hexadécimal.

# Structure d'un fichier mid
D'après http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html.

## Header Chunk

- un MThd -> 4 bytes
- Length -> 4 bytes
- SMF Type -> 2 bytes
- Number of Tracks -> 2 bytes
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

Pour avoir plusieurs track dans notre fichier, il suffit d'avoir le même format que la Track Chunk 2. La Track Chunk 2 est facultative.

# Conception

## But du projet

Le but de ce compilateur est de pouvoir compiler un fichier mus en un fichier mid, notre fichier mus contiendra certaines instructions :
- assignation de variables afin d'être réutilisé
- loop
- fonction silence
- fonction tempo
- note

il sera construit de la manière suivante

```
track (
    INSTRUMENT=PIANO;
    TEMPO=500;
    silence = 1000;
    loop 6 {
        SOL
    }
);

my_tune = (DO,RE,MI,FA,SOL,LA,SI,DO+1);

track (
    INSTRUMENT=PIANO;
    TEMPO=500;
    loop 5 {
        my_tune
    };
    SOL;
    SOL
)
```

## Fonctionnalités

### Instruments
On peut définir l'instrument pour chaque track avec une affectation à `INSTRUMENT`.

Les instruments disponibles sont :
- `GUITAR`
- `VIOLIN`
- `PIANO`
- `FLUTE`
- `SYNTHPAD`
- `HELICOPTER`

Exemple: `INSTRUMENT = PIANO;`

### Notes
On peut écrire toute la gamme de note : `DO`, `RE`, `MI`, `FA`, `SOL`, `LA`, `SI`.

On peut également ajouter des modificateurs à ces notes, par exemple définir quelle figure c'est, exemple pour une ronde : `@DO`.

Les figures se présentent comme ceci : 

|  `@`  |   `$`   |  `?`  |   `!`  |      `.`      |
|:-----:|:-------:|:-----:|:------:|:-------------:|
| Ronde | Blanche | Noire | Croche | Double croche |

On peut également changer d'octave pour chaque note avec les opérateurs `+` et `-`, par exemple : `DO+2`, `RE-1`. `+x` correspond à `x` octaves plus hautes et `-x` à `x` octaves plus basses. On peut descendre jusqu'à 4 octaves, et monter jusqu'à 5 octaves

### Boucles
Il est possible de boucler sur un ensemble de notes, cela permet de répéter une séquence musicale. Les boucles se font avec `loop x`, avec x un nombre entier positif.

Cet exemple va répéter 5 fois la séquence `DO; RE; MI;` :
```
loop 5 {
    DO; RE; MI;
}
```

### Assignation de variables
Il est possible d'ajouter un groupe de note dans une variable afin que cette suite de note puisse être réutilisée plusieurs fois.

Exemple : 

Assignation : `ding_dong = (DO,SOL-1,$DO);`

Puis par exemple dans une boucle : 
```
loop 5 {
    ding_dong
}
```

### Tempo
Au début de chaque track on peut paramétrer le tempo pour la track en question de la manière suivante:
```
TEMPO=1000
```
Le numéro correspond au nombre de millisecondes que chaque note va durer.

Pour pouvoir déterminer le temps du tempo en millisecondes il a fallut cacluler de la manière suivante:  
 > BPM = 120 (par défaut)  
PPQ = 1000 (c'est un choix -> plus facile pour calculer)  
Si on mutliplie le BPM par le PPQ cela va nous donner le nombre de ticks par minute:  
BPM \* PPQ = 120 \* 1000 = 120'000 ticks/minute = 2'000 ticks/seconde  
Dans le format midi la valeur de durée de chaque note se compte en nombre de ticks. Donc avec les valeurs que nous avons ici cela signifie que si on mets 2'000 ticks pour une note, elle va durer 1 seconde. Ensuite pour pouvoir écrire les tempos en millisecondes il suffit de multipier par deux le chiffre qu'il y a dans le code.


### Time
Permet de modifie la durée d'une note.
```
LA;
TIME=2000;
DO;
```
Cela signifie que la note LA va durer 2 secondes et les durées des autres notes sera celui du tempo.

### Silence
Permet de jouer une note silencieuse de la manière suivante:
```
LA;
DO;
silence=1000;
Mi;
```
Cela veut dire qu'il y aura 1 seconde de silence entre le DO et le MI.


## Lex

Nous avons commencé par définir les mots réservés, les tokens et les literals

```python

reserved_words = (
    'track',
    'silence',
    'time',
    'loop',
    'violin',
    'guitar',
    'piano',
    'flute',
    'synthpad',
    'helicopter',
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
             'TEMPO',
             'IDENTIFIER',
             'NOTE',
             'INSTRUMENT',
             'ADD_OP',
             'FIGURE'
         ) + tuple(map(lambda s: s.upper(), reserved_words))

literals = '(){};=,'

```

Nous avons ensuite utilisé les expression regulière. Exemple pour les instruments et les figures de notes.

```python
def t_INSTRUMENT(t):
    r'(GUITAR)|(VIOLIN)|(PIANO)|(FLUTE)|(SYNTHPAD)|(HELICOPTER)'
    return t

def t_FIGURE(t):
    r'[@$?!.]'
    return t
```

## Parser

Nous avons défini notre grammaire

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

Exemple pour les chansonnettes récursives :

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

Pour le compiler, nous avons transformé nos expressions en code héxadécimal. Chaque expression, notes, instruments, en-tête, etc. ont un code qui leur correspondent.

Exemple pour quelques constantes obligatoire pour les fichier `.mid` :

```python
MTHD = "4d546864"
MTRK = "4d54726b"
END_OF_TRACK = "ff2f00"
SMF = "0001"
PPQ = "03e8"
```

Exemple pour les notes et les instruments

```python
NOTES = {
    'DO': '30',  # 48
    'RE': '32',  # 50
    'MI': '34',  # 52
    'FA': '35',  # 53
    'SOL': '37',  # 55
    'LA': '39',  # 57
    'SI': '3b'  # 59
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

Pour les figures des notes, nous avons défini pour chaque figure un facteur de durée de la note par rapport à la normale :

```python
FIGURES = {
    '@': 4,  # Ronde
    '$': 2,  # Blanche
    '?': 1,  # Noire
    '!': 1 / 2,  # Croche
    '.': 1 / 4  # Double croche
}
```

# Conclusion

## Etat du projet
Le compilateurs est fonctionnel et il est possible d'écouter les fichiers audios générés. Nous avons par exemple pu écrire Frère Jacques.
Toutes les fonctionnalités implémentés fonctionnent. Cependant les track débutent toutes en même temps, le format MIDI est prévu ainsi. Il est possible de palier à ce souci en ajoutant des silences au début d'une track à décaler.

## Améliorations possibles
- Ajouter la possibilité de définir un offset au début d'une track pour qu'elle se joue avec un temps de décalage.
- Ajouter la prise en charges des dièse et bémol.
- Ajouter des instruments

# Sources
- http://www.shikadi.net/moddingwiki/MID_Format
- https://www.wavosaur.com/download/midi-note-hex.php
- http://www.ccarh.org/courses/253/handout/smf/
- http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html
- https://www.noterepeat.com/articles/how-to/213-midi-basics-common-terms-explained
- https://www.csie.ntu.edu.tw/~r92092/ref/midi/
- http://www.electronics.dit.ie/staff/tscarff/Music_technology/midi/midi_note_numbers_for_octaves.htm
- http://www.ccarh.org/courses/253/handout/gminstruments/
