from codetypes import *

# SP is R13
CODE = [
    # Explicitly set the value that is used as freelist pointer to start as NULL (0)
    LdrRel(Reg(0), LabelRef("freelist")),
    LdrRel(Reg(1), LabelRef("heap_start_size")),
    Str(Reg(1), Reg(0), Word(0)), # set start size of heap 
    Add(Reg(0), Reg(0), Word(4)),
    Mov(Reg(1), Word(10)),
    Str(Reg(1), Reg(0), Word(0)),

    Mov(Reg(0), Word(100)),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # Store current LR on stack
    Bl(LabelRef("malloc")),
    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)),

    Bx(Reg(14)),

    # FUNC: to allocate a chunk of memory on the heap
    # Params: 
    # - R0: size of memory desired in bytes
    Label("malloc"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # Push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # Push R5 onto stack
    # TODO: should traverse the freelist allocator to search for the "worst fit" free space to allocate memory into
    # Use R1 to store current best found pointer/ memory block
    # use R3 to store current size, use R2 to store the current memory address of the current block
    # use R4 to store previous memory block address
    # Also loop freelist until we see NULL valued pointer
    Mov(Reg(1), Word(0)),
    Mov(Reg(4), Word(0)),
    Mov(Reg(5), Reg(0)), # let R5 store copy of R0 which is the memory size requested by user

    
    LdrRel(Reg(2), LabelRef("freelist")),
    Label("freelist_loop"),
    Cmp(Reg(2), Word(0)), # check if freelist pointer == NULL
    B(LabelRef("exit_freelist_loop"), Cond.EQ), # exit loop when out freelist pointer becomes NULL or 0
    Ldr(Reg(3), Reg(2), Word(0)), # REMEMBER, LDR is byte sized offsets, there is no instruction that is bit sized offsets, dumbass
    Cmp(Reg(3), Reg(0)),
    Mov(Reg(5), Reg(3), Cond.GE), # if R3 >= R5, our current memory block in freelist is able to hold R0 
    Mov(Reg(1), Reg(2), Cond.GE), # similarly, update best pointer
    Mov(Reg(4), Reg())
    Ldr(Reg(2), Reg(2), Word(4)), # load next freelist block
    B(LabelRef("freelist_loop")),

    Label("exit_freelist_loop"),
    # Best sized will be stored in R0, the pointer to corresponding will be stored in R1


    Label("done"),
    Bx(Reg(14)),
    
    

    # FUNC: to free a given memory address allocated in the heap
    # Params:
    # - R0: memory address to be freed
    Label("free"),
    # TODO: look into the memory address given by R0 as well as 4 bytes before it for the length of the memory allocated
    # TODO: ^ actually no need, just add to freelist linked list appropriately 
    # TODO: check where to place the node and handle correspondence to next node on freelist properly

    # Global variables
    Label("freelist"), # This will ALWAYS refer to the start of the freelist allocator linkedlist
    Word(0xff800000), # Start of heap is at memory address 2^32 - 8MB (2^32 - 8 * 2^20)

    Label("heap_start_size"),
    Word(0x00800000) # 8MB in bytes
]
