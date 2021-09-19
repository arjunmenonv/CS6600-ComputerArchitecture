'''
MMU Simulator in python
Assignment 3, Computer Architecture
Authors: Akilesh K, Arjun Menon V
Sept 2021
Class Definition for the proc module
'''
import numpy as np

class proc:
    def __init__(self, pid):
        self.pid = pid
        self.hits = 0
        self.misses = 0
        self.requests = 0
        self.pageEvictions = 0
        self.tableEvictions = 0
        self.pTableCopy = [[None]*1024]*1024   # Helper array to model copy of page Table in disk

    def pagewalk(self, kernelMem, userMem, offsets):
        self.requests += 1
        dirOffset = offsets[0]
        tabOffset = offsets[1]
        pDir = kernelMem.mem[self.pid]
        pTableMiss = False
        pMiss = False
        wb = 0
        invalidateCopy = 0
        # Check if page table present or not
        # Bring it to memory and continue if not
        if pDir[dirOffset] == None:
            pTableMiss = True
            if kernelMem.freeFrames.empty():
                self.tableEvictions += 1
                evictedKernelFrame = kernelMem.evictFrame()
                evictedTable = kernelMem.mem[evictedKernelFrame]
                wb, evictedPID, evictedOffset = kernelMem.invalidateEntry("kernel", evictedKernelFrame)
            mappedKernelFrame = kernelMem.freeFrames.get()
            pDir[dirOffset] = mappedKernelFrame
            # in case of pTable Miss, write the Page Table Entry from "disk"
            kernelMem.mem[pDir[dirOffset]] = self.pTableCopy[dirOffset]

        pTableAddr = pDir[dirOffset]
        pTable = kernelMem.mem[pTableAddr]
        kernelMem.updateLRU(pTableAddr)

        # Check if page present or not
        # Bring it to memory and continue if not
        if pTable[tabOffset] == None:
            pMiss = True
            if userMem.freeFrames.empty():
                self.pageEvictions += 1
                evictedUserFrame = userMem.evictFrame()
                invalidateCopy = kernelMem.invalidateEntry("user", evictedUserFrame)
            mappedUserFrame = userMem.freeFrames.get()
            pTable[tabOffset] = mappedUserFrame

        pageAddr = pTable[tabOffset]
        page = userMem.mem[pageAddr]
        userMem.updateLRU(pageAddr)

        if pTableMiss:
            self.misses += 1
        else:
            if pMiss:
                self.misses += 1
            else:
                self.hits += 1

        if wb:
            rvec1 = [wb, evictedPID, evictedOffset, evictedTable]
        else:
            rvec1 = [wb, None, None, None]
        if invalidateCopy:
            rvec2 = [invalidateCopy, evictedUserFrame]
        else:
            rvec2 = [invalidateCopy, None]

        return page, rvec1, rvec2
