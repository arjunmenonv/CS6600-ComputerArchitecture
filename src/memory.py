'''
MMU Simulator in python
Assignment 3, Computer Architecture
Authors: Akilesh K, Arjun Menon V
Sept 2021
Class Definition for the memory module
Notes: - 'mem' array in memory objects of "user" type has granularity of 1 byte,
         while in objects of "kernel" type, the granularity is 4 bytes
       - Assumption: First NPROC frames in kernel space are allocated to Page Directories
       - evictframe() returns victim frame number; use this to update PDEvalid or PTEvalid from pagewalk()
'''
from sys import exit
import numpy as np
from inc.opts import *
from queue import Queue as Q

class memory:
    '''
    memory(numFrames, entriesPerFrame, memType)

    Fields:
    -------
    numFrames: int
        Number of page frames in the memory

    memType: str
        Kernel/user land indicator

    mem: 2D array (int)
        Memory array

    LRUctr: 1D array (int)
        LRU counter array, 1 entry per page frame
        -1 if empty/free

    freeFrames: Queue
        FIFO to maintain free pages in memory

    valid: 2D array (int)
        PRESENT ONLY FOR KERNEL MEMORY!!!
        indicates whether the page pointed to by the
        entry is in memory or not

    '''
    def __init__(self, numFrames= 768, entriesPerFrame = 4096, memType= "user"):
        self.numFrames = numFrames
        self.memType= memType
        self.mem = np.zeros((self.numFrames, entriesPerFrame), dtype= int)
        self.LRUctr = (-1)*np.ones(self.numFrames, dtype= int)
        if(self.memType == "user"):
            self.freeFrames = Q(self.numFrames)
            # initialise FIFO to include all page frames
            for i in range(self.numFrames):
                self.freeFrames.put(i)          
        else:
            if (self.numFrames <= NPROC):
                print("Insufficient space allocated to MMU in Kernel Space, exiting!")
                exit(-1)
            self.valid = np.zeros((self.numFrames, entriesPerFrame), dtype= bool)
            self.freeFrames = Q(self.numFrames-NPROC)
            for i in range(NPROC, self.numFrames): # page directories cannot be replaced
                self.freeFrames.put(i)          

    def updateLRU(self, hitPage):
        currCount = self.LRUctr[hitPage]
        if (currCount == -1): # page was previously free, inc LRUctr of all active frames by 1
            if((self.memType == "user") or (hitPage >= NPROC)): # PDframes not present in FIFO
                self.updateFIFO(hitPage)
            for i in range(self.numFrames):
                if(self.LRUctr[i] != -1):
                    self.LRUctr[i] += 1
        else:
            for i in range(self.numFrames):
                # inc LRUctr of all frames that were used btw prev access to current frame and now
                if((self.LRUctr[i] != -1) and (self.LRUctr[i] < currCount)):
                    self.LRUctr[i] += 1
        self.LRUctr[hitPage] = 0
        return 0

    def updateFIFO(self, hitPage):
        # update free frames by removing the hit page(if it exists) from them
        tempSize = self.freeFrames.qsize()
        temp = Q(tempSize)
        for i in range(tempSize):
            tempVal = self.freeFrames.get()
            if(tempVal != hitPage):
                temp.put(tempVal)
        for i in range(tempSize-1):
            self.freeFrames.put(temp.get())
        return 0

    def evictFrame(self):
        # Call this ONLY IF FIFO is empty
        if (self.freeFrames.empty()):
            if (self.memType == "user"):
                victimFrame = np.argmax(self.LRUctr)
                self.freeFrames.put(victimFrame)
                self.LRUctr[victimFrame] = -1
            else:
                victimFrame = np.argmax(self.LRUctr[NPROC:-1]) # do not evict Page Directory
                self.freeFrames.put(victimFrame)
                self.LRUctr[victimFrame] = -1
            return victimFrame
        return -1

    def invalidateEntry(self, targType, victim):
        if (self.memType == "kernel"):
            if (targType == "user"): # update valid field in PTE
                frame, entry = np.where((self.mem[NPROC:][:] == victim)) # search amongst PTEs
                frame = frame[0]; entry = entry[0]
                self.valid[frame][entry] = 0    #invalidate
            else:
                frame, entry = np.where((self.mem[0:NPROC][:] == victim)) # search amongst PDEs
                frame = frame[0]; entry = entry[0]
                self.valid[frame][entry] = 0
            return 0
        return -1
