import AST
from AST import addToClass

notes = {

}

vars = {}


@addToClass(AST.SongNode)
def compile(self):
    """Ecrit en-tete du fichier avec calcul de la taille."""
    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    # TODO Calcul taille et ajouter en-tete au début
    return bytecode


@addToClass(AST.InstrumentNode)
def compile(self):
    """Definit l'instrument pour la track."""
    pass


@addToClass(AST.TokenNode)
def compile(self):
    """Ecrit la valeur hexa de la note. NON + NOF + Delta time."""
    bytecode = ""
    # TODO ajouter temps de notes etc.
    bytecode += notes[self.tok]  # Récupération de l'hexa dans le dict de notes
    return bytecode


@addToClass(AST.AssignNode)
def compile(self):
    """Sauvegarde de la valeur dans le dict vars."""
    bytecode = ""
    bytecode += self.children[1].compile()
    bytecode += f"SET {self.children[0].tok}\n"
    return bytecode


@addToClass(AST.LoopNode)
def compile(self):
    """Ecrit x fois ses enfants."""
    bytecode = ""
    # whilecpt += 1


@addToClass(AST.TrackNode)
def compile(self):
    """Ecrit une track avec son header et calcul de la taille."""
    bytecode = ""
    for c in self.children:
        bytecode += c.compile()
    # TODO Calcul taille et ajouter en-tete au début
    return bytecode


@addToClass(AST.SilenceNode)
def compile(self):
    """Ecrit un silence."""
    pass


@addToClass(AST.TempoNode)
def compile(self):
    """Définit le tempo."""
    pass


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
