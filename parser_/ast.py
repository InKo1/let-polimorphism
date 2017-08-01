"""Структура данных для представления AST"""

from enum import Enum


class TermType(Enum):
    VAR = 0
    ABS = 1
    APP = 2
    LET = 3
    TYPE = 4
    ARROW = 5


class Node:

    """Узел синтаксического дерева"""

    def __init__(self, token, term_type):
        self.token = token
        self.term_type = term_type


class App(Node):
    def __init__(self, token, term_type):
        super().__init__(token, term_type)
        self.left_term = None
        self.right_term = None

    def add_left_term(self, term):
        self.left_term = term
        return self

    def add_right_term(self, term):
        self.right_term = term
        return self


class Abs(Node):
    def __init__(self, token, term_type):
        super().__init__(token, term_type)
        self.var = None
        self.var_type = None
        self.body = None

    def add_var(self, var):
        self.var = var
        return self

    def add_var_type(self, var_type):
        self.var_type = var_type
        return self

    def add_body(self, term):
        self.body = term
        return self

    @property
    def var_name(self):
        return self.var.token

    @property
    def var_type_name(self):
        return self.var_type.token


class Let(Node):
    def __init__(self, token, term_type):
        super().__init__(token, term_type)
        self.var = None
        self.substitution_term = None
        self.body = None

    def add_var(self, var):
        self.var = var
        return self

    def add_body(self, term):
        self.body = term
        return self

    def add_substitution_term(self, term):
        self.substitution_term = term
        return self

    @property
    def var_name(self):
        return self.var.token


class If(Node):
    pass


class Type(Node):
    def __init__(self, token, term_type):
        super().__init__(token, term_type)
        self.premise = None
        self.conclusion = None

    def add_premise(self, premise):
        self.premise = premise
        return self

    def add_conclusion(self, conclusion):
        self.conclusion = conclusion
        return self
