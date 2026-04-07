from codetypes import * 

"""
def pre_to_post(arr):
    root = arr[0]
    if root == "X":
        print(root, end=" ")
        return arr[1:]
    
    arr = pre_to_post(arr[1:])
    arr = pre_to_post(arr)
    
    print(root, end=" ")
    return arr

print(pre_to_post(input().split()))
"""

# TODO: check if AAPCS is followed
CODE = [
    # TODO: this may change later
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # Push LR onto stack
    Bl(LabelRef("pre_to_post")),
    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop LR from stack
    Bx(Reg(14)), # End

    # Function
    Label("pre_to_post"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # Push R4 on to stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # Push R5 on to stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(11), Reg(13), Word(0)), # Push FP on to stack
    Mov(Reg(11), Reg(13)), # Assign FP current value of SP

    LdrRel(Reg(4), LabelRef("stdin")), # Use R4 to hold stdin MMIO
    LdrRel(Reg(5), LabelRef("stdout")), # Use R4 to hold stdout MMIO

    # Should probably use frame pointer to mark
    Ldr(Reg(1), Reg(4), Word(0)), # Read from input, TODO: implement function to read input 
    Cmp(Reg(1), Word(ord("X"))),
    B(LabelRef("process_int"), Cond.NE),
    # Base case
    Strb(Reg(1), Reg(5), Word(0)), # Print X to stdout
    Ldr(Reg(1), Reg(4), Word(0)), # Read out the junk whitespace character
    Mov(Reg(1), Word(ord(" "))), # Force white space character no matter what
    Strb(Reg(1), Reg(5), Word(0)), # Print out the white space
    B(LabelRef("exit")), # double check if this is ok?

    Label("process_int"),
    # General strategy is just to store everything onto stack
    Cmp(Reg(1), Word(ord(" "))),
    B(LabelRef("exit_process_int"), Cond.EQ),
    Cmp(Reg(1), Word(ord("\n"))),
    B(LabelRef("exit_process_int"), Cond.EQ),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(1), Reg(13), Word(0)),
    Ldr(Reg(1), Reg(4), Word(0)),
    B(LabelRef("process_int")),

    Label("exit_process_int"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(1), Reg(13), Word(0)), # push the white space on too

    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # Store LR on stack
    Bl(LabelRef("pre_to_post")),
    Bl(LabelRef("pre_to_post")),
    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop LR from stack

    # Print the root sequence out
    Mov(Reg(2), Reg(11)),
    Sub(Reg(2), Reg(2), Word(4)), Ldr(Reg(1), Reg(2), Word(0)),
    
    Label("print_root"),
    Cmp(Reg(1), Word(ord(" "))),
    B(LabelRef("exit"), Cond.EQ),
    Cmp(Reg(1), Word(ord("\n"))),
    B(LabelRef("exit"), Cond.EQ),
    Ldr(Reg(1), Reg(2), Word(0)), Sub(Reg(2), Reg(2), Word(4)),  # Load character from stack following FP to SP order
    Strb(Reg(1), Reg(5), Word(0)), # print to stdout
    B(LabelRef("print_root")),

    Label("exit"),
    Mov(Reg(13), Reg(11)), # Return SP back to FP
    Ldr(Reg(11), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop FP from stack
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop FP from stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop FP from stack
    Bx(Reg(14)),


    Label("stdout"),
    Word(0x09000000),
    Label("stdin"),
    Word(0x09000004)
]