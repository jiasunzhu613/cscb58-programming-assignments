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

     # TODO: how to resolve labeled assembly code
    def resolve_label(self, curr_index):

        pass

class LabeledAssemblyCode(AssemblyCode):
    label_mapping = {} # will be updated at runtime

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

    def resolve_label(self, curr_index):
        return Word(self.label_mapping[self.label] - curr_index - 2)

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
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 8
        if isinstance(self.op2, Reg):
            encoding |= 0b00001000
        else:
            encoding |= 0b00101000
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4
        encoding |= self.rd.reg

        if isinstance(self.op2, Reg):
            encoding <<= 12
            encoding |= self.op2.reg
        else:
            if self.op2.value > 1 << 12:
                raise RuntimeError("Value for op2 is greater than 2^12")
            
            encoding <<= 12
            encoding |= self.op2.value

        # print(int(f"0x{encoding:08x}", 16))
        return Word(encoding)

@dataclass
class Sub(AssemblyCode):
    """ Represents a SUB Rd, R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. """
    rd: Reg
    r1: Reg
    op2: Reg | Word
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 8
        if isinstance(self.op2, Reg):
            encoding |= 0b00000100
        else:
            encoding |= 0b00100100
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4
        encoding |= self.rd.reg

        if isinstance(self.op2, Reg):
            encoding <<= 12
            encoding |= self.op2.reg
        else:
            if self.op2.value > 1 << 12:
                raise RuntimeError("Value for op2 is greater than 2^12")
            
            encoding <<= 12
            encoding |= self.op2.value

        # print(hex(encoding))
        return Word(encoding)


@dataclass
class Cmp(AssemblyCode):
    """ Represents a CMP R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. """
    r1: Reg
    op2: Reg | Word
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 8
        if isinstance(self.op2, Reg):
            encoding |= 0b00010101
        else:
            encoding |= 0b00110101
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4 

        if isinstance(self.op2, Reg):
            encoding <<= 12
            encoding |= self.op2.reg
        else:
            if self.op2.value > 1 << 12:
                raise RuntimeError("Value for op2 is greater than 2^12")
            
            encoding <<= 12
            encoding |= self.op2.value

        # print(hex(encoding))
        return Word(encoding)
        

@dataclass
class Mov(AssemblyCode):
    """ Represents a MOV R1, Op2 instruction. Op2 is either a Reg or a Word
        that can be represented as an rotate of an 8-bit word. """
    r1: Reg
    op2: Reg | Word | LabelRef
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 8
        if isinstance(self.op2, Reg):
            encoding |= 0b00011010
        else:
            encoding |= 0b00111010
        encoding <<= 4
        encoding |= 0  # MOV doesn't use Rn, set to 0
        encoding <<= 4
        encoding |= self.r1.reg

        if isinstance(self.op2, Reg):
            encoding <<= 12
            encoding |= self.op2.reg
        else:
            if self.op2.value > 1 << 12:
                raise RuntimeError("Value for op2 is greater than 2^12")
            
            encoding <<= 12
            encoding |= self.op2.value

        # print(hex(encoding))
        return Word(encoding)
    
    def resolve_label(self, curr_index):
        if isinstance(self.op2, LabelRef):
            self.op2 = self.op2.resolve_label(curr_index)

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
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 7
        encoding |= 0b0000000  # Multiply opcode
        encoding <<= 1
        encoding |= 0b0  # S = 0 (no condition flags)
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 4
        encoding |= 0b0000  # Unused field
        encoding <<= 4
        encoding |= self.r2.reg
        encoding <<= 4
        encoding |= 0b1001  # Multiply signature
        encoding <<= 4
        encoding |= self.r1.reg

        # print(hex(encoding))
        return Word(encoding)

@dataclass
class SDiv(AssemblyCode):
    """ Represents a SDIV Rd, R1, R2 instruction. """
    rd: Reg
    r1: Reg
    r2: Reg
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 4
        encoding |= 0b0111  # Divide opcode prefix
        encoding <<= 4
        encoding |= 0b0001  # Signed divide
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 4
        encoding |= 0b1111  # Unused field
        encoding <<= 4
        encoding |= self.r2.reg
        encoding <<= 4
        encoding |= 0b0001  # Divide signature
        encoding <<= 4
        encoding |= self.r1.reg

        # print(hex(encoding))
        return Word(encoding)

