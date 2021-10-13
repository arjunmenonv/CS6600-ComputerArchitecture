class FU:
    def __init__(self, latency, type):
        self.latency = latency
        self.type = type
        '''
        InstrIdx => Reorder Buffer index, RegVal => value to be written to RenameReg & forwarded
        opCode:
            "add":  1 => add, 0 => sub
            "mult": 1 => mult, 0 => div
            "mem":  1 => load, 0 => store
            when no instruction is issued by RS, set opCode = -1
        '''
        self.dict = [{'InstrIdx': -1, 'RegVal': None, 'opCode': -1}]*self.latency

    def shiftAndEval(self, index= -1, opCode= -1, op1=None, op2=None):
        '''
        Note: If the RS is full, issue a NOP (so that the output value is got)
              by passing the default values to shiftAndEval()
        '''
        out = self.dict[-1]
        self.dict[1:] = self.dict[0:-1]     # shift (pipelined exec)
        if (opCode == -1):      # NOP bubble
            regval = None
        else:
            if (self.type == "add"):
                if opCode:
                    regval = op1 + op2
                else:
                    regval = op1 - op2
            elif (self.type == "mult"):
                if opCode:
                    regval = op1*op2
                else:
                    regval = op1/op2
            else:       # mem operation
                if opCode:
                    #regval = implement load operation here
                    regval = 0      # remove this
                else:
                    regval = None
                    # implement store operation here
        self.dict[0] = {'InstrIdx': index, 'RegVal': regval, 'opCode': opCode}
        return out
