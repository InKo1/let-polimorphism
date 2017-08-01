from parser_ import ast
from typing import List


class Type:

    """"""

    def __init__(self, name: str, premise=None, conclusion=None):
        self.name = name
        self.premise = premise
        self.conclusion = conclusion
        self.bounded_names = []  # for let - polymorphism

    @classmethod
    def from_ast(cls, node: ast.Type):
        if node is None:
            return None
        if node.term_type == ast.TermType.ARROW:
            return Type('->', cls.from_ast(node.premise), cls.from_ast(node.conclusion))
        return Type(node.token)

    def get_copy(self):
        res = None
        if self.name == '->':
            res = Type('->', self.premise.get_copy(), self.conclusion.get_copy())
        else:
            res = Type(self.name)
        res.bound_names(self.bounded_names.copy())
        return res

    def is_basic_type(self) -> bool:
        return self.name == 'Nat' or self.name == 'Bool'

    def is_type_variable(self) -> bool:
        return self.name[0] == '$'

    def is_func_type(self) -> bool:
        return self.name == '->'

    def bound_names(self, names: List[str]):
        """Связывает имена из names"""
        self.bounded_names.extend(names)

    def replace(self, old_type, new_type):
        """Возвращает новый тип, где все подтипы old_type заменены на new_type"""
        if self == old_type:
            return new_type.get_copy()
        elif self.name == '->':
            return Type('->', self.premise.replace(old_type, new_type), self.conclusion.replace(old_type, new_type))
        else:
            return self.get_copy()

    def get_names_of_type_variables(self) -> List[str]:
        """Возвращает имена типовых переменных"""
        if self.name == '->':
            return self.premise.get_names_of_type_variables() + self.conclusion.get_names_of_type_variables()
        else:
            if self.name[0] != '$':
                return []
            return [self.name]

    def get_unified_type(self, unifier):  # унификация не одновременная, не знаю, может ли это привести к проблемам
        """Возврощает тип, унифицированный unifier`ом"""
        cur_type = self
        for eq in unifier:
            cur_type = cur_type.replace(eq[0], eq[1])
        return cur_type

    def __str__(self) -> str:
        if self.name == '->':
            return '(' + self.premise.__str__() + ' -> ' + self.conclusion.__str__() + ')'
        else:
            return self.name

    def __eq__(self, other) -> bool:
        return self.__str__() == other.__str__()
