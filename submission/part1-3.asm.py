from codetypes import *

# 1
CODE = [
    Word(0xe3510000), # CMP R1, 0
    Word(0x1735f110), # SDIVNEQ R5, R0, R1 
    Word(0x02455001), # Sub R5, R5, 1
    Word(0x02466001), # Sub R6, R6, 1
    Word(0xe12fff1e) # BX R14
]