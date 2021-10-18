from conf import *
from instructionDecoder import *
from reorderBuffer import *
from regfiles import *
from reservationStation import *
from FU import *
from dispatchBuffer import *

progCounter = 0
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
instructionsDecoded = [None]*DECODE_MAX

def topModule():
    '''
    Top Module: Performs one run of ID, Dispatch, EX, RoBComplete operations
    '''
    global progCounter
    global RF
    global asuRS, asuFU
    global muRS, muFU
    global duRS, duFU
    global lsuRS, lsuFU
    global RoB
    global numInstr
    global instructionsDecoded

    Dispatch_count = 0
    if (progCounter < numInstr):
        for i in range(DECODE_MAX):
            if instructionsDecoded[i] == None:
                instructionsDecoded[i] = decode(instructionsRaw[progCounter])
                progCounter+=1
                if progCounter == numInstr:
                    break
    while((Dispatch_count < ISSUE_WIDTH) & (instructionsDecoded[0] != None)):
        print(instructionsDecoded[0])
        stall = dispatch(instructionsDecoded[0], asuRS, muRS, duRS, lsuRS, RF, RoB)
        if stall:
            print("Dispatch Stalled")
            break
        else:
            Dispatch_count+=1
            instructionsDecoded[0:-1] = instructionsDecoded[1:]
            instructionsDecoded[-1] = None
    print("Finished dispatching")
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
    if (LSUarg != [-1, -1, None, None, None]) or (LSUarg != None):
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
         RF.registerUpdate(tag, 'finish', val)
    #commit if any instr is completed
    commitRRFtag = RoB.complete()
    if ((commitRRFtag != -1) and (commitRRFtag != -2)):
        RF.registerUpdate(commitRRFtag, 'complete')   # third arg isnt used during commiting
    return commitRRFtag

if __name__=="__main__":
    with open(INS_FILE, 'r') as f:
        instructionsRaw = f.read().splitlines()
    numInstr = len(instructionsRaw)
    while(True):
        endSim = topModule()
        if(endSim==-1):
            break
        clkCount += 1

    print("Number of Cycles elapsed: ", clkCount)
