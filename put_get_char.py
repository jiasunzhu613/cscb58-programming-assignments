from codetypes import *

CODE = [
    Label("putchar"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # push R5 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(6), Reg(13), Word(0)), # push R6 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(7), Reg(13), Word(0)), # push R7 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(8), Reg(13), Word(0)), # push R8 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(9), Reg(13), Word(0)), # push R9 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(10), Reg(13), Word(0)), # push R10 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(11), Reg(13), Word(0)), # push R11 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # push R14 onto stack

    LdrRel(Reg(4), LabelRef("put_get_stdout")),
    Strb(Reg(0), Reg(4), Word(0)),

    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(11), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(10), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(9), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(8), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(7), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(6), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Bx(Reg(14)),

    Label("getchar"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # push R5 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(6), Reg(13), Word(0)), # push R6 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(7), Reg(13), Word(0)), # push R7 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(8), Reg(13), Word(0)), # push R8 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(9), Reg(13), Word(0)), # push R9 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(10), Reg(13), Word(0)), # push R10 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(11), Reg(13), Word(0)), # push R11 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # push R14 onto stack

    LdrRel(Reg(4), LabelRef("put_get_stdin")),
    Ldr(Reg(0), Reg(4), Word(0)),

    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(11), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(10), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(9), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(8), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(7), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(6), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Bx(Reg(14)),

    Label("put_get_stdout"),
    Word(0x09000000),
    Label("put_get_stdin"),
    Word(0x09000004)
]