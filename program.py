from codetypes import *
from exprstmt import *
from decl import *

FUNCS = [
    Function(
        retType=TType.Int,
        name = "tmain",
        parameters = [VarDef(TType.Int, "arg1"), VarDef(TType.Int, "arg2")],
        local_vars = [VarDef(TType.IntPtr, "a"), 
                      VarDef(TType.IntPtr, "b"),
                      VarDef(TType.IntPtr, "c"),
                      VarDef(TType.Int, "i_4999"), 
                      VarDef(TType.Int, "i_0")], # all local vars will be declared here? [VarDef(TType.Int, f"i_{i}") for i in range(5000)
        body = Block(
            [
                If(BinExp(VarAccess("arg1"), BinaryOp.Eq, Constant(500)), 
                  Assign(VarTarget("i_4999"), Constant(600)), 
                  Assign(VarTarget("i_4999"), Constant(700))),
                # Assign(VarTarget("a"), AddressOf(VarTarget("i_4999"))),
                # Assign(VarTarget("i_0"), DerefAccess(VarAccess("a"))),
                # Assign(VarTarget("i_0"), BinExp(VarAccess("i_0"), BinaryOp.Plus, Constant(10))),
                # Assign(VarTarget("i_0"), Call("stupid", [VarAccess("i_0")])),
                # Assign(VarTarget("a"), Call("malloc", [VarAccess("i_0")])),
                # Call("print", [VarAccess("arg1")]),
                # Assign(VarTarget("arg2"), Call("getchar", [])),
                # Call("putchar", [VarAccess("arg2")])
                # Assign(VarTarget("a"), Call("malloc", [Constant(4)])),
                # Assign(VarTarget("b"), Call("malloc", [Constant(4)])),
                # Assign(VarTarget("c"), Call("malloc", [Constant(4)])),

                # Assign(DerefTarget(VarAccess("a")), Constant(1)),
                # Assign(DerefTarget(VarAccess("b")), Constant(10)),
                # Assign(DerefTarget(VarAccess("c")), Constant(100)),
                # WhileLoop(BinExp(DerefAccess(VarAccess("c")), BinaryOp.Lt, Constant(300)), 
                #           Assign(DerefTarget(VarAccess("c")), 
                #                  BinExp(DerefAccess(VarAccess("c")), BinaryOp.Plus, Constant(1)))),

                # Assign(VarTarget("i_0"), BinExp(VarAccess("i_0"), BinaryOp.Plus, DerefAccess(VarAccess("a")))),
                # Assign(VarTarget("i_0"), BinExp(VarAccess("i_0"), BinaryOp.Plus, DerefAccess(VarAccess("b")))),
                # Assign(VarTarget("i_0"), BinExp(VarAccess("i_0"), BinaryOp.Plus, DerefAccess(VarAccess("c")))),

                # Call("free", [VarAccess("a")]),
                # Call("free", [VarAccess("c")]),
                # Assign(VarTarget("a"), Call("malloc", [Constant(4)])),
                # Assign(DerefTarget(VarAccess("a")), Constant(500)),
                # Should access i_4999
                Assign(VarTarget("i_0"), BinExp(AddressOf(VarTarget("i_0")), BinaryOp.Subtract, AddressOf(VarTarget("i_4999")))),
                
                # Call("free", [VarAccess("a")]),
                # Call("free", [VarAccess("b")]),
                # Call("free", [VarAccess("a")]),

                Call("print", [VarAccess("i_0")]),
            ]
        ),
        retExpr = VarAccess("i_0")
    ),

    Function(
        retType = TType.Int,
        name = "stupid",
        parameters = [VarDef(TType.Int, "c")],
        local_vars = [],
        body = VarAccess("c"),
        retExpr = BinExp(VarAccess("c"), BinaryOp.Plus, Constant(99))
    )
]