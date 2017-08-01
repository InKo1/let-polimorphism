import sys
from string import ascii_uppercase
import random
from typing import List, Tuple, Dict

from parser_ import *
from type_ import Type


TypeEquation = TypeSubstitution = Tuple[Type, Type]


def get_possible_var_name(bounded_names: List[str]) -> str:
    """Возвращает новое имя переменной, чтобы оно не входило в bound_names"""
    ascii_ = set(map(lambda l: '$' + l, ascii_uppercase))

    diff = ascii_.difference(set(bounded_names))

    if diff != set():
        return diff.pop()
    else:  # вообще - то тут может работать неправильно, потом исправлю
        return '$' + ascii_uppercase[random.randint(0, 25)] + ascii_uppercase[random.randint(0, 25)]


def get_type_and_constraints(
        node: ast.Node,
        ctx: Dict[str, Type],
        used_names: List[str]) -> Tuple[Type, List[str], List[TypeEquation]]:
    """Реализация правил типизации с ограничениями. Пирс, глава 22, раздел 3 и модернизация из разделов 6, 7

    Возвращает тройку, где первая компонента - тип, вторая - используемые имена типовых переменных,
    третья - типовые ограничения
    """
    if node.term_type == ast.TermType.APP:
        t1 = get_type_and_constraints(node.left_term, ctx, used_names)
        t1_used_names = t1[1] + t1[0].get_names_of_type_variables()
        t2 = get_type_and_constraints(node.right_term, ctx, used_names + t1_used_names)
        t2_used_names = t2[1] + t2[0].get_names_of_type_variables()

        new_type_name = get_possible_var_name(t1_used_names + t2_used_names + used_names)
        new_type = Type(new_type_name)

        return (
            new_type,
            t1[1] + t2[1] + [new_type_name],
            t1[2] + t2[2] + [(t1[0], Type('->', t2[0], new_type))]
        )
    elif node.term_type == ast.TermType.ABS:
        new_used_names = []

        if node.var_type is not None:
            var_type = Type.from_ast(node.var_type)
            if var_type.is_type_variable():
                new_used_names.append(var_type.name)
        else:
            new_type_name = get_possible_var_name(used_names)
            var_type = Type(new_type_name)
            new_used_names.append(new_type_name)

        ctx[node.var_name] = var_type
        subterm_res = get_type_and_constraints(node.body, ctx, used_names + new_used_names)
        return (
            Type('->', var_type, subterm_res[0]),
            subterm_res[1] + new_used_names,
            subterm_res[2]
        )
    elif node.term_type == ast.TermType.LET:
        sub_term_res = get_type_and_constraints(node.substitution_term, ctx, used_names)
        sub_term_type = sub_term_res[0]

        # Вот здесь начинается модернизация из раздела 7
        unifier = get_unifier(sub_term_res[2])
        unified_type = sub_term_type.get_unified_type(unifier)
        ctx = dict(map(
            lambda el: (el[0], el[1].get_unified_type(unifier)),
            ctx.items()
        ))

        bounded_type_var_names = set(
            map(lambda t: t.name, ctx.values())
        ).intersection(set(unified_type.get_names_of_type_variables()))
        unified_type.bound_names(list(bounded_type_var_names))  # добавляем квантор для любого к типовым переменным
        ctx[node.var.token] = unified_type
        return get_type_and_constraints(node.body, ctx, used_names)
    else:
        type_ = ctx[node.token]
        if not type_.bounded_names:  # если нет переменных связанных квантором для любого
            return type_, [], []
        new_used_names = []
        for b in type_.bounded_names:
            new_name = get_possible_var_name(type_.bounded_names + used_names)
            new_used_names.append(new_name)
            type_ = type_.replace(Type(b), Type(new_name))
        type_.bounded_names = []
        return type_, new_used_names, []


def replace(constraints: List[TypeEquation], old_type: Type, new_type: Type) -> List[TypeEquation]:
    """Возвращает новый список ограничений, где все вхождения old_type из constraints заменены на new_type"""
    return list(
        map(
            lambda t: (t[0].replace(old_type, new_type), t[1].replace(old_type, new_type)),
            constraints
        )
    )


def get_unifier(constraints: List[TypeEquation]) -> List[TypeSubstitution]:
    """Возвращает унификатор для contraints. Пирс, глава 22, раздел 4"""
    if not constraints:
        return []

    left, right = constraints[0][0], constraints[0][1]
    left_type_vars = left.get_names_of_type_variables()
    right_type_vars = right.get_names_of_type_variables()

    if left == right:
        return get_unifier(constraints[1:])
    elif left.is_type_variable() and left.name not in right_type_vars:
        return [(left, right)] + get_unifier(replace(constraints[1:], left, right))
    elif right.is_type_variable() and right.name not in left_type_vars:
        return [(right, left)] + get_unifier(replace(constraints[1:], right, left))
    elif left.is_func_type() and right.is_func_type():
        return get_unifier(constraints[1:] + [(left.premise, right.premise), (left.conclusion, right.conclusion)])
    else:  # Я еще не сделал нормальную обработку ошибок
        return [(Type('Error'), Type('Error'))]


if __name__ == '__main__':
    term = ''.join(sys.argv[1:])

    tree = parser_.parse(term)
    res = get_type_and_constraints(tree, {}, [])

    main_type = res[0]
    unifier = get_unifier(res[2])
    print(main_type.get_unified_type(unifier))
