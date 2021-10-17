from FU import fuEntry

class reservationStationEntry:
    '''
    +----+-----+-------+-----+-------+-------+--------+
    | ID | Op1 | Valid | Op2 | Valid | Ready | Opcode |
    +----+-----+-------+-----+-------+-------+--------+
    '''
    def __init__(self):
        self.id = None
        self.opcode = None
        self.ready = False
        self.op1 = 0
        self.valid1 = False
        self.op2 = 0
        self.valid2 = False

class LSrsEntry:
    '''
    Modifications to reservationStationEntry to accommodate LSU specific fields
    +----+-----+-------+-----+-------+--------+-------+--------+
    | ID | Op1 | Valid | Op2 | Valid | Offset | Ready | Opcode |
    +----+-----+-------+-----+-------+--------+-------+--------+
    '''
    def __init__(self):
        self.id = None
        self.opcode = None
        self.ready = False
        self.op1 = 0
        self.valid1 = False
        self.op2 = 0
        self.valid2 = False
        self.offset = 0


class reservationStation:
    def __init__(self, numEntries):
        self.entries = [reservationStationEntry()]*numEntries

    def isFull(self):
        for i, entry in enumerate(self.entries):
            if entry.id == None:
                return False, i
        return True, None

    def addEntry(self, id, opcode, ready, op1, valid1, op2, valid2):
        for entry in self.entries:
            if entry.id == None:
                entry.id = id
                entry.opcode = opcode
                entry.ready = ready
                entry.op1 = op1
                entry.valid1 = valid1
                entry.op2 = op2
                entry.valid2 = valid2
                break

    def updateEntries(self, val, regNum):
        if ((val == None) or (regNum == None)):
            return
        for entry in self.entries:
            if entry.ready == False:
                if (entry.valid1 == False) & (entry.op1 == regNum):
                    entry.op1 = val
                    entry.valid1 = True
                if (entry.valid2 == False) & (entry.op2 == regNum):
                    entry.op2 = val
                    entry.valid2 = True
                if (entry.valid1 == True) & (entry.valid2 == True):
                    entry.ready = True
        return

    def putIntoFU(self):
        nextInstrId = -1
        nextInstrOpcode = -1
        nextInstrOp1 = None
        nextInstrOp2 = None
        index = None
        for i, entry in enumerate(self.entries):
            if entry.ready == True:
                nextInstrId = entry.id
                nextInstrOpcode = entry.opcode
                nextInstrOp1 = entry.op1
                nextInstrOp2 = entry.op2
                index = i
                break
        if index != None:
            self.entries[index:-1] = self.entries[index+1:]
            self.entries[-1] = reservationStationEntry()

        return [nextInstrId, nextInstrOpcode, nextInstrOp1, nextInstrOp2]

class LSreservationStation:
    def __init__(self, numEntries):
        self.entries = [LSrsEntry()]*numEntries

    def isFull(self):
        for i, entry in enumerate(self.entries):
            if entry.id == None:
                return False, i
        return True, None

    def addEntry(self, id, opcode, ready, op1, valid1, op2, valid2, offset):
        for entry in self.entries:
            if entry.id == None:
                entry.id = id
                entry.opcode = opcode
                entry.ready = ready
                entry.op1 = op1
                entry.valid1 = valid1
                entry.op2 = op2
                entry.valid2 = valid2
                entry.offset = offset
                break

    def updateEntries(self, val, regNum):
        if ((val == None) or (regNum == None)):
            return
        for entry in self.entries:
            if entry.ready == False:
                if (entry.valid1 == False) & (entry.op1 == regNum):
                    entry.op1 = val
                    entry.valid1 = True
                if (entry.valid2 == False) & (entry.op2 == regNum):
                    entry.op2 = val
                    entry.valid2 = True
                if (entry.valid1 == True) & (entry.valid2 == True):
                    entry.ready = True
        return

    def putIntoFU(self, LSUobject):
        nextInstrId = -1
        nextInstrOpcode = -1
        nextInstrOp1 = None
        nextInstrOp2 = None
        nextInstrOffset = None
        if(LSUobject.dict['busy']):
            return
        else:
            if self.entries[0].ready == True:           # Enforce in-order Execution
                nextInstrId = self.entries[0].id
                nextInstrOpcode = self.entries[0].opcode
                nextInstrOp1 = self.entries[0].op1
                nextInstrOp2 = self.entries[0].op2
                nextInstrOffset = self.entries[0].offset
                self.entries[:-1] = self.entries[1:]
                self.entries[-1] = LSrsEntry()
            return [nextInstrId, nextInstrOpcode, nextInstrOp1, nextInstrOp2, nextInstrOffset]
