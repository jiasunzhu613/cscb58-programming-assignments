from codetypes import *
from exprstmt import *
from decl import *

FUNCS = [
    Function(
        retType=TType.Int,
        name = "tmain",
        parameters = [VarDef(TType.Int, "arg1"), VarDef(TType.Int, "arg2")],
        local_vars = [VarDef(TType.Int, "i")], # all local vars will be declared here?
        body = Constant(10),
        retExpr = Constant(500)
    )
]