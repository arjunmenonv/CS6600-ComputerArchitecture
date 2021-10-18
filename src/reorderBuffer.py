class roBufferEntry:
    '''
    +------+--------+----------+-----------+
    | Busy | Issued | Finished | RenameReg |
    +------+--------+----------+-----------+

    Branch Pred specific fields (speculative, valid) are not used here
    '''
    def __init__(self):
        self.busy = 0
        self.issued = 0         # = 1 when instruction is pushed to FU from RS
        self.finished = 0
        self.renameReg = -1     # holds dest rrf index, init to an invalid location
    def print(self):
        print("Busy: {}\tIssued: {}\tFinished: {}\tRenameReg: {}".format\
        (self.busy, self.issued, self.finished, self.renameReg))

class roBuffer:
    '''
    +-------+------+--------+----------+-----------+
    | Index | Busy | Issued | Finished | RenameReg |
    +-------+------+--------+----------+-----------+
    | 0     |      |        |          |           |
    +-------+------+--------+----------+-----------+
    | 1     |      |        |          |           |
    +-------+------+--------+----------+-----------+
    | 2     |      |        |          |           |
    +-------+------+--------+----------+-----------+
    | 3     |      |        |          |           |
    +-------+------+--------+----------+-----------+
    ...
    ...
    ...
    +-------+------+--------+----------+-----------+
    | N-1   |      |        |          |           |
    +-------+------+--------+----------+-----------+
    '''
    def __init__(self, numEntries:int):
        self.entries = []
        for _ in range(numEntries):
            self.entries.extend([roBufferEntry()])
        self.head = 0
        self.tail = 0
        self.full = 0
        self.empty = 1
        self.len = numEntries

    def updateState(self):
        self.empty = 0
        self.full = 0
        if ((self.tail - self.head)%self.len == self.len - 1):
            self.full = 1
        elif (self.tail == self.head):
            self.empty = 1

    def insertEntry(self, rrfTag):
        '''
        This function is called from dispatch()
        call updateState() before calling this function and stall if ROBuffer is full,
        else carry on
        '''
        self.tail = (self.tail + 1)%self.len
        self.entries[self.tail].busy = 1
        self.entries[self.tail].issued = 0
        self.entries[self.tail].finished = 0
        self.entries[self.tail].renameReg = rrfTag
        return self.tail        # save this as InstrIdx in RS

    def complete(self):
        self.updateState()
        if self.empty:
            print("No instruction left to complete")
            return -1
        else:
            if(self.entries[self.head].finished):
                self.entries[self.head].busy = 0
                rrfTag = self.entries[self.head].renameReg
                self.head = (self.head + 1)%self.len
                return rrfTag
            else:
                return -2           # head instr isnt finished

    def updateEntry(self, type:str, index):
        self.updateState()
        if self.empty:
            print("Reorder Buffer is empty")
            return
        else:
            if (type == "issued"):
                self.entries[index].issued = 1
            elif (type == "finished"):
                self.entries[index].finished = 1
            return
