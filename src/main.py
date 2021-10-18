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
    print("put into FU from ASU :", end='')
    ASUarg = asuRS.putIntoFU()
    print("put into FU from MU :", end='')
    MUarg = muRS.putIntoFU()
    print("put into FU from DU :", end='')
    DUarg = duRS.putIntoFU()
    print("put into FU from LSU :", end='')
    LSUarg = lsuRS.putIntoFU(lsuFU)
    # pass args to FUs
    if (ASUarg != [None, None, None, None]):
        print(ASUarg)
        print("update RoB from ASU :", end='')
        RoB.updateEntry("issued", ASUarg[0])
    if (MUarg != [None, None, None, None]):
        print(MUarg)
        print("update RoB from MU :", end='')
        RoB.updateEntry("issued", MUarg[0])
    if (DUarg != [None, None, None, None]):
        print(DUarg)
        print("update RoB from DU :", end='')
        RoB.updateEntry("issued", DUarg[0])
    ASUout = asuFU.shiftAndEval(*ASUarg)
    MUout = muFU.shiftAndEval(*MUarg)
    DUout = duFU.shiftAndEval(*DUarg)
    if (LSUarg != [None, None, None, None, None]) and (LSUarg != None):
        print("update RoB from LSU :", end='')
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
    if (ASUout.instrId != None):
        RoB.updateEntry("finished", ASUout.instrId)
        ASUtag = RoB.entries[ASUout.instrId].renameReg
    if (MUout.instrId != None):
        RoB.updateEntry("finished", MUout.instrId)
        MUtag = RoB.entries[MUout.instrId].renameReg
    if (DUout.instrId != None):
        RoB.updateEntry("finished", DUout.instrId)
        DUtag = RoB.entries[DUout.instrId].renameReg
    if (LSUout['InstrIdx'] != None):
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
        print("Cycle {}".format(clkCount))
        endSim = topModule()
        if(endSim==-1):
            break
        clkCount += 1
        print("------------- Cycle over -------------")

    print("Number of Cycles elapsed: ", clkCount)
