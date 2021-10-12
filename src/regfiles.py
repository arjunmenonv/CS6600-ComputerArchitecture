class arfEntry:
    def __init__(self):
        self.data = 0
        self.busy = False
        self.tag = 0
    def print(self):
        print("Data: {}\tBusy: {}\tTag: {}".format(self.data, self.busy, self.tag))

class arf:
    def __init__(self, numEntries):
        self.entries = [arfEntry()]*numEntries
        print("Instantiated ARF")

class rrfEntry:
    def __init__(self):
        self.data = 0
        self.busy = False
        self.valid = False
    def print(self):
        print("Data: {}\tBusy: {}\tValid: {}".format(self.data, self.busy, self.valid))

class rrf:
    def __init__(self, numEntries):
        self.entries = [rrfEntry()]*numEntries
        print("Instantiated RRF")

class regfiles:
    def __init__(self, numEntriesRRF, numEntriesARF):
        self.rrf = rrf(numEntriesRRF)
        self.arf = arf(numEntriesARF)
        print("Regfiles instantiated")

    def destinationAllocate(self, arfReg):
        for index, entry in enumerate(self.rrf.entries):
            if entry.busy == False:
                entry.busy = True
                entry.valid = False
                self.arf.entries[arfReg].busy = True
                self.arf.entries[arfReg].tag = index
                break

    def registerUpdate(self, rrfIndex, type, data):
        if type=='finish':
            self.rrf.entries[rrfIndex].data = data
            self.rrf.entries[rrfIndex].valid = True
        elif type=='complete':
            for entry in self.arf.entries:
                if entry.tag == rrfIndex:
                    entry.data = self.rrf.entries[rrfIndex].data
                    entry.busy = False
                    self.rrf.entries[rrfIndex].busy = False
                    break

    def sourceRead(self, arfIndex):
        if self.arf.entries[arfIndex].busy == False:
            return self.arf.entries[arfIndex].data
        else:
            rrfIndex = self.arf.entries[arfIndex].tag
            if self.rrf.entries[rrfIndex].valid == True:
                return self.rrf.entries[rrfIndex].data
            else: # forward tag to reservation station. How2???
                print("Feature in development. Please wait")
        return -1
