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

# Built in function
from malloc_free import CODE as MEMORY_CODE
from print import CODE as PRINT_CODE
from put_get_char import CODE as PUT_GET_CHAR_CODE


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

global_counter = {"literal_pool": {},
                  "while": {},
                  "if": {}}
global_literal_pool = {}
binop_cpsr_mapping = {
    BinaryOp.Ge: Cond.GE,
    BinaryOp.Le: Cond.LE,
    BinaryOp.Lt: Cond.LT,
    BinaryOp.Eq: Cond.EQ,
    BinaryOp.Ne: Cond.NE,
    BinaryOp.Gt: Cond.GT
}

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
            
            expr_types[node] = f_current.varTable[node.target]
        case DerefAccess():
            expr_types |= typecheckNode(node.address, f_table, f_current)

            # TODO: should this check if address is NULL?
            if expr_types[node.address] != TType.IntPtr:
                raise ExpressionTypeMismatchError("Must be dereferencing a pointer")
            
            # We only have 1 level of indirection
            expr_types[node] = TType.Int
        case AddressOf():
            expr_types |= typecheckNode(node.target, f_table, f_current)

            # TODO: should this check if address is NULL?
            if expr_types[node.target] != TType.Int:
                raise ExpressionTypeMismatchError("Must be taking address of Type Int")
            
            # We only have 1 level of indirection
            expr_types[node] = TType.IntPtr
        case VarTarget():
            expr_types[node] = f_current.varTable[node.name]
        case DerefTarget():
            expr_types |= typecheckNode(node.address, f_table, f_current)

            if expr_types[node.address] != TType.IntPtr:
                raise ExpressionTypeMismatchError("Integer cannot be dereferenced", node)
            
            expr_types[node] = TType.Int
        case UnExp():
            expr_types |= typecheckNode(node.exp, f_table, f_current)

            match node.op:
                case UnaryOp.Negate:
                    if expr_types[node.exp] != TType.Int:
                        raise ExpressionTypeMismatchError("Expression needs to be integer type", node)
                    
                    expr_types[node] = TType.Int
                case UnaryOp.Not:
                    # we are able to take logical not of a pointer
                    # Result of logical not will always be Int typed
                    # NULL => 0
                    # all other pointer values => 1
                    expr_types[node] = TType.Int
                # case UnaryOp.Address:
                #     # we are able to take address of any type
                #     expr_types[node] = TType.IntPtr
            
        case BinExp():
            expr_types |= typecheckNode(node.left, f_table, f_current)
            expr_types |= typecheckNode(node.right, f_table, f_current)

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

                case BinaryOp.Subtract:
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
                expr_types |= typecheckNode(arg, f_table, f_current)

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
            expr_types |= typecheckNode(node.test, f_table, f_current)
            if expr_types[node.test] != TType.Int:
                raise ExpressionTypeMismatchError("Test for while loop should be Int typed", node)
            
            # expr_types |= typecheckNode(node.body)

        case If():
            # check if the condition is proper
            expr_types |= typecheckNode(node.test, f_table, f_current)
            if expr_types[node.test] != TType.Int:
                raise ExpressionTypeMismatchError("Test for while loop should be Int typed", node)
            
            # expr_types |= typecheckNode(node.body)

        case Assign():
            expr_types |= typecheckNode(node.left, f_table, f_current)
            expr_types |= typecheckNode(node.right, f_table, f_current)

            if expr_types[node.left] != expr_types[node.right]:
                raise AssignmentTypeMismatchError("Assignment type mismatch", node)

            # expr_types[node] = expr_types[node.left]

        case Block():
            for line in node.body:
                expr_types |= typecheckNode(line, f_table, f_current)

        # Have to propagate local var table in this case
        case Function(): # A typecheck for function can come from a Call instance
            # TODO: explicit check for tmain types
            for param in node.parameters:
                expr_types |= typecheckNode(param, f_table, f_current)
            for var_def in node.local_vars:
                expr_types |= typecheckNode(var_def, f_table, f_current)

            expr_types |= typecheckNode(node.body, f_table, f_current)
            expr_types |= typecheckNode(node.retExpr, f_table, f_current)
        case _:
            print("DEBUG: this default case should NEVER be invoked")
    
    return expr_types

def push(assembly_code, register):
    assembly_code.append(Sub(Reg(13), Reg(13), Word(4)))
    assembly_code.append(Str(Reg(register), Reg(13), Word(0)))

def pop(assembly_code, register):
    assembly_code.append(Ldr(Reg(register), Reg(13), Word(0)))
    assembly_code.append(Add(Reg(13), Reg(13), Word(4)))

