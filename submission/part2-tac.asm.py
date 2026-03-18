from codetypes import *

CODE = [
    # Use R0 to store stdout
    # Use R1 to store stdin
    Ldr(Reg(0), Reg(15), Word(15 * 4)), # is LDR implemented wrong? why is the offset full?
    Ldr(Reg(1), Reg(15), Word(15 * 4)),

    # Load into a register
    Sub(Reg(5), Reg(5), Word(1)), # Turn R5 to -1 for EOF checking
    Ldr(Reg(2), Reg(1), Word(0)), # Read value from stdin
    Cmp(Reg(2), Reg(5)), # EOF Check
    B(Word(2), Cond.EQ), # If is EOF, move on to print from stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(2), Reg(13), Word(0)), # otherwise, push onto stack
    B(Word(-7)), # TODO: change

    Add(Reg(13), Reg(13), Word(4)), # Remove newline character
    Cmp(Reg(13), Word(0)),
    B(Word(3), Cond.GE),
    Ldr(Reg(3), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop from stack
    Strb(Reg(3), Reg(0), Word(0)), # print to stdout
    B(Word(-7)), # loop

    Bx(Reg(14)),
    Word(0x09000000),
    Word(0x09000004)
]