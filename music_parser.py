import ply.yacc as yacc

from lex import tokens
import AST

vars = {}


def p_song_partition(p):
    ''' song : partition '''
    p[0] = AST.SongNode(p[1])


def p_song_recursive(p):
    ''' song : partition ';' song '''
    p[0] = AST.SongNode([p[1]] + p[3].children)


def p_partition(p):
    ''' partition : track
        | assignation '''
    p[0] = p[1]


def p_track(p):
    ''' track : TRACK '(' instruction ')' '''
    p[0] = AST.TrackNode(p[3].children)


def p_instruction_statement(p):
    ''' instruction : statement
        | statement ';' instruction '''
    try:
        p[0] = AST.InstructionNode([p[1]] + p[3].children)
    except:
        p[0] = AST.InstructionNode(p[1])


def p_statement(p):
    ''' statement : silence
        | tempo
        | time
        | notepp
        | instrument
        | structure '''
    p[0] = p[1]


def p_statement_identifier(p):
    ''' statement : IDENTIFIER '''
    p[0] = AST.TokenNode(p[1])


def p_structure(p):
    ''' structure : LOOP NUMBER '{' chansonnette '}' '''
    p[0] = AST.LoopNode([AST.TokenNode(p[2]), p[4]])


def p_chansonnette_recursive(p):
    ''' chansonnette : expression
        | expression ';' chansonnette '''
    try:
        p[0] = AST.ChansonnetteNode([p[1]] + p[3].children)
    except:
        p[0] = AST.ChansonnetteNode(p[1])


def p_expression_identifier(p):
    ''' expression : IDENTIFIER '''
    p[0] = AST.TokenNode(p[1])


def p_expression(p):
    ''' expression : notepp
        | silence
        | structure '''
    p[0] = p[1]


def p_assignation(p):
    ''' assignation : IDENTIFIER '=' '(' group ')' '''
    p[0] = AST.AssignNode([AST.TokenNode(p[1]), p[4]])


def p_group_recursive(p):
    ''' group : notepp ',' group
        | notepp ';' group '''
    p[0] = AST.ChansonnetteNode([p[1]] + p[3].children)


def p_group_note(p):
    ''' group : notepp '''
    p[0] = AST.ChansonnetteNode(p[1])


def p_tempo(p):
    ''' tempo : TEMPO '=' NUMBER '''
    p[0] = AST.TempoNode(AST.TokenNode(p[3]))


def p_time(p):
    ''' time : TIME '=' NUMBER '''
    p[0] = AST.TimeNode(AST.TokenNode(p[3]))


def p_silence(p):
    ''' silence : SILENCE '=' NUMBER '''
    p[0] = AST.SilenceNode(AST.TokenNode(p[3]))


def p_note(p):
    ''' note : NOTE '''
    p[0] = AST.NoteNode(p[1])


def p_notepp(p):
    ''' notepp : note '''
    p[0] = p[1]


def p_note_figure_gamme(p):
    ''' notepp : FIGURE note ADD_OP NUMBER '''
    p[0] = AST.NotePlusPlus(AST.GammeNode(children=[p[2]] + [AST.TokenNode(p[4])], op=p[3]), figure=p[1])


def p_note_figure(p):
    ''' notepp : FIGURE note '''
    p[0] = AST.NotePlusPlus(p[2], figure=p[1])


def p_note_gamme(p):
    ''' notepp : note ADD_OP NUMBER '''
    p[0] = AST.NotePlusPlus(AST.GammeNode(children=[p[1]] + [AST.TokenNode(p[3])], op=p[2]))


def p_instrument(p):
    ''' instrument : IDENTIFIER '=' INSTRUMENT '''
    p[0] = AST.InstrumentNode(AST.TokenNode(p[3]))


def p_error(p):
    if p:
        print("Syntax error in line %d" % p.lineno)
        yacc.errok()
    else:
        print("Sytax error: unexpected end of file!")


def parse(program):
    return yacc.parse(program)


yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sys

    prog = open(sys.argv[1]).read()
    result = yacc.parse(prog)
    if result:
        print(result)

        import os

        graph = result.makegraphicaltree()
        name = os.path.splitext(sys.argv[1])[0] + '-ast.pdf'
        graph.write_pdf(name)
        print("wrote ast to", name)
    else:
        print("Parsing returned no result!")
