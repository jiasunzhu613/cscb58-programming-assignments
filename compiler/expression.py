from enum import Enum
from dataclasses import dataclass


class UnaryOp(Enum):
    Not = 0
    Negate = 1
    Address = 2


class BinaryOp(Enum):
    Plus = 1
    Minus = 2
    Subtract = 3
    Divide = 4
    Ge = 5
    Le = 6
    Lt = 7
    Eq = 8
    Ne = 9


class Expression:
    pass


@dataclass(eq=False)
class NULL:
    pass


@dataclass(eq=False)
class BinExp(Expression):
    left: Expression
    op: BinaryOp
    right: Expression


@dataclass(eq=False)
class UnExp(Expression):
    op: UnaryOp
    exp: Expression


@dataclass(eq=False)
class Call(Expression):
    target: str
    arguments: list[Expression]


@dataclass(eq=False)
class Constant(Expression):
    value: int | NULL