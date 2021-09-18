import numpy as np
class proc:
    def __init__(self, pid):
        self.pid = pid
        self.hits = 0
        self.misses = 0
        self.pTableCopy = [None]*1024

    def pagewalk(self, kernelMem, userMem, offsets):
        dirOffset = offsets[0]
        tabOffset = offsets[1]
        pDir = kernelMem.mem[self.pid]
        pTableMiss = False
        pMiss = False

        # Check if page table present or not
        # Bring it to memory and continue if not
        if pDir[dirOffset] == None:
            pTableMiss = True
            if kernelMem.freeFrames.empty():
                evictedKernelFrame = kernelMem.evictFrame()
                kernelMem.invalidateEntry("kernel", evictedKernelFrame)
            mappedKernelFrame = kernelMem.freeFrames.get()
            pDir[dirOffset] = mappedKernelFrame

        pTable = pDir[dirOffset]
        kernelMem.updateLRU(pTable)

        # Check if page present or not
        # Bring it to memory and continue if not
        if pTable[tabOffset] == None:
            pMiss = True
            if userMem.freeFrames.empty():
                evictedUserFrame = userMem.evictFrame()
                userMem.invalidateEntry("user", evictedUserFrame)
            mappedUserFrame = userMem.freeFrames.get()
            pTable[tabOffset] = mappedUserFrame

        page = pTable[tabOffset]
        userMem.updateLRU(page)

        if pTableMiss:
            self.misses += 1
        else:
            if pMiss:
                self.misses += 1
            else:
                self.hits += 1
