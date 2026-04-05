from enum import Enum
from dataclasses import dataclass


class UnaryOp(Enum):
    Not = 0
    Negate = 1

class BinaryOp(Enum):
    Plus = 1
    Multiply = 2
    Subtract = 3
    Divide = 4
    Ge = 5
    Le = 6
    Lt = 7
    Eq = 8
    Ne = 9
    Gt = 10

# Statements encompass all possible lines sort of

@dataclass(eq=False)
class Statement:
    pass

# Expressions handle some manipulation of data, and performing things on top of variables and Lvalues

@dataclass(eq=False)
class Expression(Statement):
    pass


@dataclass(eq=False)
class LValue:
    pass


# NOTE: We use eq=False to discourage value based equalities and only
# allow equality to happen when the memory address of the underlying variables are the same

# Normal variable Lvalue
@dataclass(eq=False) # TODO: check is this is good
class VarTarget(LValue):
    name: str

# Dereferenced pointer Lvalue

@dataclass(eq=False)
class DerefTarget(LValue):
    address: Expression


@dataclass(eq=False)
class NULL:
    pass


# Expressions
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
class VarAccess(Expression):
    target: str

@dataclass(eq=False)
class DerefAccess(Expression):
    address: Expression

@dataclass(eq=False)
class AddressOf(Expression):
    target: LValue


@dataclass(eq=False)
class Constant(Expression):
    value: int | NULL


# Statements
@dataclass
class Block(Statement):
    body: list[Statement|Expression]


@dataclass
class WhileLoop(Statement):
    test: Expression
    body: Statement # need to check if its a Block type or some other expression, if Block type we will need to iterate


@dataclass
class Assign(Statement):
    left: LValue
    right: Expression


@dataclass
class If(Statement):
    test: Expression
    trueCase: Statement
    falseCase: Statement

