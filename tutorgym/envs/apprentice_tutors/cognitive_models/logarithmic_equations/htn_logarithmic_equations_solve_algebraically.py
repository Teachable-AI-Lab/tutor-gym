from random import randint, choice

import sympy as sp
from sympy import latex, symbols, expand, sstr, Eq, solve
from sympy.parsing.latex._parse_latex_antlr import parse_latex
import re

from random import randint
from shop2.domain import Task, Operator, Method
# from shop2.planner import SHOP2
from shop2.fact import Fact
from shop2.conditions import Filter
from shop2.common import V

from htn_cognitive_models import HTNCognitiveModel
from htn_cognitive_models import htn_loaded_models
from studymaterial import studymaterial


def replace_log_with_ln(equation):
    return equation.replace('\log', '\ln')

def htn_logarithmic_equations_solve_algebraically_problem():
    x = symbols('x')
    a, c1, c2 = randint(-10, 10), randint(-10, 10), randint(-10, 10)
    while not (c2-c1) or sp.Abs(a) <=1:
      a, c1, c2 = randint(-10, 10), randint(-10, 10), randint(-10, 10)
    equation = latex(Eq(a*sp.ln(x)+c1, c2, evaluate=False))
    equation = replace_log_with_ln(equation)
    return equation

def coeff0_to_rhs(init_value):
        x = symbols('x')
        lhs, rhs = parse_latex(init_value).lhs, parse_latex(init_value).rhs
        equation = Eq(lhs-lhs.coeff(x, 0), rhs-lhs.coeff(x, 0))
        print("EQUATION", equation)
        answer = re.compile(re.sub(r'([-+^()*])', r'\\\1', sstr(equation, order="grlex").replace("-1*", "-")))
        hint = replace_log_with_ln(latex(equation).replace("\\left(-1\\right) ", "-"))
        value = tuple([(answer, hint)])
        return value

def coefflnx_to_rhs(init_value):
        x = symbols('x')
        lhs, rhs = parse_latex(init_value).lhs, parse_latex(init_value).rhs
        equation = Eq(lhs-lhs.coeff(x, 0), rhs-lhs.coeff(x, 0))
        lhs, rhs = equation.lhs, equation.rhs
        constant = lhs.args[0]
        if lhs.args[1].is_integer:
            constant *= lhs.args[1]
        equation = Eq(lhs.args[-1], rhs/constant)
        
        answer = re.compile(re.sub(r'([-+^()*])', r'\\\1', sstr(equation, order="grlex")))
        hint = replace_log_with_ln(latex(equation).replace("\\left(-1\\right) ", "-"))
        value = tuple([(answer, hint)])
        return value

def exponential_both_sides(init_value):
        x = symbols('x')
        lhs, rhs = parse_latex(init_value).lhs, parse_latex(init_value).rhs
        equation = Eq(lhs-lhs.coeff(x, 0), rhs-lhs.coeff(x, 0))
        lhs, rhs = equation.lhs, equation.rhs
        constant = lhs.args[0]
        if lhs.args[1].is_integer:
            constant *= lhs.args[1]
        equation = Eq(lhs.args[-1], rhs/constant)
        print("EQUATION", equation)
        equation = parse_latex(latex(Eq(x, sp.E**equation.rhs)))
        answer = re.compile(re.sub(r'([-+^()*])', r'\\\1', sstr(equation, order="grlex")))
        hint = replace_log_with_ln(latex(equation))
        value = tuple([(answer, hint)])
        return value


Domain = {
    'done': Operator(head=('done', V('kc')),
                     precondition=[Fact(start=True)],
                     effects=[Fact(field='done', value=((re.compile('x'),),), kc=V('kc'), answer=True)],
    ),

    'coeff0_to_rhs': Operator(head=('coeff0_to_rhs', V('equation'), V('kc')),
                                precondition=Fact(field=V('equation'), value=V('eq'), answer=False),
                                effects=[Fact(field='coeff0_to_rhs', value=(coeff0_to_rhs, V('eq')), kc=V('kc'), answer=True)],
    ),

    'coefflnx_to_rhs': Operator(head=('coefflnx_to_rhs', V('equation'), V('kc')),
                                precondition=Fact(field=V('equation'), value=V('eq'), answer=False),
                                effects=[Fact(field='coefflnx_to_rhs', value=(coefflnx_to_rhs, V('eq')), kc=V('kc'), answer=True)],
    ),

    'exponential_both_sides': Operator(head=('exponential_both_sides', V('equation'), V('kc')),
                                    precondition=Fact(field=V('equation'), value=V('eq'), answer=False),
                                    effects=[Fact(field='exponential_both_sides', value=(exponential_both_sides, V('eq')), kc=V('kc'), answer=True)],
    ),


    'solve': Method(head=('solve', V('equation')),
                    preconditions=[
                        Fact(scaffold='level_2'),
                        Fact(scaffold='level_1'),
                        Fact(scaffold='level_0'),
                    ],
                    subtasks=[
                        [
                            Task(head=('coeff0_to_rhs', V('equation'), ('coeff0_to_rhs',)), primitive=True),
                            Task(head=('coefflnx_to_rhs', V('equation'), ('coefflnx_to_rhs',)), primitive=True),
                            Task(head=('exponential_both_sides', V('equation'), ('exponential_both_sides',)), primitive=True),
                            Task(head=('done', ('done',)), primitive=True)
                        ],

                        [
                            Task(head=('coeff0_to_rhs', V('equation'), ('coeff0_to_rhs',)), primitive=True),
                            Task(head=('exponential_both_sides', V('equation'), ('coefflnx_to_rhs','exponential_both_sides')), primitive=True),
                            Task(head=('done', ('done',)), primitive=True)
                        ],

                        [
                            Task(head=('exponential_both_sides', V('equation'), ('coeff0_to_rhs', 'coefflnx_to_rhs', 'exponential_both_sides')), primitive=True),
                            Task(head=('done', ('done',)), primitive=True)
                        ]
                    ]
    ),
}

def htn_logarithmic_equations_solve_algebraically_kc_mapping():

    kcs = {
        "coeff0_to_rhs": "coeff0_to_rhs",
        "coefflnx_to_rhs": "coefflnx_to_rhs",
        "exponential_both_sides": "exponential_both_sides",
        "done": "done"
    }
    return kcs


def htn_logarithmic_equations_solve_algebraically_intermediate_hints():
    hints = {
        "coeff0_to_rhs": ["Take the natural log of both sides of the equation."],
        "coefflnx_to_rhs": ["Set the right hand side equal to zero."],
        "exponential_both_sides": ["Factor the left hand side of the equation using FOIL."],
        'done': [" You have solved the problem. Click the done button!"]
    }
    return hints

def htn_logarithmic_equations_solve_algebraically_studymaterial():
    study_material = studymaterial["logarithmic_equations_solve_algebraically"]
    return study_material

htn_loaded_models.register(HTNCognitiveModel('htn_logarithmic_equations',
                                             'htn_logarithmic_equations_solve_algebraically',
                                             Domain,
                                             Task(head=('solve', 'equation'), primitive=False),
                                             htn_logarithmic_equations_solve_algebraically_problem,
                                             htn_logarithmic_equations_solve_algebraically_kc_mapping(),
                                             htn_logarithmic_equations_solve_algebraically_intermediate_hints(),
                                             htn_logarithmic_equations_solve_algebraically_studymaterial()))