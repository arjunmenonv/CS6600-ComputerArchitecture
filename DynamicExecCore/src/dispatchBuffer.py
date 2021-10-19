from reorderBuffer import roBuffer
from reservationStation import reservationStation, LSreservationStation
from regfiles import regfiles
from instructionDecoder import instruction

def dispatch(instr:instruction, asuRS:reservationStation, muRS:reservationStation, duRS:reservationStation, lsuRS:LSreservationStation, regfiles:regfiles, rob:roBuffer):
    '''
        Initiate reg renaming, source reading and allocating RS, ROBuffer entries
        Stall if RRF, RS or ROBuffer is full
    '''
    robFull = False
    rsFull = False
    rrfFull = False
    rob.updateState()
    index, entry = regfiles.getFreeIdx()
    if rob.full:
        print("RoB is Full")
        robFull = True
        return True
    elif (index == None):
        print("RRF is Full")
        rrfFull = True
        return True
    else:
        if instr.fu == "ASU":
            if asuRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            destReg = instr.r1
            source1Reg = instr.r2
            source2Reg = instr.r3
            ready = False
            op1, valid1 = regfiles.sourceRead(source1Reg)
            op2, valid2 = regfiles.sourceRead(source2Reg)
            regfiles.destinationAllocate(index, entry, destReg)
            if (valid1 == 1) & (valid2 == 1):
                ready = True
            rrfTag = regfiles.arf.entries[destReg].tag
            instrId = rob.insertEntry(rrfTag)
            asuRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2)

        elif instr.fu == "MU":
            if muRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            destReg = instr.r1
            source1Reg = instr.r2
            source2Reg = instr.r3
            ready = False
            op1, valid1 = regfiles.sourceRead(source1Reg)
            op2, valid2 = regfiles.sourceRead(source2Reg)
            regfiles.destinationAllocate(index, entry, destReg)
            if (valid1 == 1) & (valid2 == 1):
                ready = True
            rrfTag = regfiles.arf.entries[destReg].tag
            instrId = rob.insertEntry(rrfTag)
            muRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2)

        elif instr.fu == "DU":
            if duRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            destReg = instr.r1
            source1Reg = instr.r2
            source2Reg = instr.r3
            ready = False
            op1, valid1 = regfiles.sourceRead(source1Reg)
            op2, valid2 = regfiles.sourceRead(source2Reg)
            regfiles.destinationAllocate(index, entry, destReg)
            if (valid1 == 1) & (valid2 == 1):
                ready = True
            rrfTag = regfiles.arf.entries[destReg].tag
            instrId = rob.insertEntry(rrfTag)
            duRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2)

        elif instr.fu == "LSU":
            if lsuRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            if instr.inst == "LOD":
                destReg = instr.r1
                sourceReg = instr.r2
                offset = instr.r3
                ready = False
                op1, valid1 = None, True
                op2, valid2 = regfiles.sourceRead(sourceReg)
                regfiles.destinationAllocate(index, entry, destReg)
                if (valid1 == 1) & (valid2 == 1):
                    ready = True
                rrfTag = regfiles.arf.entries[destReg].tag
                instrId = rob.insertEntry(rrfTag)
                lsuRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2, offset)
            elif instr.inst == "STO":
                source1Reg = instr.r1
                source2Reg = instr.r2
                offset = instr.r3
                ready = False
                op1, valid1 = regfiles.sourceRead(source1Reg)
                op2, valid2 = regfiles.sourceRead(source2Reg)
                if (valid1 == 1) & (valid2 == 1):
                    ready = True
                rrfTag = None
                instrId = rob.insertEntry(rrfTag)
                lsuRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2, offset)
    return False
