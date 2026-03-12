from codetypes import *

# 1
CODE = [
    Word(0xe3510000), # CMP R1, 0
    Word(0x1735f110), # SDIVNEQ R5, R0, R1 
    Word(0x03e05000), # MVN R5, 0
    Word(0x03e06000), # MVN R6, 0
    Word(0xe12fff1e) # BX R14
]