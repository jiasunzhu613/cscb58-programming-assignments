from dataclasses import dataclass
from expression import *
from lvalue import LValue


@dataclass
class Statement:
    pass


@dataclass
class Block(Statement):
    body: list[Statement]


@dataclass
class WhileLoop(Statement):
    test: Expression
    body: Statement


@dataclass
class Assign(Statement):
    left: LValue
    right: Expression


@dataclass
class If(Statement):
    test: Expression
    trueCase: Statement
    falseCase: Statement

