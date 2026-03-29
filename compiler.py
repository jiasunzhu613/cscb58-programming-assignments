import argparse
import importlib
import importlib.util
import sys

from decl import *
from type import *
from codetypes import *
from exprstmt import *
from typecheck_errors import *
from labelasm import assembleCode


type ExpressionTypes = dict[Expression|LValue, TType]
type SymbolTable = dict[str, FunctionInformation]


@dataclass
class FunctionInformation:
    paramTypes: list[TType]
    returnType: TType
    varTable: dict[str, TType]

def typecheckExpression():
    pass

def typecheckStatement():
    pass

def typecheckNode(node, f_table: SymbolTable, f_current: FunctionInformation) -> ExpressionTypes:
    # You may modify this function and its input arguments as you'd like.

    # TODO: Implement typechecking for each node type and add the types of expressions to expr_types
    # The minimum required cases for the first checkpoint have been added for you
    expr_types: ExpressionTypes = {}
    match node:
        case Constant():
            if isinstance(node.value, int):
                expr_types[node] = TType.Int
            else:
                expr_types[node] = TType.IntPtr
        case VarDef(): # Create VarTarget instances 
            expr_types[node] = node.type
            # expr_types[VarTarget(name = node.name)] = node.type # This is used later for assignments, might not be needed
            f_current.varTable[node.name] = node.type
        case VarTarget():
            pass
        case DerefTarget():
            expr_types |= typecheckNode(node.address)

            if isinstance(expr_types[node.address], TType.IntPtr):
                raise ExpressionTypeMismatchError("Target cannot be dereferenced", node)
        case UnExp():
            expr_types |= typecheckNode(node.exp)

            match node.op:
                case UnaryOp.Not | UnaryOp.Negate | UnaryOp.Address:
                    # Make sure the expression is Int
                    if not isinstance(expr_types[node.exp], TType.Int):
                        raise ExpressionTypeMismatchError("Expression needs to be integer type", node)
        case BinExp():
            expr_types |= typecheckNode(node.left)
            expr_types |= typecheckNode(node.right)

            match node.op:
                case BinaryOp.Plus:
                case BinaryOp.Subtract:
                case BinaryOp.
        # Have to propagate local var table in this case
        case Function(): # A typecheck for function can come from a Call instance
            for param in node.parameters:
                expr_types |= typecheckNode(param, f_table, f_current)
            for var_def in node.local_vars:
                expr_types |= typecheckNode(var_def, f_table, f_current)

            # check if body is a Block type
            if isinstance(node.body, Block):
                for line in node.body:
                    expr_types |= typecheckNode(line, f_table)
            else:
                expr_types |= typecheckNode(node.body, f_table)
            
            # Check if param types and 
        case Assign():
            expr_types |= typecheckNode(node.left, f_table)
            expr_types |= typecheckNode(node.right, f_table)

            if expr_types[node.left] != expr_types[node.right]:
                raise RuntimeError("Assign type mismatch")

            expr_types[node] = expr_types[node.left]
        case _:
            pass
    
    return expr_types


def generateNode(node, expr_types: ExpressionTypes, f_table: SymbolTable, f_current: FunctionInformation) -> list[LabeledAssemblyCode]:
    # You may modify this function and its input arguments as you'd like.

    # TODO: Implement assembly code generation for each node type and add the generated instructions to assembly_code
    # The minimum required cases for the first checkpoint have been added for you
    assembly_code: list[LabeledAssemblyCode] = []
    match node:
        case Function():
            pass
        case VarDef():
            pass
        case Constant():
            pass
        case VarAccess():
            pass
    # Add more cases for each node type...
    return assembly_code


# We are building ftable here and returning it out
def typecheck(input_fs: list[Function]) -> tuple[ExpressionTypes, SymbolTable]:
    '''Checks type constraints on an input program input_fs, which consists of a list of Function objects.

    Args:
        input_fs: list of Function objects representing the input program
    
    Returns:
        A tuple (expr_types, f_table) where:
            expr_types: a mapping from each expression and lvalue in the program to its type
            f_table: a mapping from each function name to its parameter types, return type, and variable table

    Raises:
        TypeCheckError
     
    Note:
        Do not modify the input arguments to typecheck. You may modify the body as needed.
    '''
    expr_types: ExpressionTypes = {}
    f_table: SymbolTable = {}

    # Initialize function table
    for function in input_fs:
        paramTypes: list[TType] = [param.type for param in function.parameters]
        returnType: TType = function.retType
        f_table[function.name] = FunctionInformation(paramTypes, returnType, {}) # TODO: this dict is the local scoped function local table
    
    # TODO: add the 5 builtin functions to the f_table
    
    # TODO: check if the tmain function was found
    # Run typechecking on each function and add returned types to expr_types
    for function in input_fs:
        expr_types = expr_types | typecheckNode(function, f_table, f_table[function.name])

    return (expr_types, f_table)


def generate(input_fs: list[Function], expr_types: ExpressionTypes, f_table: SymbolTable) -> list[list[LabeledAssemblyCode]]:
    '''Generates assembly code for an input program input_fs, which consists of a list of Function objects.
    
    Args:
        input_fs: list of Function objects representing the input program
        expr_types: a mapping from each expression and lvalue in the program to its type
        f_table: a mapping from each function name to its parameter types, return type, and variable table

    Returns:
        A list of lists of LabeledAssemblyCode, one list for each function in the input program, containing the generated assembly code for that function

    Note:
        Do not modify the input arguments to generate. You may modify the body as you'd like, but its not reccomended.
    '''
    assembly_code: list[list[LabeledAssemblyCode]] = []

    # Generate each function's labeled assembly code
    for function in input_fs:
        asm_code = generateNode(function, expr_types, f_table, f_table[function.name])
        assembly_code.append(asm_code)

    return assembly_code


def compileCode(input_fs: list[Function], output = sys.stdout.buffer):
    try:
        expr_types, f_table = typecheck(input_fs)
        asm_fns = generate(input_fs, expr_types, f_table)
        concatAsm = [elem for sublist in asm_fns for elem in sublist]
        assembleCode(concatAsm, output)
    except TypeCheckError as tc_err:
        print(f"TypeCheck error raised: {tc_err}")

if __name__ == "__main__":
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdout.fileno(  ), os.O_BINARY)

    parser = argparse.ArgumentParser(
                    prog="compiler",
                    description="Assembles a sequence of Function objects")
    parser.add_argument("filename")
    args = parser.parse_args()
    
    spec = importlib.util.spec_from_file_location("code", args.filename)
    assert(not spec is None and not spec.loader is None)
    code = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code)
    compileCode(code.FUNCS) 
