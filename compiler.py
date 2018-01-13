import AST
from AST import addToClass

MTHD = "4d546864"
MTRK = "4d54726b"
SMF = "0001"
PPQ = "01e0"

META_EVENT = "ff030120"
END_OF_TRACK = "ff2f00"
NON = "90"
NOF = "80"
DELTA_TIME_ZERO = "00"
DELTA_TIME_DEFAULT = "8170"
DELTA_TIME_ONE = "01"

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

END_NOTE_40 = "40"
END_NOTE_ZERO = "00"

NOTES = {
    'DO': '60',
    'RE': '62',
    'MI': '64',
    'FA': '65',
    'SOL': '67',
    'LA': '69',
    'SI': '71'
}

INSTRUMENTS = {
    'FLUTE': 'c049'
}

vars = {}


def int_to_hex(val, nb_byte):
    size = int(val / 2)
    hexsize = hex(size)[2:]
    while (len(hexsize) < nb_byte * 2):
        hexsize = '0' + hexsize
    return hexsize


@addToClass(AST.SongNode)
def compile(self):
    """Ecrit en-tete du fichier avec calcul de la taille."""
    bytecode = ""
    track_counter = 0
    for c in self.children:
        if c is AST.TrackNode:
            track_counter += 1
        bytecode += c.compile()

    length = int_to_hex(len(bytecode), 4)
    nb_track = int_to_hex(track_counter, 2)

    bytecode = MTHD + length + SMF + nb_track + PPQ + bytecode
    return bytecode


@addToClass(AST.InstrumentNode)
def compile(self):
    """Definit l'instrument pour la track."""
    # print(self.tok, INSTRUMENTS)
    vars['instrument'] = INSTRUMENTS[self.instrument.tok]
    return ""


@addToClass(AST.TokenNode)
def compile(self):
    """Ecrit la valeur hexa de la note. NON + NOF + Delta time."""
    bytecode = ""
    # Récupération de l'hexa dans le dict de notes
    print(self.tok)
    bytecode += DELTA_TIME_ZERO + NON + NOTES[self.tok] + END_NOTE_40 + \
                DELTA_TIME_DEFAULT + NOF + NOTES[self.tok] + END_NOTE_ZERO
    return bytecode


@addToClass(AST.AssignNode)
def compile(self):
    """Sauvegarde de la valeur dans le dict vars."""
    vars[self.children[0].tok] = self.children[1].compile()
    return ""


@addToClass(AST.ChansonnetteNode)
def compile(self):
    """Compile une chansonnette (ensemble de notes)."""
    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    return bytecode


@addToClass(AST.LoopNode)
def compile(self):
    """Ecrit x fois ses enfants."""
    bytecode = ""
    for _ in range(0, int(self.children[0].tok)):
        bytecode += self.children[1].compile()
    return bytecode


@addToClass(AST.TrackNode)
def compile(self):
    """Ecrit une track avec son header et calcul de la taille."""
    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    length = int_to_hex(len(bytecode), 4)
    bytecode = MTRK + length + DELTA_TIME_ZERO + vars['instrument'] + \
               CONTROLLERS + DELTA_TIME_ZERO + META_EVENT + bytecode + \
               DELTA_TIME_ONE + END_OF_TRACK

    return bytecode


@addToClass(AST.SilenceNode)
def compile(self):
    """Ecrit un silence."""
    return ""


@addToClass(AST.TempoNode)
def compile(self):
    """Définit le tempo."""
    return ""


# @addToClass(AST.OpNode)
# def compile(self):
#     bytecode = ""
#     if len(self.children) == 1:
#         bytecode += self.children[0].compile()
#         bytecode += "USUB\n"
#     else:
#         bytecode += self.children[0].compile()
#         bytecode += self.children[1].compile()
#         bytecode += operations[self.op]
#     return bytecode


# def whilecounter():


if __name__ == "__main__":
    from music_parser import parse
    import sys, os

    prog = open(sys.argv[1]).read()
    ast = parse(prog)
    compiled = ast.compile()
    name = os.path.splitext(sys.argv[1])[0] + '.mus'
    outfile = open(name, 'w')
    outfile.write(compiled)
    outfile.close()
    print("Wrote output to", name)
