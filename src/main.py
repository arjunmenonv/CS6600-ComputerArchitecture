from conf import *
from instructionDecoder import *
from reorderBuffer import *
from regfiles import *
from reservationStation import *
from FU import *
from dispatchBuffer import *

def topModule():
    '''
    Top Module: Performs one run of ID, Dispatch, EX, RoBComplete operations
    '''
    if (Decode_ptr < numInstr):
        # send upto DECODE_MAX decoded instructions to dispatch buffer, break if buffer is full
        # increment Decode_ptr by number of instructions sent to dispatch buffer
        for i in range(Decode_ptr, Decode_ptr + DECODE_MAX, 1):
            # call decoder, break if Dispatch buffer is full
            Decode_ptr += 1
    else:
        print("Decoder: Reached End of Instructions")
    if (Dispatch_ptr < numInstr):
        for i in range(Dispatch_ptr, Dispatch_ptr+ISSUE_WIDTH, 1):
            #stall = dispatch(instructionsDecoded[i], asu, mu, du, lsu)
            if stall:
                break
            Dispatch_ptr += 1
    else:
        print("Dispatch: Reached End of Instructions")
    ASUarg = asuRS.putIntoFU()
    MUarg = muRS.putIntoFU()
    DUarg = duRS.putIntoFU()
    LSUarg = lsuRS.putIntoFU(lsuFU)
    # pass args to FUs
    if (ASUarg != [-1, -1, None, None]):
        RoB.updateEntry("issued", ASUarg[0])
    if (MUarg != [-1, -1, None, None]):
        RoB.updateEntry("issued", MUarg[0])
    if (DUarg != [-1, -1, None, None]):
        RoB.updateEntry("issued", DUarg[0])
    ASUout = asuFU.shiftAndEval(*ASUarg)
    MUout = muFU.shiftAndEval(*MUarg)
    DUout = duFU.shiftAndEval(*DUarg)
    if (LSUarg != [-1, -1, None, None, None]):
        lsuFU.IssueNewOp(clkCount, *LSUarg)
        RoB.updateEntry("issued", LSUarg[0])
    LSUout = lsuFU.pollLSU(clkCount)
    # finish instructions, obtain rrfTag
    ASUtag = None
    ASUval = ASUout.regVal
    MUtag = None
    MUval = MUout.regVal
    DUtag = None
    DUval = DUout.regVal
    LSUtag = None
    LSUval = LSUout['RegVal']
    if (ASUout.instrId != -1):
        RoB.updateEntry("finished", ASUout.instrId)
        ASUtag = RoB.entries[ASUout.instrId].renameReg
    if (MUout.instrId != -1):
        RoB.updateEntry("finished", MUout.instrId)
        MUtag = RoB.entries[MUout.instrId].renameReg
    if (DUout.instrId != -1):
        RoB.updateEntry("finished", DUout.instrId)
        DUtag = RoB.entries[DUout.instrId].renameReg
    if (LSUout['InstrIdx'] != -1):
        RoB.updateEntry("finished", LSUout['InstrIdx'])
        LSUtag = RoB.entries[LSUout['InstrIdx']].renameReg
    fwdList = [[ASUtag, ASUval], [MUtag, MUval], [DUtag, DUval], [LSUtag, LSUval]]
    #implement forwarding
    for tag, val in fwdList:
         asuRS.updateEntries(val, tag)
         muRS.updateEntries(val, tag)
         duRS.updateEntries(val, tag)
         lsuRS.updateEntries(val, tag)
    #commit if any instr is completed
    commitRRFtag = RoB.complete()
    if ((commitRRFtag != -1) and (commitRRFtag != -2)):
        RF.registerUpdate(commitRRFtag, 'complete', None)   # third arg isnt used during commiting
    return commitRRFtag

if __name__=="__main__":
    #global mem
    #mem = [None]*MEM_SIZE
    RF = regfiles(NUM_RRF, NUM_ARF)
    #dispBuffer = []
    asuRS = reservationStation(NUM_RSE_ASU)
    muRS = reservationStation(NUM_RSE_MU)
    duRS = reservationStation(NUM_RSE_DU)
    lsuRS = LSreservationStation(NUM_RSE_LSU)
    #
    asuFU = ASU(LATENCY_ASU)
    muFU = MU(LATENCY_MU)
    duFU = DU(LATENCY_DU)
    lsuFU = LSU(LATENCY_LSU + LATENCY_CCH)
    #
    RoB = roBuffer(NUM_ROB)
    clkCount = 0
    Decode_ptr = 0                                   # ID of instr that was last decoded
    Dispatch_ptr = 0                                 # ID of inst that was last dispatched
    with open(INS_FILE, 'r') as f:
        instructionsRaw = f.readlines()
    numInstr = len(instructionsRaw)

    while(True):
        clkCount += 1
        endSim = topModule()
        if(endSim == -1):
            break

    print("Number of Cycles elapsed: ", clkCount)
