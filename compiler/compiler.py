from decl import *
from type import *
from expression import *
from lvalue import *
from statement import *
from codetypes import *


type ExpressionTypes = dict[Expression, TType]
type SymbolTable = dict[str, FunctionInformation]


@dataclass
class FunctionInformation:
    paramTypes: list[TType]
    returnType: TType
    varTable: dict[str, TType]


ftable: dict[str, FunctionInformation] = {}


def typeCheck(node) -> dict[Expression|LValue, TType]:
    match node:
        case Function():
            pass
        case VarDef():
            pass
        case TType():
            pass
        case Constant():
            pass
    # ...
    return {}


def codeGen(node) -> list[LabeledAssemblyCode]:
    match node:
        case Function():
            pass
        case VarDef():
            pass
        case TType():
            pass
        case Constant():
            pass
    # ...
    return []


def generate(fs: list[Function]) -> list[list[LabeledAssemblyCode]]:
    assembly_code: list[list[LabeledAssemblyCode]] = []
    # still figuring this stuff out right now....
    # try: 
    #     for function in fs:
    #         ftable[function.name] = FunctionInformation(function.parameters, function.retType, {})
    #         expr_types = typeCheck(function)
    #         asm_code = codeGen(function)
    #         assembly_code.append(asm_code)
    # except BaseException as e:
    #     print(e)
    return assembly_code

