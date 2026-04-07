from codetypes import * 

# Initial value is stored in R0
CODE = [
    Label("print"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(1), Reg(13), Word(0)), # push R1 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(2), Reg(13), Word(0)), # push R2 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(3), Reg(13), Word(0)), # push R3 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # push R5 onto stack
    Mov(Reg(1), Word(0)),
    Mov(Reg(2), Word(0)),
    Mov(Reg(3), Word(0)),
    Mov(Reg(4), Word(0)),
    Mov(Reg(5), Word(0)),

    LdrRel(Reg(2), LabelRef("builtin_print_stdout")), # Store stdout memory mapped io
    Mov(Reg(3), Word(ord("0"))), 
    Cmp(Reg(0), Word(0)), # handle case when R0 starts as 0
    Strb(Reg(3), Reg(2), Word(0), Cond.EQ),
    B(LabelRef("builtin_print_exit"), Cond.EQ),

    LdrRel(Reg(3), LabelRef("builtin_print_smallest")),
    Cmp(Reg(0), Reg(3)),
    B(LabelRef("builtin_print_body"), Cond.NE),
    # Hardcode Case for printing most negative value
    Mov(Reg(3), Word(ord("-"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("2"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("1"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("4"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("7"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("4"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("8"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("3"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("6"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("4"))), Strb(Reg(3), Reg(2), Word(0)),
    Mov(Reg(3), Word(ord("8"))), Strb(Reg(3), Reg(2), Word(0)),
    B(LabelRef("builtin_print_exit")),

    Label("builtin_print_body"),
    Mov(Reg(3), Word(0)), Sub(Reg(3), Reg(3), Word(1)),
    Mov(Reg(1), Reg(0)), Mul(Reg(1), Reg(1), Reg(3)),
    Cmp(Reg(0), Reg(1)), # compare R0 to -R0, if R0 < - R0 then R0 is negative, otherwise, positive
    Mov(Reg(3), Word(ord("-"))), 
    Strb(Reg(3), Reg(2), Word(0), Cond.LT), # print negative sign if negative value
    Mov(Reg(1), Reg(0), Cond.GT),

    # Print decimal values by repeatedly taking remainder and dividing until the value is 0
    Label("builtin_print_loop"),
    Cmp(Reg(1), Word(0)),
    B(LabelRef("builtin_print_output_loop"), Cond.LE),
    Add(Reg(5), Reg(5), Word(1)),
    Mov(Reg(4), Reg(1)), # store temp value to calculate modulo
    Mov(Reg(3), Word(10)),
    UDiv(Reg(4), Reg(4), Reg(3)), # figure out how many times 10 goes into R4
    Mul(Reg(4), Reg(4), Reg(3)), 
    Sub(Reg(4), Reg(1), Reg(4)),
    Add(Reg(4), Reg(4), Word(ord("0"))),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # store ascii value on stack for now, because we want to print in reverse
    UDiv(Reg(1), Reg(1), Reg(3)),
    B(LabelRef("builtin_print_loop")),

    Label("builtin_print_output_loop"),
    Cmp(Reg(5), Word(0)),
    B(LabelRef("builtin_print_exit"), Cond.LE),
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)),
    Strb(Reg(4), Reg(2), Word(0)),
    Sub(Reg(5), Reg(5), Word(1)),
    B(LabelRef("builtin_print_output_loop")),

    Label("builtin_print_exit"),
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R5 off stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R4 off stack
    Ldr(Reg(3), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R3 off stack
    Ldr(Reg(2), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R2 off stack
    Ldr(Reg(1), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R1 off stack
    B(LabelRef("builtin_print_done")),

    Label("builtin_print_done"),
    Bx(Reg(14)),

    Label("builtin_print_stdout"),
    Word(0x09000000),

    Label("builtin_print_smallest"),
    Word(0x80000000) #1000..000 in twos complement
]