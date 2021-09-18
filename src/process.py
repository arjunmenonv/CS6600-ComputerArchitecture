import numpy as np
class proc:
    def __init__(self, pid):
        self.pid = pid
        self.pTableHits = 0
        self.pTableMisses = 0
        self.pageHits = 0
        self.pageMisses = 0
        self.pTableCopy = [[None]*1024]*1024   # Helper array to model copy of page Table in disk

    def pagewalk(self, kernelMem, userMem, offsets):
        dirOffset = offsets[0]
        tabOffset = offsets[1]
        pDir = kernelMem.mem[self.pid]
        pTableMiss = False
        pMiss = False
        wb = 0
        inv_copy = 0
        # Check if page table present or not
        # Bring it to memory and continue if not
        if pDir[dirOffset] == None:
            pTableMiss = True
            if kernelMem.freeFrames.empty():
                evictedKernelFrame = kernelMem.evictFrame()
                ev_Table = kernelMem.mem[evictedKernelFrame]
                wb, ev_pid, ev_offset = kernelMem.invalidateEntry("kernel", evictedKernelFrame)
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
                evictedUserFrame = userMem.evictFrame()
                inv_copy = kernelMem.invalidateEntry("user", evictedUserFrame)
            mappedUserFrame = userMem.freeFrames.get()
            pTable[tabOffset] = mappedUserFrame

        pageAddr = pTable[tabOffset]
        page = userMem.mem[pageAddr]
        userMem.updateLRU(pageAddr)

        if pTableMiss:
            self.pTableMisses += 1
        else:
            self.pTableHits += 1
        if pMiss:
            self.pageMisses += 1
        else:
            self.pageHits += 1

        if wb:
            rvec1 = [wb, ev_pid, ev_offset, ev_Table]
        else:
            rvec1 = [wb, None, None, None]
        if inv_copy:
            rvec2 = [inv_copy, evictedUserFrame]
        else:
            rvec2 = [inv_copy, None]

        return page, rvec1, rvec2
