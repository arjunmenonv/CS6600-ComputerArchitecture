import random
from replacePLRU import Tree
from replaceLRU import LRUreplace, LRUupdate
import math
from copy import copy

class cacheBlock:
    def __init__(self, tag=None):
        self.tag = tag
        if tag == None:
            self.valid = False
        else:
            self.valid = True
        self.dirty = False

    def print(self):
        print("Valid: {}    Dirty: {}    Tag: {}".format(self.valid, self.dirty, self.tag))

    def access(self, accessType:str):
        if self.valid is True:
            if accessType == 'r':
                pass
            if accessType == 'w':
                self.dirty = True
        else:
            raise ValueError("Accessing Invalid Cache Block")

class cacheSet:
    def __init__(self, assoc:int, replacementPolicy:str):
        self.assoc = assoc
        self.blocks = []
        for _ in range(assoc):
            self.blocks.extend([cacheBlock()])
        self.replacementPolicy = replacementPolicy
        if self.replacementPolicy == "LRU":
            self.LRUCounter = []
            for _ in range(self.assoc):
                self.LRUCounter.extend([-1])
        if (self.replacementPolicy == "PLRU"):
            numStages = int(math.log(assoc,2))
            self.PLRUTree = Tree(numStages)

    def emptyExists(self):
        for block in self.blocks:
            if block.valid == False:
                return True
        return False

    def accessBlock(self, blockTag, accessType):
        for idx, block in enumerate(self.blocks):
            idx += 1
            if block.tag == blockTag: # block in cache - return hit (True)
                block.access(accessType)
                if (self.replacementPolicy == "PLRU"):
                    self.PLRUTree.traverse(idx)
                elif self.replacementPolicy == "LRU":
                    self.LRUCounter = LRUupdate(self.LRUCounter, idx)
                return True, None
        # if comes here, then block with given tag not in cache
        # bring to cache, and return miss (False)
        newBlock = cacheBlock(blockTag)
        newBlock.access(accessType)
        status, replaceBlock = self.insert(newBlock)
        if status == 0:
            return False, None
        else:
            return False, replaceBlock

    def replace(self):
        if self.replacementPolicy == "RANDOM":
            replacementCandidate = random.randint(0,self.assoc-1)
        elif self.replacementPolicy == "LRU":
            replacementCandidate = LRUreplace(self.LRUCounter)
        elif self.replacementPolicy == "PLRU":
            replacementCandidate = self.PLRUTree.getVictim()
        else:
            raise ValueError("Invalid Replacement Policy for cache set: ", self.replacementPolicy)
        return replacementCandidate

    def insert(self, newBlock):
        flag = -1
        for i, block in enumerate(self.blocks):
            if block.valid == False: # empty block
                block.valid = newBlock.valid
                block.tag = newBlock.tag
                block.dirty = newBlock.dirty
                if (self.replacementPolicy == "PLRU"):
                    self.PLRUTree.traverse(i)
                elif self.replacementPolicy == "LRU":
                    self.LRUCounter = LRUupdate(self.LRUCounter, i)
                flag = 1
                break
        if flag == -1: # no empty block - replace
            replacementCandidate = self.replace()
            replacedBlock = copy(self.blocks[replacementCandidate])
            self.blocks[replacementCandidate].valid = True
            self.blocks[replacementCandidate].dirty = False
            self.blocks[replacementCandidate].tag = newBlock.tag
            return 1, replacedBlock
        return 0, None

class cache:
    def __init__(self, numSets, assoc, replacementPolicy):
        self.numSets = numSets
        self.assoc = assoc
        self.replacementPolicy = replacementPolicy
        self.history = []
        self.numAccesses = 0
        self.numReads = 0
        self.numWrites = 0
        self.numHits = 0
        self.numMisses = 0
        self.numCompMisses = 0
        self.numCapMisses = 0
        self.numConfMisses = 0
        self.numReadMisses = 0
        self.numWriteMisses = 0
        self.numDEs = 0
        self.cacheSets = []
        for _ in range(self.numSets):
            self.cacheSets.extend([cacheSet(self.assoc, self.replacementPolicy)])

    def memRequest(self, blockAddress, accessType):
        self.numAccesses += 1
        if accessType == 'r':
            self.numReads += 1
        elif accessType == 'w':
            self.numWrites += 1
        else:
            raise ValueError("Invalid Access Type")
        setIndex = blockAddress % self.numSets
        blockTag = blockAddress//self.numSets
        reqStatus, retBlock = self.cacheSets[setIndex].accessBlock(blockTag, accessType)
        if reqStatus == True:
            self.numHits += 1
        else:
            self.numMisses += 1
            if accessType == 'r':
                self.numReadMisses += 1
            elif accessType == 'w':
                self.numWriteMisses += 1
            if blockAddress not in self.history:
                self.history.extend([blockAddress])
                self.numCompMisses += 1
            else:
                flag = 0
                for set in self.cacheSets:
                    if set.emptyExists() == True:
                        self.numConfMisses += 1
                        flag = 1
                        break
                if flag == 0:
                    self.numCapMisses += 1
            if retBlock is not None:
                if retBlock.dirty is True:
                    self.numDEs += 1
    def printStats(self):
        print("----------- Simulation Results -----------")
        print("Number of Accesses:", self.numAccesses)
        print("Number of Reads:", self.numReads)
        print("Number of Writes:", self.numWrites)
        print("Number of Hits:", self.numHits)
        print("Number of Misses:", self.numMisses)
        print("Number of Read Misses:", self.numReadMisses)
        print("Number of Write Misses:", self.numWriteMisses)
        print("Number of Compulsory Misses:", self.numCompMisses)
        print("Number of Capacity Misses:", self.numCapMisses)
        print("Number of Conflict Misses:", self.numConfMisses)
        print("Number of Dirty Evictions:", self.numDEs)
        print("------------------------------------------")
