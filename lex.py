import ply.lex as lex

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

literals = '(){};=,'


def t_INSTRUMENT(t):
    r'(guitar)|(violon)|(piano)'
    return t


def t_NOTE(t):
    r'(DO)|(RE)|(MI)|(FA)|(SOL)|(LA)|(SI)'
    return t


def t_NUMBER(t):
    r'\d'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Line %d: Problem while parsing %s!" % (t.lineno, t.value))
        t.value = 0
    return t


def t_IDENTIFIER(t):
    r'[A-Za-z_]\w*'
    if t.value in reserved_words:
        t.type = t.value.upper()
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'


def t_error(t):
    print("Illegal character '%s'" % repr(t.value[0]))
    t.lexer.skip(1)


lex.lex()

if __name__ == "__main__":
    import sys

    prog = open(sys.argv[1]).read()

    lex.input(prog)

    while 1:
        tok = lex.token()
        if not tok: break
        print("line %d: %s(%s)" % (tok.lineno, tok.type, tok.value))
