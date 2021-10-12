class arf:
    def __init__(self, numEntries):
        self.data = [None]*numEntries
        self.busy = [False]*numEntries
        self.tag = [None]*numEntries
        print("Instantiated ARF")

class rrf:
    def __init__(self, numEntries):
        self.data = [None]*numEntries
        self.valid = [False]*numEntries
        self.busy = [False]*numEntries
        print("Instantiated RRF")

class regfiles:
    def __init__(self, numEntriesRRF, numEntriesARF):
        self.rrf = rrf(numEntriesRRF)
        self.arf = arf(numEntriesARF)
        print("Regfiles instantiated")