@dataclass
class UDiv(AssemblyCode):
    """ Represents a UDIV Rd, R1, R2 instruction. """
    rd: Reg
    r1: Reg
    r2: Reg
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 4
        encoding |= 0b0111  # Divide opcode prefix
        encoding <<= 4
        encoding |= 0b0011  # Unsigned divide
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 4
        encoding |= 0b1111  # Unused field
        encoding <<= 4
        encoding |= self.r2.reg
        encoding <<= 4
        encoding |= 0b0001  # Divide signature
        encoding <<= 4
        encoding |= self.r1.reg

        # print(hex(encoding))
        return Word(encoding)

#######################################################################################
## Branch-to-offset
@dataclass
class B(AssemblyCode):
    """ Represents a BL <imm> instruction. The immediate can either
        be a label reference or a word offset. """
    offset: Word | LabelRef
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 4
        encoding |= 0b1010  # Branch opcode
        encoding <<= 24
        
        if isinstance(self.offset, Word):
            offset_val = self.offset.value
        else:
            raise RuntimeError("LabelRef cannot be encoded directly, must be resolved first")
        
        # Ensure offset fits in 24-bit signed
        if offset_val > 0x7FFFFF or offset_val < -0x800000:
            raise RuntimeError("Offset for B must fit in 24-bit signed range")
        
        # Mask to 24 bits
        encoding |= offset_val & 0xFFFFFF
        
        # print(hex(encoding))
        return Word(encoding)
    
    def resolve_label(self, curr_index):
        if isinstance(self.offset, LabelRef):
            self.offset = self.offset.resolve_label(curr_index)

@dataclass
class Bl(AssemblyCode):
    """ Represents a BL <imm> instruction. The immediate can either
        be a label reference or a word offset. """
    offset: Word | LabelRef
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 3
        encoding |= 0b101  # Branch opcode (same as B)
        encoding <<= 1
        encoding |= 0b1    # L=1 for Link (BL)
        encoding <<= 24
        
        if isinstance(self.offset, Word):
            offset_val = self.offset.value
        else:
            raise RuntimeError("LabelRef cannot be encoded directly, must be resolved first")
        
        # Ensure offset fits in 24-bit signed
        if offset_val > 0x7FFFFF or offset_val < -0x800000:
            raise RuntimeError("Offset for BL must fit in 24-bit signed range")
        
        # Mask to 24 bits
        encoding |= offset_val & 0xFFFFFF
        
        print(hex(encoding))
        return Word(encoding)

    def resolve_label(self, curr_index):
        if isinstance(self.offset, LabelRef):
            self.offset = Word((curr_index + self.offset.resolve_label(curr_index).value + 2) * 4)

########################################################################################
## Branch-to-register
@dataclass
class Bx(AssemblyCode):
    """ Represents a BX R1 instruction. """
    r: Reg
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 8
        encoding |= 0b00010010
        for _ in range(3):
            encoding <<= 4
            encoding |= 0b1111
        encoding <<= 4
        encoding |= 0b0001
        encoding <<= 4
        encoding |= self.r.reg

        return Word(encoding)

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

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 2
        encoding |= 0b01  # Load/Store indicator
        encoding <<= 1
        encoding |= 0b0   # I = 0 (immediate offset)
        encoding <<= 1
        encoding |= 0b1   # P = 1 (pre-index)
        encoding <<= 1
        encoding |= 0b1   # U = 1 (add offset)
        encoding <<= 1
        encoding |= 0b0   # B = 0 (word)
        encoding <<= 1
        encoding |= 0b0   # W = 0 (no write-back)
        encoding <<= 1
        encoding |= 0b1   # L = 1 (load)
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 12
        # if self.off.value > 0xFFF or self.off.value < 0:
        #     raise RuntimeError("Offset for Ldr must be in range 0-4095")
        encoding |= self.off.value

        # print(hex(encoding))
        return Word(encoding)

