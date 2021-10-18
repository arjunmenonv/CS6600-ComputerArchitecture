from collections import namedtuple
from memory import mem, exceptions

fuEntry = namedtuple('fuEntry', 'instrId, regVal, opCode')

class ASU:
    '''
        Add/Sub Functional Unit
        Execution is pipelined with 1 instr fed in each cycle
        latency of FU is as mentioned in config.py
    '''
    def __init__(self, latency):
        self.latency = latency
        '''
            InstrIdx => Reorder Buffer index, RegVal => value to be written to RenameReg & forwarded
            opCode: 1 => add, 0 => sub
        '''
        self.stages = []
        for _ in range(self.latency):
            temp = fuEntry(None, None, None)
            self.stages.extend([temp])

    def shiftAndEval(self, index= None, opCode= None, op1=None, op2=None):
        '''
            Note: If the RS is full, issue a NOP (so that the output value is got)
                  by passing the default values to shiftAndEval()
        '''
        #out = self.stages[-1]
        self.stages[1:] = self.stages[0:-1]     # shift (pipelined exec)
        if (opCode == None):                      # NOP bubble
            regval = None
        else:
            if opCode == 'ADD':
                regval = op1 + op2
            elif opCode == 'SUB':
                regval = op1 - op2
            else:
                index = None
                regval = None
        self.stages[0] = fuEntry(index, regval, opCode)
        out = self.stages[-1]
        return out

class MU:
    '''
        Mult Functional Unit
        Execution is pipelined with 1 instr fed in each cycle
        latency of FU is as mentioned in config.py
    '''
    def __init__(self, latency):
        self.latency = latency
        '''
            InstrIdx => Reorder Buffer index, RegVal => value to be written to RenameReg & forwarded
            opCode: 1 => add, 0 => sub
        '''
        self.stages = []
        for _ in range(self.latency):
            temp = fuEntry(None, None, None)
            self.stages.extend([temp])

    def shiftAndEval(self, index= None, opCode= None, op1=None, op2=None):
        '''
            Note: If the RS is full, issue a NOP (so that the output value is got)
                  by passing the default values to shiftAndEval()
        '''
        #out = self.stages[-1]
        self.stages[1:] = self.stages[0:-1]     # shift (pipelined exec)
        if (opCode == None):                      # NOP bubble
            regval = None
        else:
            if opCode == 'MUL':
                regval = op1 * op2
            else:
                index = None
                regval = None
        self.stages[0] = fuEntry(index, regval, opCode)
        out = self.stages[-1]
        return out

class DU:
    '''
        Div Functional Unit
        Execution is pipelined with 1 instr fed in each cycle
        latency of FU is as mentioned in config.py
    '''
    def __init__(self, latency):
        self.latency = latency
        '''
            InstrIdx => Reorder Buffer index, RegVal => value to be written to RenameReg & forwarded
            opCode: 1 => add, 0 => sub
        '''
        self.stages = []
        for _ in range(self.latency):
            temp = fuEntry(None, None, None)
            self.stages.extend([temp])

    def shiftAndEval(self, index= None, opCode= None, op1=None, op2=None):
        '''
            Note: If the RS is full, issue a NOP (so that the output value is got)
                  by passing the default values to shiftAndEval()
        '''
        #out = self.stages[-1]
        self.stages[1:] = self.stages[0:-1]     # shift (pipelined exec)
        if (opCode == None):                      # NOP bubble
            regval = None
        else:
            if opCode == 'DIV':
                if op2 != 0:
                    regval = int(op1/op2)
                else:
                    regval = int(2e32 - 1)
                    err_string = "\n[DIV, {}, {}]\nEXCEPTION: Divide by 0 exception! \
                    \nFunctional correctness may be affected by this exception.".format(op1, op2)
                    print(err_string)
                    exceptions.append(err_string)
            else:
                index = None
                regval = None
        self.stages[0] = fuEntry(index, regval, opCode)
        out = self.stages[-1]
        return out

class LSU:
    '''
        Load/Store Functional Unit
        Unlike othger FUs, the LSU is not pipelined
    '''
    def __init__(self, latency):
        self.latency = latency
        self.dict = {'InstrIdx': None, 'RegVal': None, 'opCode': None, 'busy': 0}
        self.end = None

    def IssueNewOp(self, start, index= None, opCode= None, op1=None, op2=None, offset= None):
        '''
            Check if FU is busy before calling this Function
            Redundant "if(busy)" added
        '''
        if (self.dict['busy']):
            return 1       # busy, try again in next cycle
        else:
            if (opCode == None):      # NOP bubble
                regval = None
                busy = 0
            else:
                busy = 1
                self.end = start + self.latency - 1     # including current cycle
                if opCode == 'LOD':
                    addr = (op2 + offset)%len(mem)
                    regval = mem[addr]
                elif opCode == 'STO':
                    regval = None
                    addr = (op2 + offset)%len(mem)
                    mem[addr] = op1
                else:
                    regval = None
                    index = None
                    busy = 0
            self.dict = {'InstrIdx': index, 'RegVal': regval, 'opCode': opCode, 'busy': busy}
            return 0

    def pollLSU(self, clkVal):
        if(self.dict['busy']):
            if(clkVal == self.end):
                self.dict['busy'] = 0
                return self.dict
        return {'InstrIdx': None, 'RegVal': None, 'opCode': None, 'busy': 0}