def assign_literal(f_name, value):
    global global_counter, global_literal_pool
    if f_name not in global_counter["literal_pool"]:
        global_counter["literal_pool"][f_name] = 0

    name = f"literal_pool_{f_name}_{global_counter["literal_pool"][f_name]}"
    
    if f_name not in global_literal_pool:
        global_literal_pool[f_name] = {}
        
    global_literal_pool[f_name][name] = value
    global_counter["literal_pool"][f_name] += 1

    return name

def assign_while_labels(f_name):
    global global_counter
    if f_name not in global_counter["while"]:
        global_counter["while"][f_name] = 0
    
    start_label = f"while_start_{global_counter["while"][f_name]}"
    end_label = f"while_end_{global_counter["while"][f_name]}"

    global_counter["while"][f_name] += 1

    return (start_label, end_label)

def assign_if_label(f_name):
    global global_counter
    if f_name not in global_counter["if"]:
        global_counter["if"][f_name] = 0
    
    else_label = f"else_{global_counter["if"][f_name]}"
    end_label = f"if_end_{global_counter["if"][f_name]}"

    global_counter["if"][f_name] += 1

    return (else_label, end_label)


def generateNode(node, expr_types: ExpressionTypes, f_name: str, f_table: SymbolTable, f_current: FunctionInformation, stack_offset: dict[str, int] = None) -> list[LabeledAssemblyCode | AssemblyCode]:
    # You may modify this function and its input arguments as you'd like.

    # TODO: Implement assembly code generation for each node type and add the generated instructions to assembly_code
    # The minimum required cases for the first checkpoint have been added for you
    assembly_code: list[LabeledAssemblyCode | AssemblyCode] = []
    match node:
        case Function():
            # Push the function name as a label
            assembly_code.append(Label(node.name))

            # Push all stack related things on
            # We know by this step all value in param and local are unique
            # Push all parameters, local context, and local vars onto stack
            # Note parameters are already pushed onto stack by user, except r0-r3

            # There are 9 elements from callee saved, but FP points directly at the last element, so just 8 to account for 
            length_above_fp = 8 + len(node.parameters)
            offset_table = {}
            for i in range(len(node.parameters)):
                offset_table[node.parameters[len(node.parameters) - i - 1].name] = 4 * (length_above_fp - i)
            # Push r3 to r0
            # arg0 => r0, arg1 => r1, arg2 => r2, arg3 => r3
            for i in range(min(4, len(node.parameters)) - 1, -1, -1):
                push(assembly_code, i)
            
            # Push R4 - R11 and R14 onto stack
            # R11 is saving previous FP
            for i in range(4, 11 + 1):
                push(assembly_code, i)

            # Push R14 onto stack
            push(assembly_code, 14)
            assembly_code.append(Mov(Reg(11), Reg(13)))

            # Local variables
            for i in range(len(node.local_vars)):
                offset_table[node.local_vars[i].name] = -4 * (i + 1)
                assembly_code.extend(generateNode(node.local_vars[i], expr_types, f_name, f_table, f_current))
            print(offset_table, file=sys.stderr)
            
            # Generate code for body
            assembly_code.extend(generateNode(node.body, expr_types, f_name, f_table, f_current, offset_table))

            # Generate code for return
            # Codegen will put immediate value onto stack so we just read it into R0
            assembly_code.extend(generateNode(node.retExpr, expr_types, f_name, f_table, f_current, offset_table))
            pop(assembly_code, 0)

            # Set return statement
            # We set return value in R0 and we also need to call Bx(Reg(14)))
            # Also need to cleanup stack first, so set SP to the position of FP and then load values from stack back into registers (callee saved values)
            assembly_code.append(Mov(Reg(13), Reg(11))) # Move address at R11 into R13
            # Pop R14 off stack
            pop(assembly_code, 14)
            # Pop R4 to R11 off stack (make sure to go in reverse order form 11 to 4)
            for i in range(11, 4-1, -1):
                assembly_code.append(Ldr(Reg(i), Reg(13), Word(0)))
                assembly_code.append(Add(Reg(13), Reg(13), Word(4)))
            
            # Pop r3 to r0 into scratch
            # arg0 => r0, arg1 => r1, arg2 => r2, arg3 => r3
            for i in range(min(4, len(node.parameters)) - 1, -1, -1):
                pop(assembly_code, 12)
            # Branch back to where function was called
            assembly_code.append(Bx(Reg(14)))
        case VarDef():
            assembly_code.append(Mov(Reg(12), Word(0))) # Move 0 into scratch register to move onto stack after
            push(assembly_code, 12)
        case Constant():
            # WARNING: If the constant is really big, we cant just mov directly!
            if isinstance(node.value, int):
                # put onto scratch and then push into stack?
                if 0 <= node.value <= 255: # Limit for 8bit values
                    assembly_code.append(Mov(Reg(12), Word(node.value)))
                else:
                    # Literal pool, register value into literal pool?
                    label = assign_literal(f_name, node.value)
                    assembly_code.append(LdrRel(Reg(12), LabelRef(label)))
            else:
                assembly_code.append(Mov(Reg(12), Word(0)))
            push(assembly_code, 12)
        case VarAccess(): # Use stack_offset to find address, then push the address onto stack
            # Just take R11 + stack_offset[node.name] => into scratch
            # but need to know which side VarAccess is on tho???
            # assembly_code.append(Add(Reg(12), Reg(11), Word(stack_offset[node.target])))
            if 0 <= stack_offset[node.target] < 2**12 - 1:
                assembly_code.append(Ldr(Reg(12), Reg(11), Word(stack_offset[node.target])))
            else:
                assembly_code.extend(generateNode(Constant(stack_offset[node.target]), expr_types, f_name, f_table, f_current, stack_offset))
                pop(assembly_code, 12)
                assembly_code.append(Add(Reg(12), Reg(11), Reg(12)))
                assembly_code.append(Ldr(Reg(12), Reg(12), Word(0)))
            push(assembly_code, 12)
        case BinExp():
            assembly_code.extend(generateNode(node.left, expr_types, f_name, f_table, f_current, stack_offset))
            assembly_code.extend(generateNode(node.right, expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 5) # load right side into R5
            pop(assembly_code, 4) # load left side into R4

            # TODO: handle special cases in addition, mult, sub nad divide
            match node.op:
                case BinaryOp.Plus:
                    if expr_types[node.left] == TType.IntPtr and expr_types[node.right] == TType.Int:
                        assembly_code.append(Mov(Reg(12), Word(4)))
                        assembly_code.append(Mul(Reg(5), Reg(5), Reg(12)))
                    elif expr_types[node.left] == TType.Int and expr_types[node.right] == TType.IntPtr:
                        assembly_code.append(Mov(Reg(12), Word(4)))
                        assembly_code.append(Mul(Reg(4), Reg(4), Reg(12)))
                    assembly_code.append(Add(Reg(4), Reg(4), Reg(5)))
                case BinaryOp.Multiply:
                    assembly_code.append(Mul(Reg(4), Reg(4), Reg(5)))
                case BinaryOp.Subtract:
                    if expr_types[node.left] == TType.Int and expr_types[node.right] == TType.Int:
                        assembly_code.append(Sub(Reg(4), Reg(4), Reg(5)))
                    elif expr_types[node.left] == TType.IntPtr and expr_types[node.right] == TType.Int:
                        assembly_code.append(Mov(Reg(12), Word(4)))
                        assembly_code.append(Mul(Reg(5), Reg(5), Reg(12)))
                        assembly_code.append(Sub(Reg(4), Reg(4), Reg(5)))
                    elif expr_types[node.left] == TType.Int and expr_types[node.right] == TType.IntPtr:
                        assembly_code.append(Mov(Reg(12), Word(4)))
                        assembly_code.append(Sub(Reg(4), Reg(4), Reg(5)))
                        assembly_code.append(SDiv(Reg(4), Reg(4), Reg(12)))
                case BinaryOp.Divide:
                    assembly_code.append(SDiv(Reg(4), Reg(4), Reg(5)))
                case BinaryOp.Ge | BinaryOp.Le | BinaryOp.Lt | BinaryOp.Eq | BinaryOp.Ne | BinaryOp.Gt:
                    assembly_code.append(Mov(Reg(12), Word(0)))
                    assembly_code.append(Cmp(Reg(4), Reg(5)))
                    assembly_code.append(Mov(Reg(12), Word(1), binop_cpsr_mapping[node.op]))
                    assembly_code.append(Mov(Reg(4), Reg(12)))
            push(assembly_code, 4)
        case UnExp():
            assembly_code.extend(generateNode(node.exp, expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 4)
            match node.op:
                case UnaryOp.Not:
                    assembly_code.append(Cmp(Reg(4), Word(0)))
                    assembly_code.append(Mov(Reg(4), Word(0), Cond.NE))
                    assembly_code.append(Mov(Reg(4), Word(1), Cond.EQ))
                case UnaryOp.Negate:
                    # TODO: handle -2^31 case in twos complement
                    assembly_code.append(Mov(Reg(12), Word(0)))
                    assembly_code.append(Sub(Reg(12), Reg(12), Word(1)))
                    assembly_code.append(Mul(Reg(4), Reg(4), Reg(12)))
            push(assembly_code, 4)
        case Assign():
            # Storing into memory address on stack
            assembly_code.extend(generateNode(node.left, expr_types, f_name, f_table, f_current, stack_offset))
            assembly_code.extend(generateNode(node.right, expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 4) # pop value of expression into r0
            pop(assembly_code, 5) # pop address of lvalue into r4
            assembly_code.append(Str(Reg(4), Reg(5), Word(0)))
        case VarTarget():
            assembly_code.extend(generateNode(Constant(stack_offset[node.name]), expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 0)
            assembly_code.append(Add(Reg(0), Reg(11), Reg(0))) # TODO: check if works
            push(assembly_code, 0) # Push address of lvalue onto stack
        case DerefTarget():
            assembly_code.extend(generateNode(node.address, expr_types, f_name, f_table, f_current, stack_offset))
        case DerefAccess():
            assembly_code.extend(generateNode(node.address, expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 4)
            assembly_code.append(Ldr(Reg(4), Reg(4), Word(0)))
            push(assembly_code, 4)
        case AddressOf():
            assembly_code.extend(generateNode(node.target, expr_types, f_name, f_table, f_current, stack_offset))
        case WhileLoop():
            # label
            # check
            # end if check fails
            # go body and loop
            start_label, end_label = assign_while_labels(f_name)

            assembly_code.append(Label(start_label))
            assembly_code.extend(generateNode(node.test, expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 0)
            assembly_code.append(Cmp(Reg(0), Word(0))) # If test failed, we exit
            assembly_code.append(B(LabelRef(end_label), Cond.EQ))
            assembly_code.extend(generateNode(node.body, expr_types, f_name, f_table, f_current, stack_offset))
            assembly_code.append(B(LabelRef(start_label)))

            assembly_code.append(Label(end_label))
        case If():
            else_label, end_label = assign_if_label(f_name)

            assembly_code.extend(generateNode(node.test, expr_types, f_name, f_table, f_current, stack_offset))
            pop(assembly_code, 0)
            assembly_code.append(Cmp(Reg(0), Word(0))) # If test failed, we exit
            assembly_code.append(B(LabelRef(else_label), Cond.EQ))
            assembly_code.extend(generateNode(node.trueCase, expr_types, f_name, f_table, f_current, stack_offset))
            assembly_code.append(B(LabelRef(end_label)))

            assembly_code.append(Label(else_label))
            assembly_code.extend(generateNode(node.falseCase, expr_types, f_name, f_table, f_current, stack_offset))
            assembly_code.append(Label(end_label))
        case Block():
            for line in node.body:
                assembly_code.extend(generateNode(line, expr_types, f_name, f_table, f_current, stack_offset))
        case Call():
            # set up all arguments, make sure to perserve caller saved stuff
            # go from end to start and generate argument expressions
            # pop top 4 into registers
            # call_f_information = f_table[node.target]
            for i in range(len(node.arguments) - 1, -1, -1):
                assembly_code.extend(generateNode(node.arguments[i], expr_types, f_name, f_table, f_current, stack_offset))
            
            for i in range(min(4, len(node.arguments))):
                pop(assembly_code, i)
            
            assembly_code.append(Bl(LabelRef(node.target)))

            for i in range(max(0, len(node.arguments) - 4)):
                pop(assembly_code, 12) # pop function arguments 4 to n off stack into scratch

            push(assembly_code, 0)

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
    
    # Add builtin function definitions
    f_table["putchar"] = FunctionInformation(paramTypes=[TType.Int], returnType=TType.Int, varTable={})
    f_table["getchar"] = FunctionInformation(paramTypes=[], returnType=TType.Int, varTable={})
    f_table["print"] = FunctionInformation(paramTypes=[TType.Int], returnType=TType.Int, varTable={})
    f_table["malloc"] = FunctionInformation(paramTypes=[TType.Int], returnType=TType.IntPtr, varTable={})
    f_table["free"] = FunctionInformation(paramTypes=[TType.IntPtr], returnType=TType.Int, varTable={})
    
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
        asm_code = generateNode(function, expr_types, function.name, f_table, f_table[function.name])
        if function.name in global_literal_pool:
            for key, value in global_literal_pool[function.name].items():
                asm_code.append(Label(key))
                asm_code.append(Word(value))
        assembly_code.append(asm_code)


    return assembly_code


def compileCode(input_fs: list[Function], output = sys.stdout.buffer):
    try:
        expr_types, f_table = typecheck(input_fs)
        asm_fns = generate(input_fs, expr_types, f_table)
        concatAsm = [elem for sublist in asm_fns for elem in sublist]

        # Append built in function
        concatAsm.extend(MEMORY_CODE)
        concatAsm.extend(PRINT_CODE)
        concatAsm.extend(PUT_GET_CHAR_CODE)

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
