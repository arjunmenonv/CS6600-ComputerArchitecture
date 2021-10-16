import sys
from collections import namedtuple

typeOfRS = {'0001':'ALU', '0010':'ALU', '0011':'MDU', '0100':'MDU', '0101':'LSU', '0110':'LSU'}
typeOfInstr = {'0001':'ADD', '0010':'SUB', '0011':'MUL', '0100':'DIV', '0101':'LOD', '0110':'STO'}

instruction = namedtuple('instruction', ['inst', 'fu', 'r1', 'r2', 'r3'])

def decode(instr):
    '''
        Decode 16-bit instructions to a format more
        human readable and easier to deal with
    '''
    if len(instr) == 16:
        inst = typeOfInstr[instr[:4]]
        fu = typeOfRS[instr[:4]]
        r1 = int(instr[4:8], base=2)
        r2 = int(instr[8:12], base=2)
        r3 = int(instr[12:16], base=2)
        instrn = instruction(inst, fu, r1, r2, r3)
        return instrn
    else:
        sys.exit("Invalid instruction length")
