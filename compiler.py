import AST
from AST import addToClass


# operations = {
#     '+': lambda x, y: x + y,
#     '-': lambda x, y: x - y,
#     '*': lambda x, y: x * y,
#     '/': lambda x, y: x / y,
# }

# operations = {
#     '+': 'ADD\n',
#     '-': 'SUB\n',
#     '*': 'MUL\n',
#     '/': 'DIV\n'
# }

notes = {
    'SOL': 'AF556',

}



@addToClass(AST.SongNode)
def compile(self):
    bytecode = ""
    for c in self.children:
        bytecode += (c.compile())
    return bytecode


@addToClass(AST.TokenNode)
def compile(self):
    bytecode = ""
    if isinstance(self.tok, str):
        bytecode += f"PUSHV {self.tok}\n"
    else:
        bytecode += f"PUSHC {self.tok}\n"
    return bytecode


@addToClass(AST.AssignNode)
def compile(self):
    bytecode = ""
    bytecode += self.children[1].compile()
    bytecode += f"SET {self.children[0].tok}\n"
    return bytecode


@addToClass(AST.PrintNode)
def compile(self):
    bytecode = ""
    bytecode += self.children[0].compile()
    bytecode += f"PRINT\n"
    return bytecode


@addToClass(AST.OpNode)
def compile(self):
    bytecode = ""
    if len(self.children) == 1:
        bytecode += self.children[0].compile()
        bytecode += "USUB\n"
    else:
        bytecode += self.children[0].compile()
        bytecode += self.children[1].compile()
        bytecode += operations[self.op]
    return bytecode


# def whilecounter():

@addToClass(AST.LoopNode)
def compile(self):
    bytecode = ""
    # whilecpt += 1


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
