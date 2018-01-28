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
- Number of Tracks -> 2 bytes
- PPQ Value -> 2 bytes

## Track Chunk (contient les messages NON NOF)
- MTrk -> 4 bytes
- Patch change messages
- Reset all Controllers Message
- Pan Control Message
- Volume Control Message
- First MIDI Message
- additional MIDI messages
- Last MIDI message
- PPQ Reset All Controllers Message
- PPQ End of Track Message

Pour avoir plusieurs track dans notre fichier, il suffit d'avoir le même format que la Track Chunk.

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

Nous avons ensuite utilisé les expression regulière. Exemple pour les instruments.

```python
def t_INSTRUMENT(t):
    r'(GUITAR)|(VIOLIN)|(PIANO)|(FLUTE)|(SYNTHPAD)|(HELICOPTER)'
    return t
```

## Parser

Nous avons défini notre grammaire

```
song : partition
song : partition ';' song
partition : track | assignation
track : TRACK '(' instruction ')'
instruction : statement | statement ';' instruction
statement : silence | tempo | note | instrument | structure
structure : LOOP NUMBER '{' chansonnette '}'
chansonnette : expression | expression ';' chansonnette
expression : IDENTIFIER
expression : notepp | silence | structure
assignation : IDENTIFIER '=' '(' group ')'
group : notepp ',' group
ggroup : notepp
time : TIME '=' NUMBER
silence : SILENCE '=' NUMBER
note : NOTE
notepp : note
notepp : FIGURE note ADD_OP NUMBER
notepp : FIGURE note
notepp : note ADD_OP NUMBER
instrument : IDENTIFIER '=' INSTRUMENT
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

Exemple pour les notes, les instruments, figures et les operations.

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

operations = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y
}

FIGURES = {
    '@': 4,
    '$': 2,
    '?': 1,
    '!': 1 / 2
}

```

Ensuite, nous avons definit nos méthodes compile pour nos Nodes. Exemple pour le Note_Node

```python
@addToClass(AST.NoteNode)
def compile(self, gamme=0, op=''):
    """Ecrit la valeur hexa de la note. NON + NOF + Delta time."""
    if DEBUG:
        print('NOTE NODE', self.note)
    bytecode = ""

    # Recherche du tempo
    try:
        tempo = vars['time']
        del vars['time']
    except(KeyError):
        # Tempo par defaut
        tempo = DELTA_TIME_DEFAULT
        try:
            tempo = vars['tempo']
        except(KeyError):
            pass

    # Récupération de l'hexa dans le dict de notes
    note = NOTES[self.note]
    if gamme != 0:
        note = hex(operations[op](int(note, 16), 12 * gamme))[2:]

    bytecode += DELTA_TIME_ZERO + NON + note + END_NOTE_48 + \
                tempo + NOF + note + END_NOTE_ZERO

    return bytecode

```

# Conclusion



# Guide utilisateur

Pour pouvoir utiliser notre compilateur, il faut :
- Installer [pydot](https://pypi.python.org/pypi/pydot)
- Installer [PLY](https://pypi.python.org/pypi/ply)

Ensuite créer un nouveau fichier texte et changer le type de fichier en '.mus'. Editer le fichier avec un éditeur de texte (Atom, Notepad++, Sublime Text).

Quelques règles pour l'édition du fichier.

- Pour une nouvelle track
```
track(
  ...
  )
```
- chaque track aura un instrument et un tempo

```
track(
      INSTRUMENT=SYNTHPAD;
      TEMPO=500;
  )
```
- Les notes seront écrites en majuscules

```
track(
    INSTRUMENT=SYNTHPAD;
    TEMPO=500;
    DO;
    RE;
)
```
- On peut utilier des silences et des TIME pour ajouter un silence, allonger le temps d'une note

```
track(
    INSTRUMENT=SYNTHPAD;
    TEMPO=500;
    DO;
    RE;
    silence=3000;
    SOL;
    LA;
    SI;
    TIME=3000;
)
```
- On peut utiliser les loop pour jouer plusieurs fois les même notes et utiliser des variables pour encapsuler plusieurs notes dedans

```
my_tune = (DO,RE,MI,FA,SOL,LA,SI);

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
- On peut jouer aussi sur le temps de la note en mettant devant la note
  - @(4 fois plus long) => ronde
  - $(2 fois plus longue) => blanche
  - ? => noire
  - !(2 fois plus petite) => croche
- On peut jouer sur les octaves en mettant un
  - '-' un nombre compris entre 1 et 4 si on veut une octave inférieur
  - '+' un nombre compris entre 1 et 5 si on veut une octave supérieur

```
INSTRUMENT=PIANO;
TEMPO=500;
DO;RE;MI;DO;
DO;RE;MI;DO;
MI;FA;$SOL;
MI;FA;$SOL;
!SOL;!LA;!SOL;!FA;MI;DO;
!SOL;!LA;!SOL;!FA;MI;DO;
DO;SOL-1;$DO;
DO;SOL-1;$DO
```

- Enregistrer le fichier dans le dossier tests_inputs
- Ouvrir une invite de commande dans le dossier du projet

```bash
 python compiler.py tests_inputs\nom_de_votre_fichier.mus
```

- double-cliquer sur le fichier généré (non_de_votre_fichier.mid)
- Detendez-vous et appréciez vos talents de musicien

# Sources
- http://www.shikadi.net/moddingwiki/MID_Format
- https://www.wavosaur.com/download/midi-note-hex.php
- http://www.ccarh.org/courses/253/handout/smf/
- http://acad.carleton.edu/courses/musc108-00-f14/pages/04/04StandardMIDIFiles.html
