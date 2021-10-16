class reservationStationEntry:
    '''
    +------+-----+-------+-----+-------+-------+
    | Busy | Op1 | Valid | Op2 | Valid | Ready |
    +------+-----+-------+-----+-------+-------+
    '''
    def __init__(self):
        self.busy = False
        self.ready = False
        self.op1 = 0
        self.valid1 = False
        self.op2 = 0
        self.valid2 = False

class reservationStation:
    def __init__(self, numEntries):
        self.entries = [reservationStationEntry()]*numEntries

    def isFull(self):
        for entry in self.entries:
            if entry.busy == True:
                return False
        return True
