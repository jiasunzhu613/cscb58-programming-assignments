from codetypes import *

CODE = [
    Ldr(Reg(0), Reg(15), Word(2*4)), # why is this giving R15, R0????
    Cmp(Reg(1), Word(0)),
    Add(Reg(0), Reg(1), Reg(15), Cond.AL),
    Bx(Reg(14)),
    Word(0x09000000)
]