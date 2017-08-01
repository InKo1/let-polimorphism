"""Пасер для лямбда - исчисления с конструкцией let"""

import ply.yacc as yacc
import ply.lex as lex

from .ast import *


tokens = (
    'LAMBDA', 'SIMPLE_TYPE', 'POINT',
    'OPEN', 'CLOSE', 'VAR', 'COLON',
    'ARROW', 'LET', 'IN', 'EQ', 'TYPE_VAR',
)

t_LAMBDA = r'\\'
t_SIMPLE_TYPE = r'Nat|Bool'
t_TYPE_VAR = r'\$[A-Z][A-Z]*'
t_ARROW = r'-'
t_POINT = r'\.'
t_OPEN = r'\('
t_CLOSE = r'\)'
t_IN = r'in'
t_VAR = r'\$[a-z][a-z]*'
t_COLON = r':'
t_LET = r'let'
t_EQ = r'='

t_ignore = ' \r\n\t\f'


def t_error(t):
    print('')


def p_term(p):
    """
    term : var
         | abs
         | app
         | let
    """
    p[0] = p[1]


def p_abs(p):
    """
    abs : OPEN LAMBDA var COLON type POINT term CLOSE
        | OPEN LAMBDA var POINT term CLOSE
    """
    if len(p) == 9:
        p[0] = Abs('\\', TermType.ABS)\
            .add_var(p[3])\
            .add_var_type(p[5])\
            .add_body(p[7])
    elif len(p) == 7:
        p[0] = Abs('\\', TermType.ABS)\
            .add_var(p[3])\
            .add_body(p[5])


def p_type(p):
    """
    type : SIMPLE_TYPE
         | TYPE_VAR
         | OPEN type ARROW type CLOSE
    """
    if len(p) == 2:
        p[0] = Type(p[1], TermType.TYPE)
    elif len(p) == 6:
        p[0] = Type('->', TermType.ARROW)\
            .add_premise(p[2])\
            .add_conclusion(p[4])
    elif len(p) == 4:
        p[0] = Type('->', TermType.ARROW)\
            .add_premise(p[1])\
            .add_conclusion(p[3])


def p_app(p):
    """app : OPEN term term CLOSE"""
    if len(p) == 5:
        p[0] = App('', TermType.APP)\
            .add_left_term(p[2])\
            .add_right_term(p[3])


def p_let(p):
    """let : LET var EQ term IN term"""
    p[0] = Let('let', TermType.LET)\
        .add_var(p[2])\
        .add_substitution_term(p[4])\
        .add_body(p[6])


def p_var(p):
    """var : VAR"""
    p[0] = Node(p[1], TermType.VAR)


def parse(term):
    lexer = lex.lex()
    parser = yacc.yacc()

    return parser.parse(term)
