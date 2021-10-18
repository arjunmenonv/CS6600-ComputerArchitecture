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
    if rob.full:
        print("RoB is Full")
        robFull = True
        return True
    else:
        if instr.fu == "ASU":
            destReg = instr.r1
            if asuRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            if regfiles.destinationAllocate(destReg) == False:
                print("RRF is Full")
                rrfFull = True
                return True
        elif instr.fu == "MU":
            destReg = instr.r1
            if muRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            if regfiles.destinationAllocate(destReg) == False:
                print("RRF is Full")
                rrfFull = True
                return True
        elif instr.fu == "DU":
            destReg = instr.r1
            if duRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            if regfiles.destinationAllocate(destReg) == False:
                print("RRF is Full")
                rrfFull = True
                return True
        elif instr.fu == "LSU":
            if lsuRS.isFull():
                print("RS is Full")
                rsFull = True
                return True
            if instr.inst == "LOD":
                destReg = instr.r1
                if regfiles.destinationAllocate(destReg) == False:
                    print("RRF is Full")
                    rrfFull = True
                    return True

    if (robFull == False) & (rsFull == False) & (rrfFull == False):
        if instr.fu == "ASU":
            destReg = instr.r1
            source1Reg = instr.r2
            source2Reg = instr.r3
            ready = False
            rrfTag = regfiles.arf.entries[destReg].tag
            instrId = rob.insertEntry(rrfTag)
            op1, valid1 = regfiles.sourceRead(source1Reg)
            op2, valid2 = regfiles.sourceRead(source2Reg)
            if (valid1 == 1) & (valid2 == 1):
                ready = True
            asuRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2)

        elif instr.fu == "MU":
            destReg = instr.r1
            source1Reg = instr.r2
            source2Reg = instr.r3
            ready = False
            rrfTag = regfiles.arf.entries[destReg].tag
            instrId = rob.insertEntry(rrfTag)
            op1, valid1 = regfiles.sourceRead(source1Reg)
            op2, valid2 = regfiles.sourceRead(source2Reg)
            if (valid1 == 1) & (valid2 == 1):
                ready = True
            muRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2)

        elif instr.fu == "DU":
            destReg = instr.r1
            source1Reg = instr.r2
            source2Reg = instr.r3
            ready = False
            rrfTag = regfiles.arf.entries[destReg].tag
            instrId = rob.insertEntry(rrfTag)
            op1, valid1 = regfiles.sourceRead(source1Reg)
            op2, valid2 = regfiles.sourceRead(source2Reg)
            if (valid1 == 1) & (valid2 == 1):
                ready = True
            duRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2)

        elif instr.fu == "LSU":
            if instr.inst == "LOD":
                destReg = instr.r1
                rrfTag = regfiles.arf.entries[destReg].tag
                sourceReg = instr.r2
                offset = instr.r3
                ready = False
                instrId = rob.insertEntry(rrfTag)
                op1, valid1 = None, True
                op2, valid2 = regfiles.sourceRead(sourceReg)
                if (valid1 == 1) & (valid2 == 1):
                    ready = True
                lsuRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2, offset)
            elif instr.inst == "STO":
                rrfTag = None
                source1Reg = instr.r1
                source2Reg = instr.r2
                offset = instr.r3
                ready = False
                instrId = rob.insertEntry(rrfTag)
                op1, valid1 = regfiles.sourceRead(source1Reg)
                op2, valid2 = regfiles.sourceRead(source2Reg)
                if (valid1 == 1) & (valid2 == 1):
                    ready = True
                lsuRS.addEntry(instrId, instr.inst, ready, op1, valid1, op2, valid2, offset)

        return False
