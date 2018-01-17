import AST
import binascii
from AST import addToClass

DEBUG = True

MTHD = "4d546864"
MTRK = "4d54726b"
END_OF_TRACK = "ff2f00"
SMF = "0001"
PPQ = "03e8"

DELTA_TIME_ZERO = "00"
DELTA_TIME_DEFAULT = "8768"
DELTA_TIME_ONE = "01"
END_NOTE_48 = "48"
END_NOTE_ZERO = "00"

TEMPO_CONDUCTOR_TRACK = MTRK + '00000019' + \
                        DELTA_TIME_ZERO + 'FF580404021808' + \
                        DELTA_TIME_ZERO + 'FF59020200' + \
                        DELTA_TIME_ZERO + 'FF51030F4240' + \
                        DELTA_TIME_ONE + END_OF_TRACK

META_EVENT = "ff030120"
NON = "90"
NOF = "80"

RESET_ALL_CONTROLLER = "b07900"
PEDAL_OFF = "b04000"
EFFECTS_LEVEL = "b05b30"
STEREO_PAN = "b00a40"
VOLUME = "b00764"
CONTROLLERS = DELTA_TIME_ZERO + RESET_ALL_CONTROLLER + \
              DELTA_TIME_ZERO + PEDAL_OFF + \
              DELTA_TIME_ZERO + EFFECTS_LEVEL + \
              DELTA_TIME_ZERO + STEREO_PAN + \
              DELTA_TIME_ZERO + VOLUME

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
    '@': 4,  # Ronde
    '$': 2,  # Blanche
    '?': 1,  # Noire
    '!': 1 / 2,  # Croche
    '.': 1 / 4  # Double croche
}

vars = {
    'tempo': DELTA_TIME_DEFAULT
}


def int_to_hex(val, nb_bytes_desired):
    hexsize = hex(val)[2:]
    while (len(hexsize) < nb_bytes_desired * 2):
        hexsize = '0' + hexsize
    return hexsize


def int_to_vlv(val):
    val_bin = bin(val)[2:]
    val_bin_vlv = ""
    count = 0
    state = '0'
    for bit in reversed(val_bin):
        val_bin_vlv = bit + val_bin_vlv
        count += 1
        if count % 7 == 0:
            val_bin_vlv = state + val_bin_vlv
            state = '1'

    while len(val_bin_vlv) % 8 != 0:
        val_bin_vlv = '0' + val_bin_vlv

    if len(val_bin_vlv) > 8:
        val_bin_vlv = '1' + val_bin_vlv[1:]

    return hex(int(val_bin_vlv, 2))[2:]


def vlv_to_int(val_vlv_hex):
    vlv_bin = bin(int(val_vlv_hex, 16))[2:]
    bin_number = ""
    count = 0
    for bit in reversed(vlv_bin):
        count += 1
        if count % 8 != 0:
            bin_number = bit + bin_number
    return int(bin_number, 2)


@addToClass(AST.SongNode)
def compile(self):
    """Ecrit en-tete du fichier avec calcul de la taille."""
    if DEBUG:
        print('SONG NODE')
    bytecode = ""
    # bytecode += TEMPO_TRACK
    track_counter = 0
    for c in self.children:
        if c.type == 'TRACK':
            track_counter += 1
        bytecode += c.compile()

    length = "00000006"  # length of header is 6
    nb_track = int_to_hex(track_counter, 2)

    bytecode = MTHD + length + SMF + nb_track + PPQ + bytecode
    return bytecode


@addToClass(AST.InstrumentNode)
def compile(self):
    """Definit l'instrument pour la track."""
    if DEBUG:
        print('INSTRU NODE', self.children[0].tok)
    # print(self.tok, INSTRUMENTS)
    vars['instrument'] = INSTRUMENTS[self.children[0].tok]
    return ""


@addToClass(AST.TokenNode)
def compile(self):
    """Ecrit la valeur hexa de la note. NON + NOF + Delta time."""
    if DEBUG:
        print('TOKEN NODE', self.tok)
    bytecode = ""
    try:
        # Definit le tempo pour les notes des variables
        bytecode += vars[self.tok].replace(' ', vars['tempo'])
    except:
        print("var not found", self.tok)
    return bytecode


@addToClass(AST.NotePlusPlus)
def compile(self):
    """Definit la figure de la note (ronde, blanche, noire, croche)."""

    if self.figure != '':
        # vars['time'] = int_to_vlv(int(FIGURES[self.figure] * int(PPQ, 16)))
        vars['figure'] = self.figure

    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    return bytecode


