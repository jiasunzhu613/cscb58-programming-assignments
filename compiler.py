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
class FunctionMetadata:
    type: TType
    offset: int # in bytes from R11

@dataclass
class FunctionInformation:
    paramTypes: list[TType]
    returnType: TType
    varTable: dict[str, TType]

def checkTyped(expr_types: ExpressionTypes, expressions: list[Expression], types: list[TType]):
    return all([expr_types[expressions[i]] == types[i] for i in range(len(expressions))])

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
            # expr_types[node] = node.type
            # expr_types[VarTarget(name = node.name)] = node.type # This is used later for assignments, might not be needed
            f_current.varTable[node.name] = node.type
        case VarAccess():
            if node.target not in f_current.varTable:
                raise VariableNotDefinedError(f"Variable '{node.target}' not defined", node)
        case DerefAccess():
            expr_types |= typecheckNode(node.address)

            # TODO: should this check if address is NULL?
            if expr_types[node.address] != TType.IntPtr:
                raise ExpressionTypeMismatchError("Must be dereferencing a pointer")
        case AddressOf():
            pass # TODO: does this need a case?
        case VarTarget():
            expr_types[node] = f_current.varTable[node.name]
        case DerefTarget():
            expr_types |= typecheckNode(node.address)

            if expr_types[node.address] == TType.Int:
                raise ExpressionTypeMismatchError("Integer cannot be dereferenced", node)
            
            expr_types[node] = TType.Int
        case UnExp():
            expr_types |= typecheckNode(node.exp)

            match node.op:
                case UnaryOp.Not | UnaryOp.Negate:
                    # Make sure the expression is Int
                    if expr_types[node.exp] != TType.Int:
                        raise ExpressionTypeMismatchError("Expression needs to be integer type", node)
                    
                    expr_types[node] = TType.Int
                case UnaryOp.Address:
                    # we are able to take address of any type
                    expr_types[node] = TType.IntPtr
            
        case BinExp():
            expr_types |= typecheckNode(node.left)
            expr_types |= typecheckNode(node.right)

            match node.op:
                case BinaryOp.Plus:
                    if expr_types[node.left] == TType.IntPtr and expr_types[node.right] == TType.IntPtr:
                        raise ExpressionTypeMismatchError("Cannot add IntPtr and IntPtr", node)
                    
                    if checkTyped(expr_types, [node.left, node.right], [TType.Int, TType.Int]):
                        expr_types[node] = TType.Int
                    elif checkTyped(expr_types, [node.left, node.right], [TType.IntPtr, TType.Int]):
                        expr_types[node] = TType.IntPtr
                    elif checkTyped(expr_types, [node.left, node.right], [TType.Int, TType.IntPtr]):
                        expr_types[node] = TType.IntPtr

                case BinaryOp.Minus:
                    if expr_types[node.left] == TType.Int and expr_types[node.right] == TType.IntPtr:
                        raise ExpressionTypeMismatchError("Cannot subtract IntPtr from Int", node)

                    if checkTyped(expr_types, [node.left, node.right], [TType.Int, TType.Int]):
                        expr_types[node] = TType.Int
                    elif checkTyped(expr_types, [node.left, node.right], [TType.IntPtr, TType.Int]):
                        expr_types[node] = TType.IntPtr
                    elif checkTyped(expr_types, [node.left, node.right], [TType.IntPtr, TType.IntPtr]):
                        expr_types[node] = TType.Int

                case BinaryOp.Multiply:
                    if expr_types[node.left] != TType.Int and expr_types[node.right] == TType.Int:
                        raise ExpressionTypeMismatchError("Cannot multiply non integer expressions", node)
                    expr_types[node] = TType.Int

                case BinaryOp.Divide:
                    if expr_types[node.left] != TType.Int and expr_types[node.right] == TType.Int:
                        raise ExpressionTypeMismatchError("Cannot divide non integer expressions", node)
                    expr_types[node] = TType.Int
                
                case BinaryOp.Ge | BinaryOp.Le | BinaryOp.Lt | BinaryOp.Eq | BinaryOp.Ne | BinaryOp.Gt:
                    if expr_types[node.left] != expr_types[node.right]:
                        raise ExpressionTypeMismatchError("Cannot compare two expressions of differing type")
                    expr_types[node] = TType.Int # comparison will always result in int type

        case Call():
            # check if target exists
            if node.target not in f_table:
                raise FunctionNotDefinedError(f"Function named '{node.target}' is not defined", node)
            
            # check if argument types match parameter types
            for arg in node.arguments:
                expr_types |= typecheckNode(arg)

            # Length check
            target_fn_param_types = f_table[node.target].paramTypes
            if len(node.arguments) != len(target_fn_param_types):
                raise ArgumentCountMismatchError(
                    f"Function '{node.target}' takes {len(f_table[node.target].paramTypes)}\
                        arguments but only received{len(node.arguments)} arguments", node)
            
            # Type check
            for i in range(len(node.arguments)):
                if expr_types[node.arguments[i]] != target_fn_param_types[i]:
                    raise ArgumentTypeMismatchError(f"Function '{node.target}' received {expr_types[node.arguments[i]]} but needed {target_fn_param_types[i]} for argument {i}", node)

            expr_types[node] = f_table[node.target].returnType
        
        case WhileLoop():
            # check if the condition is proper
            expr_types |= typecheckNode(node.test)
            if expr_types[node.test] != TType.Int:
                raise ExpressionTypeMismatchError("Test for while loop should be Int typed", node)
            
            expr_types |= typecheckNode(node.body)

        case If():
            # check if the condition is proper
            expr_types |= typecheckNode(node.test)
            if expr_types[node.test] != TType.Int:
                raise ExpressionTypeMismatchError("Test for while loop should be Int typed", node)
            
            expr_types |= typecheckNode(node.body)

        case Assign():
            expr_types |= typecheckNode(node.left, f_table, f_current)
            expr_types |= typecheckNode(node.right, f_table, f_current)

            if expr_types[node.left] != expr_types[node.right]:
                raise AssignmentTypeMismatchError("Assignment type mismatch", node)

            expr_types[node] = expr_types[node.left]

        case Block():
            for line in node.body:
                expr_types |= typecheckNode(line)

        # Have to propagate local var table in this case
        case Function(): # A typecheck for function can come from a Call instance
            # TODO: explicit check for tmain types
            for param in node.parameters:
                expr_types |= typecheckNode(param, f_table, f_current)
            for var_def in node.local_vars:
                expr_types |= typecheckNode(var_def, f_table, f_current)

            expr_types |= typecheckNode(node.body, f_table, f_current)
        case _:
            print("DEBUG: this default case should NEVER be invoked")
    
    return expr_types


