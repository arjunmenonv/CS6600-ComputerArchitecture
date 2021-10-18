from conf import *
from instructionDecoder import *
from reorderBuffer import *
from regfiles import *
from reservationStation import *
from FU import *
from dispatchBuffer import *

RF = regfiles(NUM_RRF, NUM_ARF)
RoB = roBuffer(NUM_ROB)

asuRS = reservationStation(NUM_RSE_ASU)
muRS = reservationStation(NUM_RSE_MU)
duRS = reservationStation(NUM_RSE_DU)
lsuRS = LSreservationStation(NUM_RSE_LSU)

asuFU = ASU(LATENCY_ASU)
muFU = MU(LATENCY_MU)
duFU = DU(LATENCY_DU)
lsuFU = LSU(LATENCY_LSU + LATENCY_CCH)

clkCount = 0
progCounter = 0
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
    Decode_count = 0
    print("Decoding Instructions...")
    if (progCounter < numInstr):
        for i in range(DECODE_MAX):
            if instructionsDecoded[i] == None:
                instructionsDecoded[i] = decode(instructionsRaw[progCounter])
                progCounter+=1
                if instructionsDecoded[i] == None:
                    break
                Decode_count+=1
                if progCounter == numInstr:
                    break
    print("Decoded {} new instructions".format(Decode_count))
    print("Dispatching Instructions...")
    while((Dispatch_count < ISSUE_WIDTH) & (instructionsDecoded[0] != None)):
        print(instructionsDecoded[0])
        stall = dispatch(instructionsDecoded[0], asuRS, muRS, duRS, lsuRS, RF, RoB)
        if stall:
            print("\tDispatch Stalled")
            break
        else:
            Dispatch_count+=1
            instructionsDecoded[0:-1] = instructionsDecoded[1:]
            instructionsDecoded[-1] = None
    print("Dispatched {} instructions to respective RS".format(Dispatch_count))
    print("Issuing instructions to FUs...")
    ASUarg = asuRS.putIntoFU()
    MUarg = muRS.putIntoFU()
    DUarg = duRS.putIntoFU()
    LSUarg = lsuRS.putIntoFU(lsuFU)
    Issue_count = 0
    # pass args to FUs
    if (ASUarg[0] != None):
        Issue_count += 1
        print("\tTo ASU: ", end='')
        print(ASUarg)
        print("\tUpdate RoB from ASU :", end='')
        RoB.updateEntry("issued", ASUarg[0])
    if (MUarg[0] != None):
        Issue_count += 1
        print("\tTo MU: ", end='')
        print(MUarg)
        print("\tUpdate RoB from MU :", end='')
        RoB.updateEntry("issued", MUarg[0])
    if (DUarg[0] != None):
        Issue_count += 1
        print("\tTo DU: ", end='')
        print(DUarg)
        print("\tUpdate RoB from DU :", end='')
        RoB.updateEntry("issued", DUarg[0])
    ASUout = asuFU.shiftAndEval(*ASUarg)
    MUout = muFU.shiftAndEval(*MUarg)
    DUout = duFU.shiftAndEval(*DUarg)
    if (LSUarg[0] != None):
        Issue_count += 1
        print("\tTo LSU: ", end='')
        print(LSUarg)
        print("\tUpdate RoB from LSU :", end='')
        lsuFU.IssueNewOp(clkCount, *LSUarg)
        RoB.updateEntry("issued", LSUarg[0])
    LSUout = lsuFU.pollLSU(clkCount)
    print("Issued {} non-NOP instructions".format(Issue_count))
    print("Finishing Instructions...")
    Finish_count = 0
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
        Finish_count += 1
        print("\tUpdate RoB from ASU: ", end='')
        RoB.updateEntry("finished", ASUout.instrId)
        ASUtag = RoB.entries[ASUout.instrId].renameReg
    if (MUout.instrId != None):
        Finish_count += 1
        print("\tUpdate RoB from MU: ", end='')
        RoB.updateEntry("finished", MUout.instrId)
        MUtag = RoB.entries[MUout.instrId].renameReg
    if (DUout.instrId != None):
        Finish_count += 1
        print("\tUpdate RoB from DU: ", end='')
        RoB.updateEntry("finished", DUout.instrId)
        DUtag = RoB.entries[DUout.instrId].renameReg
    if (LSUout['InstrIdx'] != None):
        Finish_count += 1
        print("\tUpdate RoB from LSU: ", end='')
        RoB.updateEntry("finished", LSUout['InstrIdx'])
        LSUtag = RoB.entries[LSUout['InstrIdx']].renameReg
    print("Finished {} instructions".format(Finish_count))
    fwdList = [[ASUtag, ASUval], [MUtag, MUval], [DUtag, DUval], [LSUtag, LSUval]]
    print("Forwarding FU outputs: ")
    print("\tFrom ASU: tag =", fwdList[0][0], "| data =", fwdList[0][1])
    print("\tFrom MU:  tag =", fwdList[1][0], "| data =", fwdList[1][1])
    print("\tFrom DU:  tag =", fwdList[2][0], "| data =", fwdList[2][1])
    print("\tFrom LSU: tag =", fwdList[3][0], "| data =", fwdList[3][1])
    #implement forwarding
    for tag, val in fwdList:
         asuRS.updateEntries(val, tag)
         muRS.updateEntries(val, tag)
         duRS.updateEntries(val, tag)
         lsuRS.updateEntries(val, tag)
         RF.registerUpdate(tag, 'finish', val)
    #commit if any instr is completed
    print("Committing ROB head...")
    commitRRFtag = RoB.complete()
    if ((commitRRFtag != -1) and (commitRRFtag != -2)):
        RF.registerUpdate(commitRRFtag, 'complete')   # third arg isnt used during commiting
        print("\tCompleted head instruction")
    return commitRRFtag

if __name__=="__main__":
    with open(INS_FILE, 'r') as f:
        instructionsRaw = f.read().splitlines()
    numInstr = len(instructionsRaw)
    while(True):
        print("------------- Cycle {} start -------------".format(clkCount))
        endSim = topModule()
        print("Reorder Buffer:\t Head:{}\t Tail:{}".format(RoB.head, RoB.tail))
        print("------------- Cycle {} end   -------------".format(clkCount))
        if(endSim==-1):
            break
        clkCount += 1

    print("Number of Cycles elapsed: ", clkCount)
    if exceptions:
        print("\nThe following EXCEPTIONs were encountered:")
        for e in exceptions:
            print(e)
