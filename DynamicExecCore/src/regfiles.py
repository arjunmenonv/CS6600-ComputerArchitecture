class arfEntry:
    '''
    +------+------+-----+
    | Data | Busy | Tag |
    +------+------+-----+
    '''
    def __init__(self):
        self.data = 1
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
        self.entries = []
        for _ in range(numEntries):
            self.entries.extend([arfEntry()])

class rrfEntry:
    '''
    +------+------+-------+
    | Data | Busy | Valid |
    +------+------+-------+
    '''
    def __init__(self):
        self.data = 1
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
        self.entries = []
        for _ in range(numEntries):
            self.entries.extend([rrfEntry()])


class regfiles:
    '''
    Parameters:

    numEntriesRRF (int): Number of entries in rename regfile
    numEntriesARF (int): Number of entries in arch. regfile


    Block Diagram:

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
    def __init__(self, numEntriesRRF:int, numEntriesARF:int):
        self.rrf = rrf(numEntriesRRF)
        self.arf = arf(numEntriesARF)

    def getFreeIdx(self):
        for index, entry in enumerate(self.rrf.entries):
            if entry.busy == False: # RRF entry is free. Allocate this
                return index, entry
        return None, None

    def destinationAllocate(self, index:int, entry:rrfEntry, arfReg:int):
        if entry.busy == True:          # sanity check
            print("Exception; destination allocation failed, exiting")
            exit()
        else:
            entry.busy = True
            entry.valid = False
            self.arf.entries[arfReg].busy = True
            self.arf.entries[arfReg].tag = index

    def registerUpdate(self, rrfIndex:int, type:str, data:int = None):
        if rrfIndex != None:
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

    def sourceRead(self, arfIndex:int):
        if self.arf.entries[arfIndex].busy == False: # return data from ARF
            return self.arf.entries[arfIndex].data, True
        else:
            rrfIndex = self.arf.entries[arfIndex].tag
            if self.rrf.entries[rrfIndex].valid == True: # return data from RRF
                return self.rrf.entries[rrfIndex].data, True
            else: # forward tag to reservation station
                return rrfIndex, False

# simple test to see if working properly
if __name__=="__main__":
    rf = regfiles(numEntriesARF=32, numEntriesRRF=8)
    print("Architecture RegFile")
    for i, entry in enumerate(rf.arf.entries):
        print("{}".format(i), end='\t')
        entry.print()
    print("Rename RegFile")
    for i, entry in enumerate(rf.rrf.entries):
        print("{}".format(i), end='\t')
        entry.print()