def generateNode(node, expr_types: ExpressionTypes, f_table: SymbolTable, f_current: FunctionInformation) -> list[LabeledAssemblyCode | AssemblyCode]:
    # You may modify this function and its input arguments as you'd like.

    # TODO: Implement assembly code generation for each node type and add the generated instructions to assembly_code
    # The minimum required cases for the first checkpoint have been added for you
    assembly_code: list[LabeledAssemblyCode | AssemblyCode] = []
    match node:
        case Function():
            # Need to figure out offsets? for parameters, for local_vars, and then store them in expr_types?

            # Generate code for body
            assembleCode.append(generateNode(node.body, expr_types, f_table, f_current))
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
    
    # Check if tmain is defined
    if "tmain" not in f_table:
        raise FunctionNotDefinedError("not entry point tmain")
    
    # TODO: add the 5 builtin functions to the f_table
    
    # Run typechecking on each function and add returned types to expr_types
    for function in input_fs:
        expr_types = expr_types | typecheckNode(function, f_table, f_table[function.name])

    return (expr_types, f_table)


def generate(input_fs: list[Function], expr_types: ExpressionTypes, f_table: SymbolTable) -> list[list[LabeledAssemblyCode | AssemblyCode]]:
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
    assembly_code: list[list[LabeledAssemblyCode | AssemblyCode]] = []

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
