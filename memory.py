from codetypes import *

# SP is R13
CODE = [
    # Explicitly set the value that is used as freelist pointer to start as NULL (0)
    B(Word(0)),
    LabelRef("freelist"),
    Mov(Reg(0), LabelRef("freelist")),
    Bx(Reg(14)),
    # Global variables
    Label("freelist"), # This will ALWAYS refer to the start of the freelist allocator linkedlist
    Word(0xff800000), # Start of heap is at memory address 2^32 - 8MB (2^32 - 8 * 2^20)

    Label("heap_start_size"),
    Word(0x00800000) # 8MB in bytes
]
