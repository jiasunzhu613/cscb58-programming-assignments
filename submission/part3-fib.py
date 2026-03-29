from codetypes import *

# TODO: remove loading of stack variable, just subtract by 4
# need to use two additional registers to store temporary results from calling fib(n-1) and fib(n-2)
# use BL to call the subroutine and then BX R14 (LR) to go back to main execution
CODE = [
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)),  # Push LR onto stack
    Bl(LabelRef("fib")), # call fib(n)
    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop LR off stack
    Bx(Reg(14)),

    Label("fib"),
    Cmp(Reg(0), Word(1)), # Base case, <= 1, we return itself
    B(LabelRef("fib_body"), Cond.GT), # TODO: probably use a label later for body code
    # Mov(Reg(0), Word(1)),
    B(LabelRef("done")), # end function calls by branching back to LR
    
    Label("fib_body"),
    # Need to push register value into stack first, we will use R1 and R2 for two fib calls
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(1), Reg(13), Word(0)), 
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(2), Reg(13), Word(0)), 
    Mov(Reg(1), Reg(0)), Sub(Reg(1), Reg(1), Word(1)), # n - 1
    Mov(Reg(2), Reg(0)), Sub(Reg(2), Reg(2), Word(2)), # n - 2
    
    # Call fib(n - 1)
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # Push LR onto stack
    Mov(Reg(0), Reg(1)), # make R0 = n - 1 (TODO: couldve just subtracted)
    Bl(LabelRef("fib")),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(0), Reg(13), Word(0)), # push return value onto stack to use later
    Mov(Reg(0), Reg(2)), # make R0 = n - 2
    Bl(LabelRef("fib")),
    Ldr(Reg(1), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop value of fib(n-1) off from stack
    Add(Reg(0), Reg(0), Reg(1)), # add fib(n-1) and fib(n-2)
    # Handle popping off stack
    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop LR back
    Ldr(Reg(2), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R2 back
    Ldr(Reg(1), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R1 back
    B(LabelRef("done")),
    # Need to BL to fib later


    Label("done"), 
    Bx(Reg(14)),
]


"""
this should just constantly add 1 to register 1:
Label("Hello"),
Add(Reg(1), Reg(1), Word(1)),
B(LabelRef("Hello")),

this loads word1 into register 0: 
LdrRel(Reg(0), LabelRef("word1")),
Add(Reg(1), Reg(1), Word(1)),
Label("word1"),
Word(0x0f0081e2),
Word(0xBA000002)
"""