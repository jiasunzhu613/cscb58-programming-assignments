from codetypes import *

CODE = [
    Word(0xe3a01010), # MOV R1, 16
    Word(0xe0010091), # MUL R0, R0, R1
    Word(0xe5cf1001), # 0 STRB R1, [PC + 1], note +1 because of endianness
    Word(0xe3510000), # 4: CMP R1, 0, random filler instruction
    Word(0xe080000d), # 8: ADD R0, R0, R13, NOTE: top half of this instruction will stay the same no matter what
    Word(0xe12fff1e) # 12: BX R14
]

# Word(0xe0805001), # ADD R5, R0, R1 
# 0xE080040D