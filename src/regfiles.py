class arfEntry:
    '''
    +------+------+-----+
    | Data | Busy | Tag |
    +------+------+-----+
    '''
    def __init__(self):
        self.data = 0
        self.busy = False
        self.tag = 0
    def print(self):
        print("Data: {}\tBusy: {}\tTag: {}".format(self.data, self.busy, self.tag))

class arf:
    '''
   +---+------+------+-----+
   |   | Data | Busy | Tag |
   +---+------+------+-----+
   | 0 |      |      |     |
   +---+------+------+-----+
   | 1 |      |      |     |
   +---+------+------+-----+
   | 2 |      |      |     |
   +---+------+------+-----+
   ....
   ....
   ....
   +---+------+------+-----+
   | N |      |      |     |
   +---+------+------+-----+
    '''
    def __init__(self, numEntries):
        self.entries = [arfEntry()]*numEntries
        print("Instantiated ARF")

class rrfEntry:
    '''
    +------+------+-------+
    | Data | Busy | Valid |
    +------+------+-------+
    '''
    def __init__(self):
        self.data = 0
        self.busy = False
        self.valid = False
    def print(self):
        print("Data: {}\tBusy: {}\tValid: {}".format(self.data, self.busy, self.valid))

class rrf:
    '''
   +---+------+------+-------+
   |   | Data | Busy | Valid |
   +---+------+------+-------+
   | 0 |      |      |       |
   +---+------+------+-------+
   | 1 |      |      |       |
   +---+------+------+-------+
   | 2 |      |      |       |
   +---+------+------+-------+
   ....
   ....
   ....
   +---+------+------+-------+
   | N |      |      |       |
   +---+------+------+-------+
    '''
    def __init__(self, numEntries):
        self.entries = [rrfEntry()]*numEntries
        print("Instantiated RRF")

class regfiles:
    '''
    +==========================+
    |  +-------+    +-------+  |
    |  |       |    |       |  |
    |  |  ARF  |    |  RRF  |  |
    |  |       |    |       |  |
    |  +-------+    +-------+  |
    |      |            |      |
    |   +------------------+   |
    |   |                  |   |
    |   |       Logic      |   |
    |   |                  |   |
    |   +------------------+   |
    |             |            |
    | +----------------------+ |
    | | Data / Tag forwarded | |
    | +----------------------+ |
    +==========================+

    '''
    def __init__(self, numEntriesRRF, numEntriesARF):
        self.rrf = rrf(numEntriesRRF)
        self.arf = arf(numEntriesARF)
        print("Regfiles instantiated")

    def destinationAllocate(self, arfReg):
        for index, entry in enumerate(self.rrf.entries):
            if entry.busy == False: # RRF entry is free. Allocate this
                entry.busy = True
                entry.valid = False
                self.arf.entries[arfReg].busy = True
                self.arf.entries[arfReg].tag = index
                break

    def registerUpdate(self, rrfIndex, type, data):
        if type=='finish': # Update data from FU in RRF
            self.rrf.entries[rrfIndex].data = data
            self.rrf.entries[rrfIndex].valid = True
        elif type=='complete': # Update from RRF to ARF and deallocate RRF and ARF
            for entry in self.arf.entries:
                if entry.tag == rrfIndex:
                    entry.data = self.rrf.entries[rrfIndex].data
                    entry.busy = False
                    self.rrf.entries[rrfIndex].busy = False
                    break

    def sourceRead(self, arfIndex):
        if self.arf.entries[arfIndex].busy == False: # return data from ARF
            return self.arf.entries[arfIndex].data
        else:
            rrfIndex = self.arf.entries[arfIndex].tag
            if self.rrf.entries[rrfIndex].valid == True: # return data from RRF
                return self.rrf.entries[rrfIndex].data
            else: # forward tag to reservation station
                return rrfIndex