@addToClass(AST.NoteNode)
def compile(self, gamme=0, op=''):
    """Ecrit la valeur hexa de la note. NON + NOF + Delta time."""
    if DEBUG:
        print('NOTE NODE', self.note)
    bytecode = ""

    tempo = ' '
    # Recherche du tempo
    try:
        tempo = vars['figure']
        del vars['figure']
    except:
        try:
            tempo = vars['time']
            del vars['time']
        except(KeyError):
            # Tempo par defaut
            pass

    # Récupération de l'hexa dans le dict de notes
    note = NOTES[self.note]
    if gamme != 0:
        note = hex(operations[op](int(note, 16), 12 * gamme))[2:]

    bytecode += DELTA_TIME_ZERO + NON + note + END_NOTE_48 + \
                tempo + NOF + note + END_NOTE_ZERO

    return bytecode


@addToClass(AST.GammeNode)
def compile(self):
    """ Change la gamme d'une note. """
    if DEBUG:
        print('GAMME NODE : ' + self.children[0].note, self.children[1].tok)
    bytecode = ""
    bytecode += self.children[0].compile(self.children[1].tok, self.op)
    return bytecode


@addToClass(AST.AssignNode)
def compile(self):
    """Sauvegarde de la valeur dans le dict vars."""
    if DEBUG:
        print('ASSIGN NODE', self.children[0].tok, self.children[1])
    vars[self.children[0].tok] = self.children[1].compile()
    return ""


@addToClass(AST.ChansonnetteNode)
def compile(self):
    """Compile une chansonnette (ensemble de notes)."""
    if DEBUG:
        print('CHANSONNETTE NODE')
    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    return bytecode


@addToClass(AST.LoopNode)
def compile(self):
    """Ecrit x fois ses enfants."""
    if DEBUG:
        print('LOOP NODE')
    bytecode = ""
    for _ in range(0, int(self.children[0].tok)):
        bytecode += self.children[1].compile()
    return bytecode


@addToClass(AST.TrackNode)
def compile(self):
    """Ecrit une track avec son header et calcul de la taille."""
    if DEBUG:
        print('TRACK NODE')
    bytecode = ""

    size = len(self.children)
    i = 0
    while i < size:
        c = self.children[i]
        if type(c) is AST.TokenNode:
            while i + 1 < size and type(self.children[i + 1]) is AST.TimeNode:
                self.children[i + 1].compile()
                i += 1
        compiled = c.compile()
        for key in FIGURES.keys():
            compiled = compiled.replace(key, int_to_vlv(int(FIGURES[key] * vlv_to_int(vars['tempo']))))

        compiled = compiled.replace(' ', vars['tempo'])
        bytecode += compiled
        i += 1

    bytecode = DELTA_TIME_ZERO + vars['instrument'] + \
               CONTROLLERS + DELTA_TIME_ZERO + META_EVENT + bytecode + \
               DELTA_TIME_ONE + END_OF_TRACK

    length = int_to_hex(int(len(bytecode) / 2), 4)
    bytecode = MTRK + length + bytecode
    return bytecode


@addToClass(AST.TimeNode)
def compile(self):
    """Ecrit un silence."""
    if DEBUG:
        print('TIME NODE', int_to_vlv(int(self.children[0].tok) * 2))
    last_time = 0
    try:
        last_time = vlv_to_int(vars['time'])
    except(KeyError):
        pass
    vars['time'] = int_to_vlv(int(self.children[0].tok) * 2 + last_time)
    return ""


@addToClass(AST.TempoNode)
def compile(self):
    """Définit le tempo."""
    if DEBUG:
        print('TEMPO NODE', int_to_vlv(int(self.children[0].tok) * 2))
    vars['tempo'] = int_to_vlv(int(self.children[0].tok) * 2)
    return ""


@addToClass(AST.SilenceNode)
def compile(self):
    """Ecrit une note silencieuse"""
    bytecode = ""
    silence = int_to_vlv(self.children[0].tok)
    bytecode += DELTA_TIME_ZERO + NON + "3c" + END_NOTE_ZERO + \
                silence + NOF + "3c" + END_NOTE_ZERO
    return bytecode


if __name__ == "__main__":
    from music_parser import parse
    import sys, os

    prog = open(sys.argv[1]).read()
    ast = parse(prog)
    compiled = ast.compile()

    name = os.path.splitext(sys.argv[1])[0] + '.mid'
    with open(name, "wb") as f:
        f.write(binascii.unhexlify(compiled))
    print("Wrote output to", name)
