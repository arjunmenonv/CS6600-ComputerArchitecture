'''
MMU Simulator in python
Assignment 3, Computer Architecture
Authors: Akilesh K, Arjun Menon V
Sept 2021
Main Module: - Create kernel memory, user memory and process objects
             - Call functions for pagewalk, page eviction (LRU policy) and writing evicted PageTable
               back to Disk (WriteBack policy)
'''
import numpy as np
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
    '''
     - kernel memory allocation type 1: give MMU access to the entire kernel space
     - for 0 page table evictions for the given page access pattern, only 40 page frames are needed by the mmu
    '''
    kernelMem = memory(256, 1024, "kernel")
    # kernel memory allocation type 2: Reserving only 64K for Page Directories and Page Tables
    #kernelMem = memory(16, 1024, "kernel")
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
                        pr.pTableCopy[evictedOffset] = evictedTable

        if rv2[0] != 0:
            evictedUserFrame = rv2[1]
            for pr in activeProcesses:
                if pr != None:
                    for table in pr.TableCopy:
                        for entry in table:
                            if entry == evictedUserFrame:
                                entry = None

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

    totalKernelPFUsed = max(kernelMem.LRUctr)+1
    totalUserPFUsed = max(userMem.LRUctr)+1
    numActiveProcesses = 0
    for p in activeProcesses:
        if p != None:
            numActiveProcesses += 1
    print(totalKernelPFUsed)
    print(totalUserPFUsed)
    print(numActiveProcesses)
    print('Final number of pageframes used: {}'.format(totalKernelPFUsed+totalUserPFUsed+numActiveProcesses))


if __name__=="__main__":
    main()
    # print("Please check back later. In development")
