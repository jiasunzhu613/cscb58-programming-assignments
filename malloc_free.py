from codetypes import *

CODE = [
    # ===================================
    # ======= FUNCTION ========
    # ===================================


    # FUNC: to allocate a chunk of memory on the heap
    # Params: 
    # - R0: size of memory desired in bytes
    Label("malloc"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # Push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # Push R5 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(6), Reg(13), Word(0)), # Push R6 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(7), Reg(13), Word(0)), # Push R7 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(8), Reg(13), Word(0)), # Push R8 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(9), Reg(13), Word(0)), # Push R9 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(10), Reg(13), Word(0)), # Push R10 onto stacks
    # TODO: should traverse the freelist allocator to search for the "worst fit" free space to allocate memory into
    
    LdrRel(Reg(4), LabelRef("is_freelist_init")),
    Cmp(Reg(4), Word(0)),
    B(LabelRef("freelist_skip_init"), Cond.NE),
    LdrRel(Reg(4), LabelRef("freelist")),
    LdrRel(Reg(5), LabelRef("heap_start_size")),
    Str(Reg(5), Reg(4), Word(0)), # set start size of heap 
    Mov(Reg(5), Word(0)),
    Str(Reg(5), Reg(4), Word(4)), # set next pointer to point to 0
    Mov(Reg(5), Word(1)),
    StrRel(Reg(5), LabelRef("is_freelist_init")), # set init flag to true
    B(LabelRef("freelist_skip_init")), 
    # Normalize the amount request first and + 4 for metadata header

    Label("freelist_skip_init"),
    Mov(Reg(1), Word(4)),
    Add(Reg(0), Reg(0), Word(3)), # Add 3 
    UDiv(Reg(0), Reg(0), Reg(1)), # div 4
    Mul(Reg(0), Reg(0), Reg(1)), # mult 4
    Mov(Reg(2), Reg(0)), # Store altered request value in R2 to use later in size header
    Add(Reg(0), Reg(0), Word(4)), # add 4 for size header

    LdrRel(Reg(4), LabelRef("freelist")),
    Cmp(Reg(4), Word(0)),
    B(LabelRef("no_heap_remaining_to_allocate_error"), Cond.EQ),

    Ldr(Reg(5), Reg(4), Word(0)), # best size
    Cmp(Reg(5), Reg(0)),
    Mov(Reg(5), Reg(0), Cond.LT),
    Mov(Reg(6), Reg(4)), # pointer to memory block associated with best size 
    Mov(Reg(6), Word(0), Cond.LT),
    Mov(Reg(7), Word(0)), # prev pointer for the potential block that points to the block associated with best size

    Label("freelist_loop"),
    Ldr(Reg(8), Reg(4), Word(4)), # Load next pointer value into register
    Cmp(Reg(8), Word(0)), # check if freelist pointer == NULL
    B(LabelRef("exit_freelist_loop"), Cond.EQ), # exit loop when out freelist pointer becomes NULL or 0
    Ldr(Reg(9), Reg(8), Word(0)), # load size of next memory block
    Cmp(Reg(9), Reg(5)), # compare size of current block with "best block"
    Mov(Reg(5), Reg(9), Cond.GE), # if R3 >= R5, our current memory block in freelist is able to hold R0 
    Mov(Reg(6), Reg(8), Cond.GE), # similarly, update best pointer
    Mov(Reg(7), Reg(4), Cond.GE), # Similar for best prev pointer
    Mov(Reg(4), Reg(8)), # load next freelist block
    B(LabelRef("freelist_loop")),

    Label("exit_freelist_loop"),
    Cmp(Reg(6), Word(0)), 
    B(LabelRef("malloc_block_requested_too_big_error"), Cond.EQ),
    # If pointer has any value, we can be guaranteed that it has enough room to store the requested memory and the 4 byte header
    # Best sized will be stored in R0, the pointer to corresponding will be stored in R1
    # If there is no prev, we need to StrRel into freelist label
    # Take difference between best size and the size we need to use up
    # see if it is >= 8 and then if it is, we can set the size and next pointers
    # TODO: need to save next pointer before allocating
    Sub(Reg(5), Reg(5), Reg(0)), # R5 - R0 => R5: remaining size of block
    Str(Reg(2), Reg(6), Word(0)), # Put in size
    Add(Reg(6), Reg(6), Word(4)), # move past region reserved for header
    Ldr(Reg(10), Reg(6), Word(0)), # Load pointer to next block into R10
    Mov(Reg(0), Reg(6)), # use R6 as return value
    Add(Reg(6), Reg(6), Reg(2)), # Move past allocated region
    
    # Coming into this section R5 hold the remaining size of the best block
    Sub(Reg(5), Reg(5), Word(4)),
    Cmp(Reg(5), Word(4)), # check if R5 has anymore space to use for further allocation
    B(LabelRef("has_remaining_block_else"), Cond.LT),
    Str(Reg(5), Reg(6), Word(0)), # Store size in R5 into memory at R6
    Str(Reg(10), Reg(6), Word(4)), # Store next pointer in R10 into memory at R6 + 4
    B(LabelRef("prev_pointer_if")),

    Label("has_remaining_block_else"),
    # R6 will now store the value the prev pointer should point to (which should be R10 or the next pointer if the current block has no remaining)
    Mov(Reg(6), Reg(10)), 


    Label("prev_pointer_if"),
    Cmp(Reg(7), Word(0)),
    B(LabelRef("has_prev_pointer_else"), Cond.EQ),
    Str(Reg(6), Reg(7), Word(4)), # Store R6 into pointer header of prev free block
    B(LabelRef("after_prev_pointer_if")),

    Label("has_prev_pointer_else"),
    StrRel(Reg(6), LabelRef("freelist")), # No prev pointer, so store into freelist label

    Label("after_prev_pointer_if"),
    B(LabelRef("malloc_done")), 

    Label("malloc_block_requested_too_big_error"),
    Mov(Reg(0), Word(0)), 
    Sub(Reg(0), Reg(0), Word(1)),
    B(LabelRef("malloc_done")),

    Label("no_heap_remaining_to_allocate_error"),
    Mov(Reg(0), Word(0)), 
    Sub(Reg(0), Reg(0), Word(1)),
    B(LabelRef("malloc_done")),

    Label("malloc_done"),
    Ldr(Reg(10), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R10 from stack
    Ldr(Reg(9), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R9 from stack
    Ldr(Reg(8), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R8 from stack
    Ldr(Reg(7), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R7 from stack
    Ldr(Reg(6), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R6 from stack
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R5 from stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # Pop R4 from stack
    Bx(Reg(14)),
    

    # FUNC: to free a given memory address allocated in the heap
    # Params:
    # - R0: memory address to be freed
    Label("free"), # No return value
    # Just use LIFO insertion into free list
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # Push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # Push R5 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(6), Reg(13), Word(0)), # Push R6 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(14), Reg(13), Word(0)), # Push R14 onto stack

    LdrRel(Reg(4), LabelRef("freelist")),
    Cmp(Reg(0), Reg(4)), # Compare R0 to R4
    B(LabelRef("free_linkedlist_body"), Cond.GE), # GEQ because our heap grows up

    Str(Reg(4), Reg(0), Word(0)), # store pointer into the memory block that is being freed
    Sub(Reg(0), Reg(0), Word(4)), # Subtract 4 since our initial location was above the size header
    StrRel(Reg(0), LabelRef("freelist")), # Store R0 - 4 as current freelist head (-4 to include size header)
    
    Mov(Reg(1), Reg(4)), 
    Bl(LabelRef("merge_blocks")),
    
    B(LabelRef("free_done")), 

    Label("free_linkedlist_body"),
    # Node can only be placed after first node 
    # while node.next < free_block:
    #   node = node.next
    Ldr(Reg(5), Reg(4), Word(4)), # Load value of node.next into R5
    Cmp(Reg(0), Reg(5)), # Want to find first block where R0 <= R5
    B(LabelRef("exit_free_body"), Cond.LE),
    Mov(Reg(4), Reg(5)), # node = node.next
    B(LabelRef("free_linkedlist_body")),

    Label("exit_free_body"),
    Sub(Reg(0), Reg(0), Word(4)), # Subtract 4 since our initial location was above the size header
    Str(Reg(0), Reg(4), Word(4)), # Store block getting freed into next pointer for R4
    Str(Reg(5), Reg(0), Word(4)), # Store next block into pointer

    Mov(Reg(6), Reg(0)),
    Mov(Reg(0), Reg(4)), 
    Mov(Reg(1), Reg(6)),
    Bl(LabelRef("merge_blocks")), # will return new block as R0

    Mov(Reg(1), Reg(5)), 
    Bl(LabelRef("merge_blocks")),

    Label("free_done"),
    Ldr(Reg(14), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R14 off stack
    Ldr(Reg(6), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R6 off stack
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R5 off stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R4 off stack
    Bx(Reg(14)),


    # R0 will always be the lower block
    Label("merge_blocks"),
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(4), Reg(13), Word(0)), # Push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(5), Reg(13), Word(0)), # Push R4 onto stack
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(6), Reg(13), Word(0)), # Push R6 onto stacks
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(7), Reg(13), Word(0)), # Push R7 onto stacks
    Sub(Reg(13), Reg(13), Word(4)), Str(Reg(8), Reg(13), Word(0)), # Push R8 onto stacks

    Ldr(Reg(4), Reg(0), Word(0)), # Load size of R0 block
    Add(Reg(4), Reg(4), Word(4)),
    Add(Reg(4), Reg(4), Reg(0)), # Add size of the block to the address of the block
    
    Cmp(Reg(4), Reg(1)), 
    # If R4 == R1 then we should merge
    B(LabelRef("merge_blocks_done"), Cond.NE),
    Ldr(Reg(5), Reg(1), Word(4)), # load next pointer of second block first
    Ldr(Reg(6), Reg(1), Word(0)), # load size of second block
    Add(Reg(6), Reg(6), Word(4)), # Add 4 for the size header that will be omitted in the merged block
    Ldr(Reg(7), Reg(0), Word(0)), # load size of first block
    Add(Reg(7), Reg(7), Reg(6)), # add sizes together
    Str(Reg(7), Reg(0), Word(0)), # store size back
    Str(Reg(5), Reg(0), Word(4)), # store pointer at R0+4 for the size header offset
    B(LabelRef("merge_blocks_done")),

    Label("merge_blocks_done"),
    Ldr(Reg(8), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R8 off stack
    Ldr(Reg(7), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R7 off stack
    Ldr(Reg(6), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R6 off stack
    Ldr(Reg(5), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R5 off stack
    Ldr(Reg(4), Reg(13), Word(0)), Add(Reg(13), Reg(13), Word(4)), # pop R4 off stack
    Bx(Reg(14)),

    # Global variables
    # Heap starts at 0xff000000 and grows upward to 0xff800000
    Label("freelist"), # This will ALWAYS refer to the start of the freelist allocator linkedlist
    Word(0xff000000), # Start of heap is at memory address 2^32 - 8MB (2^32 - 8 * 2^20)

    Label("is_freelist_init"),
    Word(0x00000000),

    Label("heap_start_size"),
    Word(0x00800000) # 8MB in bytes (TODO: not accounting for -4 for initial header yet)
]