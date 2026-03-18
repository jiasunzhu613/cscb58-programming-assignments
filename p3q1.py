from codetypes import * 

"""
90- 100 => A+
85 -89 => A
80-84 => A-
77 - 79 => B+
73-76 => B
70-72 => B-
67 -69 => C+
63-66 => C
60-62 => C-
57-59 => D+
53-56 => D
50 - 52 => D-
0-49 => F
"""
# TODO： maybe write script ot verify output for this one
CODE = [
    Ldr(Reg(3), Reg(15), Word(78 * 4)), # note: LDR needs to be byte sized offsets
    Mov(Reg(1), Word(ord("F"))),

    # A+ case
    Cmp(Reg(0), Word(90)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("A"))), 
    Mov(Reg(2), Word(ord("+"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(69)),

    # A case
    Cmp(Reg(0), Word(85)),
    B(Word(2), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("A"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    B(Word(64)),

    # A- case
    Cmp(Reg(0), Word(80)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("A"))), 
    Mov(Reg(2), Word(ord("-"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(57)),

    # B+ case
    Cmp(Reg(0), Word(77)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("B"))), 
    Mov(Reg(2), Word(ord("+"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(50)),

    # B case
    Cmp(Reg(0), Word(73)),
    B(Word(2), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("B"))),  
    Strb(Reg(1), Reg(3), Word(0)),
    B(Word(46)),

    # B- case
    Cmp(Reg(0), Word(70)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("B"))), 
    Mov(Reg(2), Word(ord("-"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(38)),

    # C+ case
    Cmp(Reg(0), Word(67)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("C"))), 
    Mov(Reg(2), Word(ord("+"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(31)),

    # C case
    Cmp(Reg(0), Word(63)),
    B(Word(2), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("C"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    B(Word(24)),

    # C- case
    Cmp(Reg(0), Word(60)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("C"))), 
    Mov(Reg(2), Word(ord("-"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(17)),

    # D+ case
    Cmp(Reg(0), Word(57)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("D"))), 
    Mov(Reg(2), Word(ord("+"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(10)),

    # D case
    Cmp(Reg(0), Word(53)),
    B(Word(2), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("D"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    B(Word(7)),

    # D- case
    Cmp(Reg(0), Word(50)),
    B(Word(4), Cond.LT), # go to next if statement
    Mov(Reg(1), Word(ord("D"))), 
    Mov(Reg(2), Word(ord("-"))), 
    Strb(Reg(1), Reg(3), Word(0)),
    Strb(Reg(2), Reg(3), Word(0)),
    B(Word(0)),

    # F case
    Strb(Reg(1), Reg(3), Word(0)),
    Bx(Reg(14)),
    Word(0x09000000)
]