@dataclass
class Ldrb(AssemblyCode):
    """ Represents a LDRB Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 2
        encoding |= 0b01  # Load/Store indicator
        encoding <<= 1
        encoding |= 0b0   # I = 0 (immediate offset)
        encoding <<= 1
        encoding |= 0b1   # P = 1 (pre-index)
        encoding <<= 1
        encoding |= 0b1   # U = 1 (add offset)
        encoding <<= 1
        encoding |= 0b1   # B = 1 (byte)
        encoding <<= 1
        encoding |= 0b0   # W = 0 (no write-back)
        encoding <<= 1
        encoding |= 0b1   # L = 1 (load)
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 12
        # if self.off.value > 0xFFF or self.off.value < 0:
        #     raise RuntimeError("Offset for Ldrb must be in range 0-4095")
        encoding |= self.off.value

        # print(hex(encoding))
        return Word(encoding)

@dataclass
class Str(AssemblyCode):
    """ Represents a STR Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 2
        encoding |= 0b01  # Load/Store indicator
        encoding <<= 1
        encoding |= 0b0   # I = 0 (immediate offset)
        encoding <<= 1
        encoding |= 0b1   # P = 1 (pre-index)
        encoding <<= 1
        encoding |= 0b1   # U = 1 (add offset)
        encoding <<= 1
        encoding |= 0b0   # B = 0 (word)
        encoding <<= 1
        encoding |= 0b0   # W = 0 (no write-back)
        encoding <<= 1
        encoding |= 0b0   # L = 0 (store)
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 12
        # if self.off.value > 0xFFF or self.off.value < 0:
        #     raise RuntimeError("Offset for Str must be in range 0-4095")
        encoding |= self.off.value

        # print(hex(encoding))
        return Word(encoding)

@dataclass
class Strb(AssemblyCode):
    """ Represents a STRB Rd, R1 + offset instruction. """
    rd: Reg
    r1: Reg
    off: Word
    cond: Cond = Cond.AL

    def encode(self):
        encoding = 0
        encoding |= self.cond.value
        encoding <<= 2
        encoding |= 0b01  # Load/Store indicator
        encoding <<= 1
        encoding |= 0b0   # I = 0 (immediate offset)
        encoding <<= 1
        encoding |= 0b1   # P = 1 (pre-index)
        encoding <<= 1
        encoding |= 0b1   # U = 1 (add offset)
        encoding <<= 1
        encoding |= 0b1   # B = 1 (byte)
        encoding <<= 1
        encoding |= 0b0   # W = 0 (no write-back)
        encoding <<= 1
        encoding |= 0b0   # L = 0 (store)
        encoding <<= 4
        encoding |= self.r1.reg
        encoding <<= 4
        encoding |= self.rd.reg
        encoding <<= 12
        # if self.off.value > 0xFFF or self.off.value < 0:
        #     raise RuntimeError("Offset for Strb must be in range 0-4095")
        encoding |= self.off.value

        # print(hex(encoding))
        return Word(encoding)

#########################################################################################
## PC-relative loads/stores
# Example: 
# LDR Rd, [word1] => in practice its actually LDR Rd, =word1 i think
# word1: .word 100
# LdrRel takes byte sized offsets
@dataclass
class LdrRel(LabeledAssemblyCode):
    """ Represents a LDR Rd, label instruction, which is
        assembled as a PC-relative load. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

    def resolve_label(self, curr_index):
        offset = self.l.resolve_label(curr_index)
        offset.value *= 4
        return Ldr(self.rd, Reg(15), offset, self.cond)

@dataclass
class LdrbRel(LabeledAssemblyCode):
    """ Represents a LDRB Rd, label instruction. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

    def resolve_label(self, curr_index):
        offset = self.l.resolve_label(curr_index)
        offset.value *= 4
        return Ldrb(self.rd, Reg(15), offset, self.cond)

@dataclass
class StrRel(LabeledAssemblyCode):
    """ Represents a STR Rd, label instruction. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

    def resolve_label(self, curr_index):
        offset = self.l.resolve_label(curr_index)
        offset.value *= 4
        return Str(self.rd, Reg(15), offset, self.cond)

@dataclass
class StrbRel(LabeledAssemblyCode):
    """ Represents a STRB Rd, label instruction. """
    rd: Reg
    l: LabelRef
    cond: Cond = Cond.AL

    def resolve_label(self, curr_index):
        offset = self.l.resolve_label(curr_index)
        offset.value *= 4
        return Strb(self.rd, Reg(15), offset, self.cond)