import argparse as ap
from inc.opts import *
from inc.parser import inputParser
from memory import memory
from translator import translate
from process import proc

def args():
    '''
    Parse command-line arguments

    '''
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, metavar='file', help="Input file with requests", required=True)
    args = parser.parse_args()
    return args

def main():
    '''
    Main simulation function

    '''
    activeProcesses = [None]*NPROC
    userMem = memory()
    kernelMem = memory(256, 1024, "kernel")
    inFile = args().input
    fileParser = inputParser(inFile)
    reqs = fileParser.parse()
    totalRequests = len(reqs)
    totalHits = 0
    totalMisses = 0
    totalPageReplacements = 0
    totalTableReplacements = 0
    totalReads = 0
    totalWrites = 0
    for req in reqs:
        if req.typ == 'r':
            totalReads += 1
        elif req.typ == 'w':
            totalWrites += 1
        # check if the request is from a new process
        if activeProcesses[req.pid] == None:
            newProc = proc(req.pid)
            activeProcesses[req.pid] = newProc
        offsets = translate(req.va)
        p = activeProcesses[req.pid]
        page, rv1, rv2 = p.pagewalk(kernelMem, userMem, offsets)

        if rv1[0] != 0:
            evictedPID, evictedOffset, evictedTable = rv1[1], rv1[2], rv1[3]
            for pr in activeProcesses:
                if pr != None:
                    if pr.pid == evictedPID:
                        pr.pTableCopy[evictedTable][evictedOffset] = None

        if rv2[0] != 0:
            evictedUserFrame = rv2[1]
            for pr in activeProcesses:
                if pr != None:
                    pr.pTableCopy[pr.pTableCopy == evictedUserFrame] = None

        
    for p in activeProcesses:
        if p != None:
            totalHits += p.hits
            totalMisses += p.misses
    print('Total Requests: {}'.format(totalRequests))
    print('Hit Rate: {:.2f}%'.format(100*totalHits/totalRequests))
    print('Miss Rate: {:.2f}%'.format(100*totalMisses/totalRequests))
    print('Read Requests: {}'.format(totalReads))
    print('Write Requests: {}'.format(totalWrites))
    for p in activeProcesses:
        if p != None:
            print('PID {}: {} requests'.format(p.pid, p.requests))
            totalPageReplacements += p.pageEvictions
            totalTableReplacements += p.tableEvictions
    print('Dirty Page Evictions: {}'.format(totalPageReplacements))
    print('Dirty Table Evictions: {}'.format(totalTableReplacements))

if __name__=="__main__":
    main()
    # print("Please check back later. In development")


'''
Test run

userMem = memory()
kernelMem = memory(256, 1024, "kernel")
print("Testing __init__()")
userMem.updateLRU(65)
userMem.updateLRU(64)
kernelMem.updateLRU(9)
kernelMem.updateLRU(7)
kernelMem.updateLRU(8)
userMem.updateLRU(63)
userMem.updateLRU(0)
kernelMem.updateLRU(7)
kernelMem.updateLRU(0)
userMem.updateLRU(64)
print(userMem.LRUctr[0:6], userMem.LRUctr[62:66], userMem.freeFrames.qsize())
print(kernelMem.LRUctr[0:10], kernelMem.freeFrames.qsize())
print(userMem.evictFrame(), kernelMem.evictFrame())
print(userMem.invalidateEntry("user", 20))
print(kernelMem.invalidateEntry("kernel", 20))
'''
