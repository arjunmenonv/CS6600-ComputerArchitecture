from collections import namedtuple
from memory import mem

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
            temp = fuEntry(-1, None, -1)
            self.stages.extend([temp])

    def shiftAndEval(self, index= -1, opCode= -1, op1=None, op2=None):
        '''
            Note: If the RS is full, issue a NOP (so that the output value is got)
                  by passing the default values to shiftAndEval()
        '''
        out = self.stages[-1]
        self.stages[1:] = self.stages[0:-1]     # shift (pipelined exec)
        if (opCode == -1):                      # NOP bubble
            regval = None
        else:
            if opCode == 'ADD':
                regval = op1 + op2
            elif opCode == 'SUB':
                regval = op1 - op2
            else:
                index = -1
                regval = None
                opCode = -1
        self.stages[0] = fuEntry(index, regval, opCode)
        return out

class MDU:
    '''
        Mult/Div Functional Unit
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
            temp = fuEntry(-1, None, -1)
            self.stages.extend([temp])

    def shiftAndEval(self, index= -1, opCode= -1, op1=None, op2=None):
        '''
            Note: If the RS is full, issue a NOP (so that the output value is got)
                  by passing the default values to shiftAndEval()
        '''
        out = self.stages[-1]
        self.stages[1:] = self.stages[0:-1]     # shift (pipelined exec)
        if (opCode == -1):      # NOP bubble
            regval = None
        else:
            if opCode == 'MUL':
                regval = op1*op2
            elif opCode == 'DIV':
                regval = op1/op2
            else:
                index = -1
                regval = None
                opCode = -1
        self.stages[0] = fuEntry(index, regval, opCode)
        return out

class LSU:
    '''
        Load/Store Functional Unit
        Execution is pipelined with 1 instr fed in each cycle
        latency of FU is as mentioned in config.py
    '''
    def __init__(self, latency):
        self.latency = latency
        '''
        InstrIdx => Reorder Buffer index, RegVal => value to be written to RenameReg & forwarded
        opCode: 1 => load, 0 => store
        '''
        self.dict = [{'InstrIdx': -1, 'RegVal': None, 'opCode': -1}]*self.latency

    def shiftAndEval(self, index= -1, opCode= -1, op1=None, op2=None, offset= None):
        '''
        Note: If the RS is full, issue a NOP (so that the output value is got)
              by passing the default values to shiftAndEval()
        '''
        out = self.dict[-1]
        self.dict[1:] = self.dict[0:-1]     # shift (pipelined exec)
        if (opCode == -1):      # NOP bubble
            regval = None
        else:
            if opCode:
                addr = (op1 + op2)%len(mem)
                regval = mem[addr]
            else:
                regval = None
                addr = (op2 + offset)%len(mem)
                mem[addr] = op1
                # Implement Store Operation here
        self.dict[0] = {'InstrIdx': index, 'RegVal': regval, 'opCode': opCode}
        return out
