#!/usr/bin/python3
from dataclasses import dataclass
from enum import Enum

#####################################################################################
## Code classes
class Code:
    pass
class AssemblyCode(Code):
    # polymorphic function that is called
    def encode(self):
        pass

class LabeledAssemblyCode(AssemblyCode):
    pass

class Cond(Enum):
    EQ = 0
    NE = 1
    CS = 2
    CC = 3
    MI = 4
    PL = 5
    HI = 8
    LS = 9
    GE = 10
    LT = 11
    GT = 12
    LE = 13
    AL = 14

@dataclass
class Reg:
    """ Represents a Register """
    reg: int

@dataclass
class LabelRef(LabeledAssemblyCode):
    """ Represents a Label Reference, either in the code stream or within an instruction """
    label: str

@dataclass
class Word(Code):
    """ Represents a 32-bit word in the final assembled output. """
    value: int # A 32-bit value either from -2^31 to 2^31 - 1 OR 0 to 2^32 -1

@dataclass
class Label(LabeledAssemblyCode):
    """ Represents a label definition in labelled assembly code. """
    label: str

##################################################################################################
## Assembly Code follows

#####################################################################################
## Data processing instructions
@dataclass
class Add(AssemblyCode):
    """ Represents a ADD Rd, R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. 

        Usage: Add(Reg(1), Reg(2), Reg(3))
               Add(Reg(1), Reg(2), Word(15))
    """
    rd: Reg
    r1: Reg
    op2: Reg | Word
    cond: Cond = Cond.AL

    def encode(self):
        pass

@dataclass
class Sub(AssemblyCode):
    """ Represents a SUB Rd, R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. """
    rd: Reg
    r1: Reg
    op2: Reg | Word
    cond: Cond = Cond.AL

    def encode(self):
        pass

@dataclass
class Cmp(AssemblyCode):
    """ Represents a CMP R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. """
    r1: Reg
    op2: Reg | Word
    cond: Cond = Cond.AL

    def encode(self):
        pass

@dataclass
class Mov(AssemblyCode):
    """ Represents a MOV R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. """
    r1: Reg
    op2: Reg | Word
    cond: Cond = Cond.AL

    def encode(self):
        pass

######################################################################################
## Multiply, Divide
@dataclass
class Mul(AssemblyCode):
    """ Represents a MUL Rd, R1, R2 instruction. """
    rd: Reg
    r1: Reg
    r2: Reg
    cond: Cond = Cond.AL

    def encode(self):
        pass

@dataclass
class SDiv(AssemblyCode):
    """ Represents a SDIV Rd, R1, R2 instruction. """
    rd: Reg
    r1: Reg
    r2: Reg
    cond: Cond = Cond.AL

    def encode(self):
        pass

@dataclass
class UDiv(AssemblyCode):
    """ Represents a UDIV Rd, R1, R2 instruction. """
    rd: Reg
    r1: Reg
    r2: Reg
    cond: Cond = Cond.AL

    def encode(self):
        pass

#######################################################################################
## Branch-to-offset
@dataclass
class B(AssemblyCode):
    """ Represents a BL <imm> instruction. The immediate can either
        be a label reference or a word offset. """
    offset: Word | LabelRef
    cond: Cond = Cond.AL

@dataclass
class Bl(AssemblyCode):
    """ Represents a BL <imm> instruction. The immediate can either
        be a label reference or a word offset. """
    offset: Word | LabelRef
    cond: Cond = Cond.AL

########################################################################################
## Branch-to-register
@dataclass
class Bx(AssemblyCode):
    """ Represents a BX R1 instruction. """
    r: Reg
    cond: Cond = Cond.AL

@dataclass
class Blx(AssemblyCode):
    """ Represents a BLX R1 instruction. """
    r: Reg
    cond: Cond = Cond.AL

#########################################################################################
## Loads/stores
@dataclass
class Ldr(AssemblyCode):
    """ Represents a LDR Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

@dataclass
class Ldrb(AssemblyCode):
    """ Represents a LDRB Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

@dataclass
class Str(AssemblyCode):
    """ Represents a STR Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

@dataclass
class Strb(AssemblyCode):
    """ Represents a STRB Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

#########################################################################################
## PC-relative loads/stores
@dataclass
class LdrRel(LabeledAssemblyCode):
    """ Represents a LDR Rd, label instruction, which is
        assembled as a PC-relative load. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

@dataclass
class LdrbRel(LabeledAssemblyCode):
    """ Represents a LDRB Rd, label instruction. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

@dataclass
class StrRel(LabeledAssemblyCode):
    """ Represents a STR Rd, label instruction. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

@dataclass
class StrbRel(LabeledAssemblyCode):
    """ Represents a STRB Rd, label instruction. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL
